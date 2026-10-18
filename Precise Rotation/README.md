# Precise Rotation

Version 1.3.0 - Author: Vittorio

Enable this world mod and restart Sapiens after installing an update.
No dependencies are required. Hammerstone adds an optional information page.

## Controls

| Default keys | Rotation step |
| --- | --- |
| X / Y / Z | 90 degrees |
| Left Alt + X / Y / Z | 45 degrees |
| Left Ctrl + X / Y / Z | 5 degrees |

All nine actions appear in the building group under Settings > Controls.
Bindings use the game's normal save/reset behavior. Existing custom bindings
remain valid. The game's modifier handling may also accept right modifiers.
Release Alt/Ctrl before confirming placement: their existing placement functions
remain active. Normal X/Z restrictions and mouse rotation controls still apply.

## Rotation display

The small Key rotation panel shows keyboard input totals for the current preview.
Each axis wraps at 360 degrees and resets when a new preview opens. Its visibility
follows the building panel. Mouse rotation, copied orientation and automatic
snapping are not included. These totals are not world angles or Euler angles;
rotations around different axes depend on their order.

## Optional information page

With Hammerstone enabled, open Mod Options > Precise Rotation. The page uses
Hammerstone's supported read-only group headings and needs no custom UI hooks.
The stable configKey rotation45 is retained for compatibility.

## Implementation

- scripts/preciseRotation/bindings.lua defines axes, steps and stable binding IDs.
- scripts/mainThread/keyMapping.lua registers only the six additional bindings.
- scripts/common/locale.lua supplies nine English labels; other keys delegate.
- scripts/mainThread/ui/buildModeInteractUI.lua adapts the game's placement state.
- scripts/preciseRotation/readout.lua owns the display and per-preview counters.

The adapter resolves explicitly named direct Lua upvalues because the game has no
public rotation setter. It validates all callbacks before modifying the key map.
Missing functions, missing bindings, unexpected types, unavailable debug access,
and occupied custom callbacks cause installation to stop with a diagnostic and
leave the original placement controls intact. Rotation state is read at each key
press, never cached across mode changes. The original 90-degree callback is used
for accepted input. The added steps update the same game state as that callback.
Hook guards prevent duplicate wrapping. UI counters are local and never saved.

Stable identifiers rotateX45/rotateY45/rotateZ45 and rotateX5/rotateY5/rotateZ5,
rotation45Installed and the Hammerstone configKey intentionally retain old names.
Changing them would risk settings migration or duplicate installation.

## Security and compatibility

The runtime code performs no network requests, file writes, shell calls or
execution of externally supplied code. Its privileged surface is Lua debug
upvalue access to the placement callbacks. Access is limited to fixed names;
there is no recursive closure traversal or user-controlled target selection.
This review found no exploitable vulnerability in this mod's inspected runtime
code. It is not a security audit of Sapiens, Steam or other installed mods.

Other mods replacing the same callbacks or wrapping UI initialization can still
be incompatible. Terrain Building Anchor enforces its own alignment. Disabling
Precise Rotation restores normal controls after reload; placed objects retain
their saved orientation. Snapping and walkability follow the game's normal rules.

## Verification and packaging

The development test at ../rotation45-tests/verify.py loads the installed game's
key mapper and original rotation callbacks, with renderer/math test doubles.
It covers all axes and steps, both placement modes, wraparound, reset, ignored
input, invalid constructables, rebinding, duplicate hooks, and atomic failure on
missing APIs or conflicting callbacks. It does not verify native rendering,
physical geometry, snapping or walkability in a live world.

The Workshop preview is preview-steam.jpg (480 x 480, below 1 MB).
WORKSHOP_DESCRIPTION.txt contains the short description. The preview is generated
promotional artwork. Upload through the existing Workshop item; its local
workshop.mjl must be preserved. The unused earlier preview is excluded.
