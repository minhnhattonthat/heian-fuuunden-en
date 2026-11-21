-- Cold-boot warp for Heian Fuuunden (docs/re/save.md; scene list tools/debug/scenes.tsv).
--   emu.py ROM --out DIR --script tools/debug/warp.lua --var "SCENE='palace'" --frames 3000 --sheet
-- Flow: title -> New Game, slot 1 (the game writes slot 1 at once) -> write the scene's slot edits and fix the
-- checksum -> soft reset (L+R+Start+Select) -> title -> Continue, slot 1 -> field ($34 == 5) -> scene RAM pokes
-- and route -> hold -> shot "warp_<scene>.png", log "WARP_OK <scene>", optional WARP_STATE savestate.
-- God mode is a separate probe: add `--script tools/lua/god.lua` (pins our side's battle HP).
-- Opt-in globals: SCENES_TSV (path; default ../debug/scenes.tsv,
-- relative to tools/mesen, the emulator's working folder), WARP_STATE (absolute path), SHOTS_AFTER (extra shot
-- every N frames after arrival), DUMP_PPU (1: also dump VRAM/CGRAM/OAM as ppu_<scene>.* with the shot).
local MEM = emu.memType.snesMemory
local function rd(a) return emu.read(a, MEM) end
local function rdw(a) return rd(a) | (rd(a + 1) << 8) end
local function wr(a, v) emu.write(a, v, MEM) end

local SLOT1, SUMS = 0x306600, 0x3065FA -- slot n at SLOT1 + (n-1)*0x8A0; checksum word at SUMS + (n-1)*2
local function fix_checksum()
  local sum = 0
  for a = SLOT1 + 0x30, SLOT1 + 0x89F do
    local v = rd(a)
    while v > 0 do sum = sum + (v & 1); v = v >> 1 end
  end
  wr(SUMS, sum & 0xFF); wr(SUMS + 1, (sum >> 8) & 0xFF)
  return sum & 0xFFFF
end

-- scenes.tsv: name, slot (live-state offset=byte list), ram (addr=byte list), route ("N buttons;..."), hold, notes
local scene
do
  local path
  for _, p in ipairs({ SCENES_TSV or "", "../debug/scenes.tsv", "tools/debug/scenes.tsv",
                       OUT .. "../../../tools/debug/scenes.tsv", OUT .. "../../tools/debug/scenes.tsv" }) do
    local fh = p ~= "" and io.open(p, "r")
    if fh then fh:close(); path = p; break end
  end
  assert(path, "scenes.tsv not found: pass --var \"SCENES_TSV=[[C:/abs/tools/debug/scenes.tsv]]\"")
  for line in io.lines(path) do
    if not line:match("^#") and line ~= "" then
      local c = {}
      for field in (line .. "\t"):gmatch("([^\t]*)\t") do c[#c + 1] = field end
      if c[1] == SCENE then scene = { name = c[1], slot = c[2], ram = c[3], route = c[4], hold = tonumber(c[5]) or 120 } end
    end
  end
  assert(scene, "scene not in " .. path .. ": " .. tostring(SCENE))
end

local function pokes(spec, base)
  for a, v in (spec or ""):gmatch("(%x+)=(%x+)") do
    local addr = base + tonumber(a, 16)
    -- a value longer than 2 hex digits is written little-endian, byte by byte
    for i = 0, (#v // 2) - 1 do wr(addr + i, tonumber(v:sub(#v - 2 * i - 1, #v - 2 * i), 16)) end
  end
end

ARRIVE_MODE = ARRIVE_MODE or 5 -- $34: 0 logo, 1 title, 3 title menu, 5 field, 7 battle?, 9 ending, 0A prologue
local stage, busy, ready_at, arrived, field_frames, steps, waited = "new", 0, nil, nil, 0, {}, 0
L.on_write(SUMS, SUMS, function()
  if stage == "new" and not ready_at then ready_at = L.frame + 20 end
end)

local function press(spec, gap)
  L.press(spec, 6); L.press("-", gap or 40); busy = L.frame + 6 + (gap or 40)
end

L.on_frame(function(f)
  if f < busy then return end
  local mode, sub = rdw(0x7E0034), rdw(0x7E0036)
  if DEBUG and f % 30 == 0 then L.log(string.format("f%d %s mode %02X sub %02X", f, stage, mode, sub)) end
  if stage == "new" or stage == "cont" then
    if ready_at and stage == "new" then
      if f >= ready_at then
        pokes(scene.slot, SLOT1 + 0x30)
        L.log(string.format("slot 1 edited for %s, checksum %04X", scene.name, fix_checksum()))
        stage = "cont"; press("l+r+start+select", 60)
      end
      return
    end
    if mode == 1 then press("start", 40)
    elseif mode == 3 and sub == 3 then -- New Game / Continue
      if stage == "cont" then press("down", 30) end
      L.press("a", 6); L.press("-", 60); busy = busy + 66
    elseif mode == 3 and sub == 5 then press("a", 60) -- slot 1
    elseif mode == 3 and sub == 4 then -- scroll opening: if it sits here, the A was eaten (timing); press again
      waited = waited + 1
      if waited >= 120 then waited = 0; press("a", 60) end
    elseif mode == ARRIVE_MODE and stage == "cont" then
      field_frames = field_frames + 1
      if field_frames >= 90 then
        stage = "arrived"; arrived = f; waited = 0
        pokes(scene.ram, 0)
        for step in (scene.route or ""):gmatch("[^;]+") do steps[#steps + 1] = step:match("^%s*(.-)%s*$") end
        L.log(string.format("arrived f%d map %02X x %04X y %04X", f, rd(0x306132 + rd(0x306001) - 1),
          rdw(0x306138 + 2 * (rd(0x306001) - 1)), rdw(0x306144 + 2 * (rd(0x306001) - 1))))
      end
    end
  elseif stage == "arrived" then
    -- route steps: "N buttons" (hold for N frames), "wait MM" / "wait MM.SS" / "wait MM.SS.TT" (until $34 == MM
    -- [and $36 == SS [and $38 == TT]], hex; gives up after 3000 frames, logging "wait timed out"), "poke ADDR=VAL,..." (CPU addresses, as in the ram column),
    -- "mash N" (press A every 30 frames for N frames), "tap BUTTON until MM[.SS]" (press every 40 frames until the mode matches)
    if not L.route_done() then return end
    local step = steps[1]
    if not step then stage = "hold"; arrived = f; return end
    local n, b = step:match("^(%d+)%s+(%S+)$")
    local wm, ws, wt = step:match("^wait%s+(%x+)%.?(%x*)%.?(%x*)$")
    local tb, tm, ts = step:match("^tap%s+(%S+)%s+until%s+(%x+)%.?(%x*)$")
    if n then L.press(b, tonumber(n)); table.remove(steps, 1)
    elseif tb then -- "tap BUTTON until MM[.SS]": press every 40 frames until $34 (and $36) match
      waited = waited + 1
      if (mode == tonumber(tm, 16) and (ts == "" or sub == tonumber(ts, 16))) or waited > 3000 then
        if waited > 3000 then L.log("tap timed out: " .. step) end
        waited = 0; table.remove(steps, 1)
      else L.press(tb, 6); L.press("-", 34) end
    elseif wm then
      waited = waited + 1
      if (mode == tonumber(wm, 16) and (ws == "" or sub == tonumber(ws, 16))
          and (wt == "" or rdw(0x7E0038) == tonumber(wt, 16))) or waited > 3000 then
        if waited > 3000 then L.log("wait timed out: " .. step) end
        waited = 0; table.remove(steps, 1)
      end
    elseif step:match("^poke%s") then pokes(step:sub(6), 0); table.remove(steps, 1)
    elseif step:match("^mash%s") then
      for _ = 1, tonumber(step:match("%d+")) // 30 do L.press("a", 6); L.press("-", 24) end
      table.remove(steps, 1)
    else error("bad route step: " .. step) end
  elseif stage == "hold" then
    if SHOTS_AFTER and (f - arrived) % SHOTS_AFTER == 0 then L.shot(string.format("warp_%s_%06d.png", scene.name, f)) end
    if f - arrived >= scene.hold then
      L.shot("warp_" .. scene.name .. ".png")
      if DUMP_PPU then L.dump_ppu("ppu_" .. scene.name) end
      L.log(string.format("WARP_OK %s f%d mode %02X sub %02X", scene.name, f, mode, sub))
      stage = "done"
      if WARP_STATE then L.save_state(WARP_STATE, function() L.finish(0) end) else L.finish(0) end
    end
  end
end)
