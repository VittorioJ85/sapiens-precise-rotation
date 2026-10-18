-- Hammerstone discovers this optional information page automatically.
-- Empty groups are read-only headings supported by its stock options UI.
local lines = {
    "Precise Rotation 1.3.0 - by Vittorio",
    "Key rotation: totals since opening the preview",
    "X / Y / Z: rotate 90 degrees",
    "Left Alt + X / Y / Z: rotate 45 degrees",
    "Left Ctrl + X / Y / Z: rotate 5 degrees",
    "Rebind each action in Settings > Controls.",
    "Release Alt / Ctrl before confirming placement.",
    "Normal X/Z restrictions and mouse controls apply.",
}
local options = {}
for i, line in ipairs(lines) do
    options["info" .. i] = {type="group", label=line, order=i, options={}}
end
return {configKey="rotation45", display_name="Precise Rotation", options=options}
