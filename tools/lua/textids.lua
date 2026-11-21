-- Text coverage probe: log each distinct string id the game opens, for $SKILL/scripts/textcover.py.
--   emu.py ROM --script tools/lua/textids.lua ...   (or warp_all.py ... -- --script tools/lua/textids.lua)
-- The three readers asm/main.asm hooks (TextPtr C1:7270 dialogue, NamePtr C1:74F1 {name}, MenuPtr C1:754D
-- renderer 2) each enter with X = string id * 2 (the original's word index; the hooks double it for the 4-byte
-- PTRS). The dialogue reader is entered once per glyph ($1416 = id, $142C = word index), hence `seen`.
-- Logged as "TEXT <hex id>"; build.py writes build/strings.tsv listing every id as "id<TAB>id".
local seen = {}
local function at(addr)
  L.on_exec(addr, addr, function()
    local x = (emu.getState()["cpu.x"] & 0xFFFF) >> 1
    if seen[x] then return end
    seen[x] = true
    L.log(string.format("TEXT %X f%d", x, L.frame))
  end)
end
at(0xC17270)
at(0xC174F1)
at(0xC1754D)
