-- Log every renderer-2 call (C1:753B: one menu string -> VRAM): frame, caller (JSL return address), string id
-- ($1416), VRAM word address (A -> $0C), buffer ($00-$02). One line per distinct (caller, id, vram).
--   emu.py ... --script tools/lua/r2log.lua      (docs/re/windows.md, renderer-2 fields)
local mem = emu.memType.snesMemory
local seen = {}
local function rd(a) return emu.read(a, mem) end
L.on_exec(0xC1753B, 0xC1753B, function()
  local s = emu.getState()
  local sp, d = s["cpu.sp"], s["cpu.d"]
  local ret = (rd(0x7E0000 + sp + 3) << 16 | rd(0x7E0000 + sp + 2) << 8 | rd(0x7E0000 + sp + 1)) - 3
  local id = rd(0x7E1416) | rd(0x7E1417) << 8
  local vram = s["cpu.a"] & 0xFFFF
  local key = ret .. ":" .. id .. ":" .. vram
  if seen[key] then return end
  seen[key] = true
  L.log(string.format("r2 f%d caller=%06X id=%03X vram=%04X buf=%02X%02X%02X", L.frame, ret, id, vram,
    rd(d + 2), rd(d + 1), rd(d)))
end)
