-- Log every change of the event interpreter state: command $1244, command-0 step $129E, mode $34/$36,
-- script pointer $12A6 (docs/re/windows.md, C5:99E4 / C5:9C29). Recon helper.
--   emu.py ... --script tools/lua/steplog.lua
local last = ""
L.on_frame(function(f)
  local function w(a) return emu.read(a, emu.memType.snesMemory) | (emu.read(a + 1, emu.memType.snesMemory) << 8) end
  local s = string.format("mode %02X sub %02X cmd %04X step %04X script %04X", w(0x7E0034), w(0x7E0036),
    w(0x7E1244), w(0x7E129E), w(0x7E12A6))
  if s ~= last then L.log(string.format("f%d %s", f, s)); last = s end
end)
