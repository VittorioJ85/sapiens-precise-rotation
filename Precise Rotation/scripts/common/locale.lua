-- English labels apply in every game language, as do the mod's descriptions.
local bindings = mjrequire "preciseRotation/bindings"
local mod = { loadOrder = 20 }
function mod:onload(locale)
    if locale.preciseRotationInstalled then return end
    local labels = {}
    for _, axis in ipairs(bindings.axes) do
        for _, step in ipairs(bindings.steps) do
            labels["key_building_" .. bindings.name(axis, step)] = bindings.label(axis, step)
        end
    end
    local originalGet, originalHas = locale.get, locale.hasLocalization
    function locale:get(key, ...)
        if labels[key] then return labels[key] end
        return originalGet(self, key, ...)
    end
    function locale:hasLocalization(key)
        return labels[key] ~= nil or originalHas(self, key)
    end
    locale.preciseRotationInstalled = true
end
return mod
