-- God mode for battles (phase 2 debug tool): pin the HP of our side's units so mash routes survive fights.
--   emu.py ... --script tools/lua/god.lua [--var GOD_UNITS=0x16]
-- Battle HP is a word per unit at $7E0B00 + 2*unit (docs/re/save.md). Units below GOD_UNITS (default 0x16; Kagura is
-- 0x0E, the first battle's enemies start at 0x16) keep the highest HP seen in the current battle.
local MEM = emu.memType.snesMemory
local function rdw(a) return emu.read(a, MEM) | (emu.read(a + 1, MEM) << 8) end
local function wrw(a, v) emu.write(a, v & 0xFF, MEM); emu.write(a + 1, v >> 8, MEM) end
local units = GOD_UNITS or 0x16
local best, pinned = {}, 0
L.on_frame(function()
  if rdw(0x7E0034) ~= 7 then best = {}; return end
  for u = 0, units - 1 do
    local a = 0x7E0B00 + 2 * u
    local hp = rdw(a)
    if hp > (best[u] or 0) and hp < 1000 then best[u] = hp
    elseif best[u] and hp < best[u] then wrw(a, best[u]); pinned = pinned + 1
      if pinned <= 5 then L.log(string.format("god: unit %02X hp %d -> %d", u, hp, best[u])) end
    end
  end
end)
