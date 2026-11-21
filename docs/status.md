# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 4. Extract next (phase 3 identity build done). Last build: `build/heian_en.sfc` 2026-11-21, sha1
  `3b0ca4a2...` = the original (no edits yet), smoke ok.
- **Done:**
  - Phase 3: `build.py` (build / `identity [--recompress]`) unpacks the dialogue banks C3/C6 + pointer table
    (`tools/kss_text.py`, JSON layout in `work/unpack/text/`) and the 541 compressed blocks in `gfx/blocks.tsv`
    (`tools/gfx_blocks.py`, `work/unpack/gfx/`), repacks them and fixes the header checksum (mirrored sum for
    1.5 MB, `tools/bps.py`): IDENTICAL. Encoder `kss_comp.encode` roundtrips every block; byte-exact on 302/541
    (LZ tie-break order not recovered), so unchanged blocks keep their original bytes. `tests/test_identity.py`
    (identity, encoder roundtrip, checksum, text edit shifts later strings, overflow refused, block edit lands).
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
  1. Phase 4 extract (`references/pipeline.md` §Extract): build `tbl/jp.tbl` (kanji 0x58-0x3B6 by eye from
     `tools/fontview.py` sheets + `fontmatch.py` guesses, checked in decoded text), dump `script/` from the
     `kss_text` layout (ids, shared ids, `jp`, `en`, `max`), roundtrip test `encode(decode(words)) == words` for every
     id, coverage test incl. the unreferenced C3 runs (`0x3143A`, `0x33AA4`, `0x33B98`, `0x347CC`) and other text
     outside the table (menu captions `C1:9E7F`, small-font tilemaps in C8, `graphics.md` §T).
  2. Later: graphics blocks that grow need relocation + load-table pointer rewrite (`gfx_blocks.pack` refuses now).
  3. Carried from phase 2, not blocking: the story-progress flags (which provinces are won; needed for stage stress
     saves in phase 8) are not mapped; the battle map doesn't follow position (every forced battle uses the 紀伊
     map); G14 and T8 field-panel sources and the T6 variants' screens (`docs/re/graphics.md` §Still open).
- **Open bugs:** none.
- **Waiting on the user:** GUI keyboard input in `tools/mesen/Mesen.exe` not checked (headless session); not blocking. Title logo 平安風雲伝 kept Japanese under D5 (no official English logo); say if an English subtitle is wanted.
