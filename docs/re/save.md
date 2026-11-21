# Save data, game modes and the warp (phase 2)

## SRAM (verified)
- 8 KB at `$30:6000`. The **live game state is kept in SRAM itself**: `$30:6000-656F` (0x570 bytes), plus WRAM
  `$0D00-$0FFF` (0x300). Together: the 0x870-byte "live state" that `tools/debug/save.py` offsets refer to.
- Save routine `C5:72E9` (X = slot 1..3): slot base `$30:6600 + (n-1)*0x8A0`; 0x30-byte header copied from
  `C1:7A18` (the "PROGRAM By Tsuyoshi Noh" signature), then the 0x570 SRAM live block, then the 0x300 WRAM block.
- **Checksum**: number of set bits in slot bytes `+0x30..+0x89F`, 16-bit, stored at `$30:65FA + (n-1)*2`. Verified:
  stored = computed on game-written saves (`tools/lua/slotpoke.lua` log), and a `save.py`-edited save loads with
  Continue straight into the edited map (`work/qa/savetest`, frame identical to the warp shot of map 0B).
- Load (`C5:72C0`) copies a slot back; "まえのきろくにもどる" (save menu option 4) and title "つづきから" both use it.
- New Game writes slot 1 at once (~frame 1205 of a cold boot): the warp relies on that.
- The save keeps no field position change: two saves at different spots in one town were byte-identical, so a
  load resumes at the squad's stored position below.

## Live-state fields
| offset | size | meaning | state |
|---|---|---|---|
| 000 | 1 | 08 on every save seen | unknown |
| 001 | 1 | active squad 1..6 (`C0:BA61`, menu "change squad") | verified by code |
| 132 | 6 | map id per squad; valid field maps 01-19 (sweep `work/qa/mapsweep`); 03 = start town | verified |
| 138 | 6 words | x per squad (pixels); new game 0770 | verified by code (`C0:D4B6`) |
| 144 | 6 words | y per squad; new game 0890 | verified by code |
| 150 / 180 / 270 | 6 each | per-squad data copied on squad reset (`C0:795E`) | guess |
| 240-26F | bytes | per-unit status: `C0:78F5` writes FF for each unit down at battle end; 248 set after the first town talk | guess |
| 4B0 | 2 | changed 1 -> 3 in the first town | unknown |

## Main mode `$34` (jump table `C0:833F`; sub-state `$36`, then `$38`/`$3A`)
0 logo · 1 title · 2 (`C0:8B34`) · 3 title menu (sub 3 = New/Continue, 5 = slot select) · 4 overworld (`C0:CBA4`,
sub table `C0:CBAB` indexed by `$36`; `$36=0` from the field draws it at the squad's slot position; **sub 0x16** =
`C0:D4AD` starts a battle: `C1:501D` -> `$12AC` = province, then `$34=7`) · 5 field · 6 field menu (`C0:9F23`; `$38=8`
= Select help panel) · 7 battle (`C0:623A`) · 8 game over (`C0:C78F`: Heian-kyō burns, 終 card G13) ·
9 ending (`JSL CB:D8FA`) · 0A prologue (furigana text, G8) · 0C/0D dialogue (`C0:D7A7`) · 0E yes/no prompt.
Soft reset: L+R+Start+Select (`$76 == 0x3030`, `C0:8330`). `$0A00`: compared with 0x33 at battle end (final battle);
used as scratch elsewhere (it churns on the overworld), so not a reliable event id.

## Battle (mode 7; verified with `tools/lua/log38.lua`)
- Sub 0 = intro, `$38` through `C0:6250`: 01-07 load (G6 at `C0:62CA`), 08 title card (message 0xB9 "<province>の闘い",
  name id `0x1A0 + $12AC` in `$144E`), 0A save prompt きろくしますか?, 0B only when `$14DC == 0x56` (tutorial battle):
  説明を見ますか? -> 0C-0E battle help panel (G7 id 0x21, map `C8:AA6E`), 0F-11 pan over the enemies.
- Sub 1 = turns, `$38` through `C0:6CC9`: 04/05 turn message (<name>のばんです), **06 = waiting for input** for the
  unit whose turn it is (first battle: an AI unit gets 06 then 08 by itself; the player's 06 is the next one), 0C enemy
  attack (map combat, damage digits), 0D after-action, **0F = battle end `C0:7888`**: `$1522 == 1` -> win (message
  0x221, then `$0A00 == 0x33` -> mode 9 ending, else overworld); otherwise per-unit check of `$09F0` -> game over
  (mode 8) when the leader is down, or message 0x225 and the overworld.
- Commands (Y): こうげき, じゅつ, どうぐ (hidden with no items), しきがみ, たいき; X = movement range; A on the unit = move.
- **HP**: word per unit at `$7E0B00 + 2*unit` (Kagura = unit 0x0E, 36 HP on a new game = status screen 体力 36/36;
  first battle's enemies 0x16+). `tools/lua/god.lua` pins it.
- Province = `$12AC`, 0..0x3E, from the overworld rectangles at `CB:D684` (5 x-bands, 5-byte records x, w, y, h,
  province, 0xFF ends; default 2). Poking `$12AC` at the first mode-7 frame changes the title card, not the map.
- The battle map does not follow the slot position or the field map (every forced battle so far is the 紀伊 map).

## Not reached yet
- Story progress / chapters: no chapter cards seen; the campaign is province by province. The flag that records
  conquered provinces (and the squad/party roster per stage) is not mapped. `$30:6240+` gets FF per fallen unit at
  battle end (`C0:78F5`), so it is a unit-status list, not event flags.
- Name entry: none found. All three "kana grid" tilemaps of the phase 1 survey are other screens (help panel,
  prologue, game over).
