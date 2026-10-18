-- Precise Rotation by Vittorio. Adapter for Sapiens' private placement callbacks.
local mjm = mjrequire "common/mjm"
local keyMapping = mjrequire "mainThread/keyMapping"
local constructable = mjrequire "common/constructable"
local bindings = mjrequire "preciseRotation/bindings"
local readout = mjrequire "preciseRotation/readout"
local mod = { loadOrder = 20 }

-- Access only explicitly named direct upvalues; never traverse arbitrary closures.
-- The debug API is required because Sapiens does not expose placement setters.
local function slot(fn, wanted, expectedType)
    assert(type(fn) == "function", "Missing function for " .. wanted)
    assert(debug and debug.getupvalue and debug.setupvalue, "Lua upvalue API unavailable")
    local index = 1
    while true do
        local name, value = debug.getupvalue(fn, index)
        if not name then break end
        if name == wanted then
            assert(not expectedType or type(value) == expectedType, "Invalid upvalue type: " .. wanted)
            local position = index
            return {
                get = function()
                    local _, current = debug.getupvalue(fn, position)
                    return current
                end,
                set = function(newValue)
                    assert(debug.setupvalue(fn, position, newValue) == wanted)
                end,
            }
        end
        index = index + 1
    end
    error("Missing upvalue: " .. wanted)
end

local function resolveAxis(original, index)
    return {
        original = original,
        finalMode = slot(original, "finalPositionMode", "boolean"),
        rotation = slot(original, "buildObjectRotation"),
        extra = slot(original, "objectExtraRotationDueToKeysOrDupe"),
        updateControls = slot(original, "updateFinalControls", "function").get(),
        typeIndex = index ~= 2 and slot(original, "constructableTypeIndex") or nil,
        vector = mjm.vec3(index == 1 and 1 or 0, index == 2 and 1 or 0, index == 3 and 1 or 0),
    }
end

local function makeCallback(state, index, step, display)
    return function(isDown, isRepeat)
        if not isDown or isRepeat then return end
        if state.typeIndex then
            local info = constructable.types[state.typeIndex.get()]
            if not info or not info.allowXZRotation then return end
        end
        local result
        if not step.modifier then
            -- Preserve the game's 90-degree implementation and return value.
            result = state.original(isDown, isRepeat)
        else
            local finalMode = state.finalMode.get()
            local target = finalMode and state.rotation or state.extra
            target.set(mjm.mat3Rotate(target.get(), math.rad(step.degrees), state.vector))
            if finalMode then state.updateControls() end
        end
        display:record(index, step.degrees)
        return result
    end
end

function mod:onload(ui)
    -- Keep the existing marker name for compatibility with earlier releases.
    if ui.rotation45Installed then return end
    local display = readout.new()
    -- Prepare all nine callbacks before any mutation. A missing/changed private
    -- game API or an occupied custom mapping must not leave a partial install.
    local ok, result = pcall(function()
        assert(type(ui.show) == "function", "Missing show callback")
        local keyChanged = slot(ui.init, "keyChanged", "function").get()
        local topView = slot(keyChanged, "topView") -- nil until init runs
        local keyMap = slot(keyChanged, "keyMap", "table").get()
        local callbacks = {}
        for index, axis in ipairs(bindings.axes) do
            local originalIndex = keyMapping:getMappingIndex("building", "rotate" .. axis)
            local state = resolveAxis(keyMap[originalIndex], index)
            for _, step in ipairs(bindings.steps) do
                local name = bindings.name(axis, step)
                local mapping = keyMapping:getMappingIndex("building", name)
                assert(type(mapping) == "number" and not callbacks[mapping], "Invalid or duplicate mapping: " .. name)
                assert(not step.modifier or keyMap[mapping] == nil, "Custom mapping already in use: " .. name)
                callbacks[mapping] = makeCallback(state, index, step, display)
            end
        end
        return {keyMap=keyMap, callbacks=callbacks, topView=topView}
    end)
    if not ok then
        mj:log("Precise Rotation: incompatible placement UI; controls unchanged: ", result)
        return
    end
    local originalInit, originalShow = ui.init, ui.show
    for mapping, callback in pairs(result.callbacks) do result.keyMap[mapping] = callback end
    function ui:init(...)
        originalInit(self, ...)
        -- Parent visibility handles hiding when placement ends.
        display:attach(result.topView.get())
    end
    function ui:show(...)
        originalShow(self, ...)
        display:reset()
    end
    ui.rotation45Installed = true
    mj:log("Precise Rotation: rotation controls and readout installed")
end

return mod
