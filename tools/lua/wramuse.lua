-- Which low-WRAM bytes ($7E:0000-1FFF, both mirrors) does the game ever write? For finding free RAM for hooks.
--   emu.py ROM ... --script tools/lua/wramuse.lua   (add it next to warp.lua through warp_all.py's extra args)
-- Writes <out>/wramuse.bin every 60 frames: 8192 bytes, 1 = written with a non-zero value at least once since boot
-- (the boot and mode-change clears write zeros everywhere).
local used = {}
for i = 0, 0x1FFF do used[i] = 0 end
L.on_write(0x7E0000, 0x7E1FFF, function(addr, value) if value ~= 0 then used[addr & 0x1FFF] = 1 end end)
L.on_frame(function(f)
  if f % 60 ~= 0 then return end
  local t = {}
  for i = 0, 0x1FFF do t[#t + 1] = string.char(used[i]) end
  L.write_file("wramuse.bin", table.concat(t))
end)
