-- One definition for registration, labels and rotation callbacks.
-- Keep mapping names stable: Sapiens persists custom bindings under these keys.
local bindings = {
    axes = {"X", "Y", "Z"},
    steps = {
        {degrees=90},
        {degrees=45, modifier="alt"},
        {degrees=5, modifier="ctrl"},
    },
}

function bindings.name(axis, step)
    return "rotate" .. axis .. (step.modifier and tostring(step.degrees) or "")
end

function bindings.label(axis, step)
    return string.format("Rotate %s axis (%d degrees)", axis, step.degrees)
end

return bindings
