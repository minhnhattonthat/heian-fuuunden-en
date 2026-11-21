-- ROM read histogram: count reads per (PC, 256-byte page of the read) between frames FROM..TO,
-- then log the table at TO. Finds data streams (font, script) read by one loop many times.
--   emu.py ... --script tools/lua/readhist.lua --var FROM=3700 --var TO=3900
local from, to = FROM or 0, TO or 600
local counts, first = {}, {}
local function hook(addr, value)
  local f = L.frame
  if f < from or f > to then return end
  local s = emu.getState()
  local pc = (s["cpu.k"] << 16) | s["cpu.pc"]
  local key = string.format("%06X %06X", pc, addr & 0xFFFF00)
  counts[key] = (counts[key] or 0) + 1
  if not first[key] then first[key] = string.format("%06X", addr) end
end
L.on_read(0xC00000, 0xFFFFFF, hook)
L.on_read(0x400000, 0x7DFFFF, hook)
L.on_frame(function(f)
  if f == to then
    for k, n in pairs(counts) do L.log(string.format("hist %s n=%d first=%s", k, n, first[k])) end
  end
end)
