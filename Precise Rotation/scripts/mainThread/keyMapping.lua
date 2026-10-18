-- Native bindings appear in Settings > Controls and use normal persistence.
local bindings = mjrequire "preciseRotation/bindings"
local mod = { loadOrder = 20 }
function mod:onload(keyMapping)
    if keyMapping.preciseRotationInstalled then return end
    local originalInit = keyMapping.mjInit
    function keyMapping:mjInit(...)
        originalInit(self, ...)
        for _, axis in ipairs(bindings.axes) do
            for _, step in ipairs(bindings.steps) do
                local name = bindings.name(axis, step)
                if step.modifier and not self.mappingGroups.building.mappingsByKey[name] then
                    self.addMapping("building", name, self.keyCodes[string.lower(axis)],
                        self.modifiers[step.modifier])
                end
            end
        end
    end
    keyMapping.preciseRotationInstalled = true
end
return mod
