-- Log every call of the graphics decompressor C1:05CF: frame, caller-independent source ($00-$02 on the direct
-- page) and destination ($04-$06), type byte and output size. One line per distinct (source, dest).
--   emu.py ... --script tools/lua/declog.lua
local mem = emu.memType.snesMemory
local seen = {}
local function rd(a) return emu.read(a, mem) end
L.on_exec(0xC105CF, 0xC105CF, function()
  local s = emu.getState()
  local d = s["cpu.d"]
  local src = rd(d + 2) << 16 | rd(d + 1) << 8 | rd(d)
  local dst = rd(d + 6) << 16 | rd(d + 5) << 8 | rd(d + 4)
  local key = src .. ":" .. dst
  if seen[key] then return end
  seen[key] = true
  L.log(string.format("dec f%d src=%06X dst=%06X type=%d size=%04X", L.frame, src, dst, rd(src),
    rd(src + 2) << 8 | rd(src + 1)))
end)
