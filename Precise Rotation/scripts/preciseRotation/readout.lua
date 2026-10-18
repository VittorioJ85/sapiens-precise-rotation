local mjm = mjrequire "common/mjm"
local uiCommon = mjrequire "mainThread/ui/uiCommon/uiCommon"
local readout = {}

-- Each placement UI owns its own state. These are keyboard input totals, not
-- Euler angles: rotations on different axes do not commute. Never persist them.
function readout.new()
    local totals = {0, 0, 0}
    local panel, text
    local instance = {}
    local function refresh()
        if not text then return end
        text.text = string.format("Key rotation:  X %d°   Y %d°   Z %d°", unpack(totals))
        panel.size = mjm.vec2(text.size.x + 24, 30)
    end
    function instance:attach(parent)
        if panel then return end -- Avoid duplicate views if init is repeated.
        panel = ColorView.new(parent)
        panel.relativePosition = ViewPosition(MJPositionCenter, MJPositionBelow)
        panel.baseOffset = mjm.vec3(0, -6, 1)
        panel.color = mjm.vec4(0.05, 0.05, 0.05, 0.85)
        text = TextView.new(panel)
        text.font = Font(uiCommon.fontName, 16)
        text.relativePosition = ViewPosition(MJPositionCenter, MJPositionCenter)
        text.color = mj.textColor
        refresh()
    end
    function instance:record(axis, degrees)
        totals[axis] = (totals[axis] + degrees) % 360
        refresh()
    end
    function instance:reset()
        totals = {0, 0, 0}
        refresh()
    end
    return instance
end

return readout
