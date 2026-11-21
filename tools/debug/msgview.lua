-- Message viewer: show any list of string ids in the dialogue box, from a cold boot, with no playthrough.
--   emu.py ROM --out DIR --route <newgame + A mash> --script tools/debug/msgview.lua --var "IDS='2A7,0B9,451'"
-- (tools/debug/msgview.py writes the route and splits long lists over runs.)
-- The new-game opening shows ~25 messages in a row through the dialogue reader C1:7270 (entered once per glyph
-- with X = id*2, $1416 = id, $142C = word index; docs/re/text.md). At each message's first glyph this swaps the
-- next id of IDS in: $1416 and X both, so every later glyph of that message reads the new string. The event goes on
-- as if its own text had shown, so the next message slot takes the next id.
-- Logs "SHOW <id> f<frame>" per swapped message and "SHOT <id> <page> <file>" per page (a shot once the reader has
-- been idle PAUSE frames, i.e. the page is drawn and waits for A); "VIEW_DONE" after the last id's last page,
-- "VIEW_STALL" when no message started for STALL frames (the opening ran out: re-run the rest).
local MEM = emu.memType.snesMemory
local PAUSE, STALL = PAUSE or 24, STALL or 4000
local queue = {}
for h in string.gmatch(IDS or "", "%x+") do queue[#queue + 1] = tonumber(h, 16) end
assert(#queue > 0, "IDS is empty")
local cur, page, last, shot_at, started = nil, 0, nil, nil, nil

L.on_exec(0xC17270, 0xC17270, L.safe(function()
  local idx = emu.read16(0x7E142C, MEM)
  local msg = emu.read16(0x7E1416, MEM)
  if idx == 0 and msg ~= cur then
    if #queue == 0 then L.log("VIEW_DONE f" .. L.frame); L.finish(0); return end
    cur = table.remove(queue, 1)
    page = 0
    emu.write16(0x7E1416, cur, MEM)
    L.log(string.format("SHOW %X f%d", cur, L.frame))
  end
  if cur and msg ~= cur then emu.write16(0x7E1416, cur, MEM) end
  if cur then
    local s = emu.getState()
    if (s["cpu.x"] & 0xFFFF) ~= cur * 2 then s["cpu.x"] = cur * 2; emu.setState(s) end
  end
  last = L.frame
  started = started or L.frame
end))

L.on_frame(function(f)
  if last and f - last == PAUSE and shot_at ~= last then
    shot_at = last
    page = page + 1
    local name = string.format("msg_%03X_%d.png", cur, page)
    L.shot(name)
    L.log(string.format("SHOT %X %d %s", cur, page, name))
  end
  if (last or 0) > 0 and f - last > STALL then L.log("VIEW_STALL f" .. f); L.finish(0) end
end)
