-- Which name ids `{name}` takes in which message: logs "NAME <msg id> <name id> f<frame>" at the {name} reader
-- (C1:74F1, X = name id * 2; $1416 = the message being drawn). One line per distinct pair.
--   emu.py ROM --script tools/debug/warp.lua --var "SCENE='battle_enemy_attack'" --script tools/lua/namelog.lua
local seen = {}
L.on_exec(0xC174F1, 0xC174F1, function()
  local id = (emu.getState()["cpu.x"] & 0xFFFF) >> 1
  local msg = emu.read16(0x7E1416, emu.memType.snesMemory)
  local k = msg * 65536 + id
  if seen[k] then return end
  seen[k] = true
  L.log(string.format("NAME %X %X f%d", msg, id, L.frame))
end)
