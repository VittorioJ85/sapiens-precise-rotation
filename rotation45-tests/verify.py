"""Integration checks with the installed game's key mapper and rotation closures."""
import sys, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from lua_runner import run, GAME as GAME_ROOT
GAME = GAME_ROOT / 'GameResources/scripts'
source = (GAME / 'mainThread/ui/buildModeInteractUI.lua').read_text()
original = source[source.index('local function rotateX('):source.index('local function updateSubtitle(')]
setup = r'''
local root, game = ROOT, GAME
local calls, updates = {}, 0
local function vec3(x,y,z) return {x=x,y=y,z=z} end
local function mat3Rotate(matrix, angle, axis)
    calls[#calls+1] = {angle=angle,axis=axis}
    return matrix + angle
end
local constructable = {types={{allowXZRotation=true},{allowXZRotation=false}}}
local constructableTypeIndex, finalPositionMode = 1, false
local buildObjectRotation, objectExtraRotationDueToKeysOrDupe = 0, 0
local function updateFinalControls() updates = updates + 1 end
local locale = {get=function(self,k) return k end, hasLocalization=function() return false end}
local settings = {values={}}
function settings:changeSetting(k,v) self.values[k]=v end
local keyMapping
local modules = {}
local hudText, hudPanel
ColorView = {new=function(parent) hudPanel={parent=parent}; return hudPanel end}
TextView = {new=function(parent) hudText={parent=parent,size={x=310}}; return hudText end}
function ViewPosition(...) return {...} end
function Font(...) return {...} end
mj = {log=function() end, textColor={}}
function mjrequire(name)
    if name:match("^preciseRotation/") then
        if not modules[name] then modules[name] = dofile(root .. "/scripts/" .. name .. ".lua") end
        return modules[name]
    end
    if name == "common/mjm" then return {vec3=vec3,vec2=vec3,vec4=function(...) return {...} end,mat3Rotate=mat3Rotate} end
    if name == "mainThread/ui/uiCommon/uiCommon" then return {fontName="test"} end
    if name == "common/constructable" then return constructable end
    if name == "mainThread/keyMapping" then return keyMapping end
    if name == "mainThread/clientGameSettings" then return settings end
    if name == "common/locale" then return locale end
    error("Unexpected dependency: " .. name)
end
dofile(root .. "/scripts/common/locale.lua"):onload(locale)
local originalLocaleGet = locale.get
dofile(root .. "/scripts/common/locale.lua"):onload(locale)
assert(locale.get == originalLocaleGet, "locale hook installed twice")
assert(locale:get("unrelated") == "unrelated")
keyMapping = dofile(game .. "/mainThread/keyMapping.lua")
dofile(root .. "/scripts/mainThread/keyMapping.lua"):onload(keyMapping)
local firstMappingInit = keyMapping.mjInit
dofile(root .. "/scripts/mainThread/keyMapping.lua"):onload(keyMapping)
assert(keyMapping.mjInit == firstMappingInit, "key mapper hook installed twice")
keyMapping:mjInit()
local topView = {hidden=false}
local buildModeInteractUI = {show=function() end}
'''
checks = r'''
function buildModeInteractUI:init() return keyChanged end
local old = {}
for _, a in ipairs({"X","Y","Z"}) do old[a] = keyMap[keyMapping:getMappingIndex("building","rotate" .. a)] end
local mod = dofile(root .. "/scripts/mainThread/ui/buildModeInteractUI.lua")
mod:onload(buildModeInteractUI)
assert(buildModeInteractUI.rotation45Installed)
buildModeInteractUI:init()
assert(hudPanel.parent == topView and hudText.parent == hudPanel)
assert(hudText.text == "Key rotation:  X 0°   Y 0°   Z 0°")
local firstPanel = hudPanel
buildModeInteractUI:init()
assert(firstPanel == hudPanel, "duplicate HUD")
local function press(axis, degrees, down, repeated)
    local modifier = degrees == 45 and keyMapping.modifiers.alt or (degrees == 5 and keyMapping.modifiers.ctrl or nil)
    keyChanged(down,keyMapping:getMappingsForInput(keyMapping.keyCodes[axis:lower()],modifier),repeated)
end
for _, final in ipairs({false,true}) do
    finalPositionMode = final
    for index, axis in ipairs({"X","Y","Z"}) do
        for _, degrees in ipairs({90,45,5}) do
            buildObjectRotation, objectExtraRotationDueToKeysOrDupe = 0,0
            local before, count = updates, #calls
            for i=1,360/degrees do
                press(axis,degrees,true,false)
                local call = calls[#calls]
                assert(math.abs(call.angle-math.pi*degrees/180)<1e-12)
                assert(call.axis.x == (index==1 and 1 or 0))
                assert(call.axis.y == (index==2 and 1 or 0))
                assert(call.axis.z == (index==3 and 1 or 0))
            end
            assert(#calls-count == 360/degrees, "multiple actions fired")
            assert(math.abs((final and buildObjectRotation or objectExtraRotationDueToKeysOrDupe)-2*math.pi)<1e-12)
            assert((final and objectExtraRotationDueToKeysOrDupe or buildObjectRotation)==0)
            assert(updates-before == (final and 360/degrees or 0))
        end
    end
end
buildModeInteractUI:show()
press("X",90,true,false)
press("Y",45,true,false)
press("Z",5,true,false)
assert(hudText.text == "Key rotation:  X 90°   Y 45°   Z 5°")
local beforeIgnoredText = hudText.text
local count = #calls
for _, degrees in ipairs({90,45,5}) do
    for _, axis in ipairs({"X","Y","Z"}) do
        press(axis,degrees,false,false)
        press(axis,degrees,true,true)
    end
end
assert(#calls == count, "release/repeat should not rotate")
constructableTypeIndex = 2
for _, degrees in ipairs({90,45,5}) do press("X",degrees,true,false); press("Z",degrees,true,false) end
assert(#calls == count, "X/Z restriction lost")
assert(hudText.text == beforeIgnoredText, "ignored input changed readout")
topView.hidden = true
press("Y",5,true,false)
assert(#calls == count, "hidden UI rotated")
assert(hudText.text == beforeIgnoredText)
topView.hidden = false
constructableTypeIndex = 1
keyMapping:setBinding("building","rotateX5",keyMapping.keyCodes.j,keyMapping.keyCodes.lalt)
keyMapping:loadSettings()
keyChanged(true,keyMapping:getMappingsForInput(keyMapping.keyCodes.j,keyMapping.modifiers.alt),false)
assert(#calls == count+1 and math.abs(calls[#calls].angle-math.pi/36)<1e-12)
keyMapping:resetBinding("building","rotateX5")
press("X",5,true,false)
assert(#calls == count+2)
for _, axis in ipairs({"X","Y","Z"}) do
    for _, degrees in ipairs({90,45,5}) do
        local name = "rotate" .. axis .. (degrees==90 and "" or degrees)
        assert(keyMapping.mappingGroups.building.mappingsByKey[name].name == "Rotate " .. axis .. " axis (" .. degrees .. " degrees)")
    end
end
local first = keyMap[keyMapping:getMappingIndex("building","rotateX45")]
mod:onload(buildModeInteractUI)
assert(first == keyMap[keyMapping:getMappingIndex("building","rotateX45")])
local unsupported = {init=function() end}
mod:onload(unsupported)
assert(not unsupported.rotation45Installed)
local info = dofile(root .. "/hammerstone/options/rotation45.lua")
local infoCount = 0
for _, entry in pairs(info.options) do
    assert(entry.type == "group" and type(entry.options)=="table" and entry.label)
    infoCount = infoCount + 1
end
assert(infoCount == 8 and info.configKey == "rotation45")
buildModeInteractUI:show()
assert(hudText.text == "Key rotation:  X 0°   Y 0°   Z 0°", "new preview did not reset")
for i=1,5 do press("Y",90,true,false) end
assert(hudText.text == "Key rotation:  X 0°   Y 90°   Z 0°")
for _, axis in ipairs({"X","Y","Z"}) do
    for _, step in ipairs({90,45,5}) do
        buildModeInteractUI:show()
        for i=1,360/step do press(axis,step,true,false) end
        assert(hudText.text == "Key rotation:  X 0°   Y 0°   Z 0°", "full turn must wrap to zero")
    end
end
buildModeInteractUI:show()
for i=1,71 do press("X",5,true,false) end
press("X",45,true,false)
assert(hudText.text == "Key rotation:  X 40°   Y 0°   Z 0°", "crossing 360 must preserve remainder")
constructableTypeIndex = nil
local invalidTypeCount = #calls
press("X",90,true,false)
press("Z",45,true,false)
assert(#calls == invalidTypeCount, "invalid constructable must be ignored")
constructableTypeIndex = 1
-- Failure on the last axis must leave ALL callbacks and lifecycle hooks intact.
local function checkFailedInstall(failure)
    local keyMap = {}
    for _, axis in ipairs({"X","Y","Z"}) do keyMap[keyMapping:getMappingIndex("building","rotate"..axis)] = old[axis] end
    local blocker = function() end
    local z5 = keyMapping:getMappingIndex("building","rotateZ5")
    if failure == "collision" then keyMap[z5] = blocker end
    local topView = {}
    local function keyChanged() return keyMap, topView end
    local testUI = {init=function() return keyChanged end, show=function() end}
    local previousInit, previousShow = testUI.init, testUI.show
    local getIndex = keyMapping.getMappingIndex
    if failure == "missing" then
        function keyMapping:getMappingIndex(group, name)
            if name == "rotateZ5" then return nil end
            return getIndex(self,group,name)
        end
    end
    local savedDebug = debug
    if failure == "debug" then debug = nil end
    mod:onload(testUI)
    debug = savedDebug
    keyMapping.getMappingIndex = getIndex
    assert(not testUI.rotation45Installed)
    assert(testUI.init == previousInit and testUI.show == previousShow)
    for _, axis in ipairs({"X","Y","Z"}) do assert(keyMap[keyMapping:getMappingIndex("building","rotate"..axis)] == old[axis]) end
    assert(keyMap[z5] == (failure == "collision" and blocker or nil))
end
checkFailedInstall("collision")
checkFailedInstall("missing")
checkFailedInstall("debug")
print("PASS: native dispatch; 90/45/5 on XYZ in both modes; no duplicate rotations; restrictions; release/repeat; hidden UI; rebinding/save/reset; labels; optional info schema; safe compatibility failure")
'''
run(setup.replace('ROOT',json.dumps((ROOT/'Precise Rotation').as_posix())).replace('GAME',json.dumps(GAME.as_posix())) + original + checks)
