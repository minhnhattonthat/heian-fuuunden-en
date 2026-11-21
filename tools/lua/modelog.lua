-- Log every change of the main mode $34 / sub-state $36 and the battle id $0A00 (recon helper).
--   emu.py ... --script tools/lua/modelog.lua
local last = ""
L.on_frame(function(f)
  local function w(a) return emu.read(a, emu.memType.snesMemory) | (emu.read(a + 1, emu.memType.snesMemory) << 8) end
  local s = string.format("mode %02X sub %02X a00 %04X", w(0x7E0034), w(0x7E0036), w(0x7E0A00))
  if s ~= last then L.log(string.format("f%d %s", f, s)); last = s end
end)
