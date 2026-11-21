-- Write live-state offsets into save slot SLOT (default 1) and fix its checksum (recon helper).
--   emu.py ... --script tools/lua/slotpoke.lua --var "POKES='132=01,138=70'" [--var SLOT=1] [--var POKE_AT=5]
-- Offsets are into the 0x870-byte live state: 000-56F = SRAM $30:6000.., 570-86F = WRAM $0D00.. (docs/re/save.md).
local at, slot = POKE_AT or 5, SLOT or 1
local function rd(a) return emu.read(a, emu.memType.snesMemory) end
local function wr(a, v) emu.write(a, v, emu.memType.snesMemory) end
function SLOT_BASE(n) return 0x306600 + (n - 1) * 0x8A0 end
function SLOT_FIX(n)
  local base, sum = SLOT_BASE(n), 0
  for a = base + 0x30, base + 0x89F do
    local v = rd(a)
    while v > 0 do sum = sum + (v & 1); v = v >> 1 end
  end
  sum = sum & 0xFFFF
  wr(0x3065FA + (n - 1) * 2, sum & 0xFF); wr(0x3065FB + (n - 1) * 2, sum >> 8)
  return sum
end
L.on_frame(function(f)
  if f ~= at or not POKES then return end
  local base = SLOT_BASE(slot)
  local old = rd(0x3065FA + (slot - 1) * 2) | (rd(0x3065FB + (slot - 1) * 2) << 8)
  local check = SLOT_FIX(slot)
  L.log(string.format("slot %d checksum stored %04X computed %04X", slot, old, check))
  for o, v in POKES:gmatch("(%x+)=(%x+)") do wr(base + 0x30 + tonumber(o, 16), tonumber(v, 16)) end
  L.log(string.format("poked; new checksum %04X", SLOT_FIX(slot)))
end)
