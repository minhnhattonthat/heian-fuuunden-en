# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 3. Identity build next (phase 2 debug tool done). Last build: none yet.
- **Done:**
  - Step 0 setup and phase 1 recon (text, compression, graphics survey): see `docs/re/`.
  - Phase 2 (`docs/re/save.md`): SRAM slot layout and checksum, live-state fields, main modes `$34`, battle states
    `$38`, battle HP table, province id. `tools/debug/warp.lua` warps from a cold boot (New Game -> edit slot 1 +
    checksum -> soft reset -> Continue -> scene pokes/route steps `N btn`, `wait MM[.SS[.TT]]` (`$34`/`$36`/`$38`),
    `poke`, `mash N`). `tools/debug/warp_all.py` runs the whole list, **123/123 ok** (default `--frames` now 24000 for the staff roll) (`work/qa/warp/index.tsv`,
    states `work/states/<scene>.mss`): 25 field maps, start town, field menus (T1/T2/T3/T6), save message (T5),
    quit message (T4), Select help panel (G7/T8), prologue (G8), overworld, battle intro card / save prompt / map /
    4 command labels (G6) / spell and shikigami lists / target / move / turn message / enemy attack, tutorial help
    panel (G7/T8), battle win -> overworld, game over (mode 8, 終 G13), the real ending path (win with
    `$0A00=33`) -> full staff roll -> 終 (G9/G10/G14), and a title card for each of the 63 provinces (`card_pNN`).
  - `tools/debug/save.py` show/edit/scene with checksum fix; an edited save loads via Continue into the edited map.
  - God mode: `--script tools/lua/god.lua` pins our side's battle HP (`$7E0B00+2*unit`); a run that hit game over at
    f3903 survives 12000 frames with it. No random encounters (battles start from the overworld), so no NOENC.
  - Tests: `tests/test_save.py`, `tests/test_scenes.py` (scene list format). Recon helpers in `tools/lua/`:
    `poke`, `slotpoke`, `modelog`, `log38` (battle state log), `memsnap` (WRAM+SRAM snapshots), `declog`.
- **Next:**
  1. Phase 3 identity build: `build.py` that unpacks (text table banks C3/C6, compressed graphics, tilemaps) and
     repacks with no edits into a byte-identical `build/heian_en.sfc`, as a test (`references/pipeline.md` §Identity).
  2. Carried from phase 2, not blocking: the story-progress flags (which provinces are won; needed for stage stress
     saves in phase 8) are not mapped; the battle map doesn't follow position (every forced battle uses the 紀伊
     map); G14 and T8 field-panel sources and the T6 variants' screens (`docs/re/graphics.md` §Still open).
- **Open bugs:** none.
- **Waiting on the user:** GUI keyboard input in `tools/mesen/Mesen.exe` not checked (headless session); not blocking. Title logo 平安風雲伝 kept Japanese under D5 (no official English logo); say if an English subtitle is wanted.
