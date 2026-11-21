-- Log changes of the battle state words $36/$38/$3A (mode 7 dispatches $38 through C0:6CC9; recon helper).
--   emu.py ... --script tools/lua/log38.lua
local MEM = emu.memType.snesMemory
local function rdw(a) return emu.read(a, MEM) | (emu.read(a + 1, MEM) << 8) end
local last = ""
L.on_frame(function(f)
  local s = string.format("mode %02X sub %02X 38=%02X 3A=%02X", rdw(0x7E0034), rdw(0x7E0036), rdw(0x7E0038), rdw(0x7E003A))
  if s ~= last then L.log(string.format("f%d %s", f, s)); last = s end
end)
