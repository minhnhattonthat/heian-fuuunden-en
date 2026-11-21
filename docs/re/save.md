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
| 240-26F | bytes | event flags (`C0:78F5` writes FF; 248 set after the first town talk) | guess |
| 4B0 | 2 | changed 1 -> 3 in the first town | unknown |

## Main mode `$34` (jump table `C0:833F`; sub-state `$36`)
0 logo · 1 title · 2 (`C0:8B34`) · 3 title menu (sub 3 = New/Continue, 5 = slot select) · 4 overworld with place-name
labels (`C0:CBA4`, sub table `C0:CBAB`; sub 0x19 = `C0:D4AD` starts a battle: enemy group `C1:501D` -> `$12AC`) ·
5 field · 6 field menu · 7 battle (`C0:623A`; G6 buttons loaded at `C0:62CA`) · 8 (`C0:C78F`, after a lost battle?) ·
9 ending (`JSL CB:D8FA`; entered when `$0A00 == 0x33` after message 0x221 "enemy squad wiped out") ·
0A prologue (furigana text, G8) · 0C/0D dialogue (`C0:D7A7`) · 0E yes/no prompt.
Soft reset: L+R+Start+Select (`$76 == 0x3030`, `C0:8330`). `$0A00` = current event / battle id.

## Not reached yet
- **Battle**: a bare `$34=7` poke shows a save prompt and hangs; `$34=4,$36=0x19` from the field goes to sub 0x1A
  and stalls. Next: reach the overworld for real (find an exit position on map 02 and put it in the slot), then
  poke `$36=0x19` there; or trace `C1:501D` for the encounter table.
- Game over (mode 8?), shikigami name entry (G7?), overworld place labels, T4 (おつかれさまでした after save+quit).
