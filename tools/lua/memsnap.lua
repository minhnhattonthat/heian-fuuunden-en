-- Snapshot WRAM ($7E0000-$7FFFFF) and SRAM ($30:6000-$7FFF) at chosen frames, for diffing (recon helper).
--   emu.py ... --script tools/lua/memsnap.lua --var "SNAP='1840,2040'"
-- Writes <out>/wram_<frame>.bin (128 KB) and <out>/sram_<frame>.bin (8 KB).
local MEM = emu.memType.snesMemory
local want = {}
for n in (SNAP or ""):gmatch("%d+") do want[tonumber(n)] = true end
local function dump(path, lo, hi)
  local t = {}
  for a = lo, hi do t[#t + 1] = string.char(emu.read(a, MEM)) end
  local fh = assert(io.open(OUT .. path, "wb")); fh:write(table.concat(t)); fh:close()
end
L.on_frame(function(f)
  if not want[f] then return end
  dump(string.format("wram_%06d.bin", f), 0x7E0000, 0x7FFFFF)
  dump(string.format("sram_%06d.bin", f), 0x306000, 0x307FFF)
  L.log("snap f" .. f)
end)
