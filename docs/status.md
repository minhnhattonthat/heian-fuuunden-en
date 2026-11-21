# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5. Engine spike and marker build in progress (VWF, relocation, small/narrow names, party list, banners
  and the lint done; left: shoot the guessed popups and the opening speaker box, see Next 1-3).
  Last build: `build/heian_en.sfc` 2026-11-22 sha1 8eb9b3e58340 (2 MB, smoke ok); marker `build/heian_marker.sfc`
  2026-11-22 sha1 9be2ddbb5507 (banner offsets; banner/slot/exit scenes shot, `work/qa/r2/`).
- **Done:**
  - **Lint** `tools/lint.py` (in `tools/check.py` via `tests/test_lint.py`): dialogue 176 px/line, 160 on a 3rd
    line before `{page}` (JP calibration: 12-px glyphs, 14 per line, 13 on that line), 3 lines/page, `{name}` = widest
    English name (64 until names exist), `{num}` = "99999"; fields via `fit_field`; party via `party_fits`; popups;
    codes multiset, encodable, no JP, no ordinal after a variable, stub last line. `--max` filled the `max` column
    (`176/160 x3`, `48 field`, `72 field`, `40 narrow`, `112 popup`, "(guess)" where not shot); `--strict` makes
    untranslated rows errors (phase 7+). `script/keep_jp.txt` (optional) lists ids kept Japanese.
  - Banners (windows.md): title slot list = place/port/province in 48 px; place/port banner and map-exit banner = 72 px
    from x 88; the build re-centres both offset tables for English strings (`insert.banner_offsets`). New scenes
    `title_slots`, `place_banner`, `exit_banner`, `opening`; warp route step `tap BUTTON until MM.SS`;
    `tools/lua/execpoke.lua` forces a value when a PC executes (banner place index).
  - Phase 5 (`docs/re/hooks.md`, `docs/re/windows.md`): ROM expanded to 2 MB; every table string relocated to
    `$D8-$DE` with a 24-bit `PTRS` table (`tools/insert.py`); VWF on both glyph paths, English digits for `{num}`;
    fonts `fonts/en16.png`, `fonts/en8.png` (Pixel Operator, CC0) and `fonts/en_narrow.png` (own art,
    `tools/font_narrow.py`) (D9, D10, D11).
  - Small mode (D10): `{small}line 1{sbr}line 2` = two 8-px lines in one 16-px field; `{narrow}` = the same in the
    narrow font, last fallback in `insert.fit_field` (one-word names over 48 px: Sadamitsu, Yasumasa, Semimaru).
  - **Party list (D11)**: 8 slots of 5 tiles on one 8-px row, narrow font, 40 px (`PartyName` in `asm/main.asm`,
    slot table `C1:A3CB`, tilemaps `C8:939E`/`C8:9450` rewritten by `tools/gfx_edits.py`; `gfx_blocks.pack` can now
    move a grown block to `$DF:8000+`). Verified `work/qa/party/` (stress build `--qa 054=Sadamitsu --qa
    100=Yasumasa`). Build rule: party names (054-083) must fit 40 px narrow, letters only (`insert.party_fits`).
  - Width gate measured (windows.md): dialogue 176 px x 3 lines (160 on the line before `{page}`), battle prompts
    176 x 1, menu popups 112, renderer-2 fields 48 px, party list 40 px narrow. `tools/lua/r2log.lua` logs every
    renderer-2 call; `tools/lua/wramuse.lua` maps free WRAM (`$7E:1B25-1CFF`).
  - Phases 1-4: recon (`docs/re/`), warp tool + save editor + god mode, identity build, `tbl/jp.tbl` + `script/`.
  - Check: 40 passed (`test_lint.py`, `test_banner_offsets` new).
- **Next:**
  1. Shoot the "(guess)" budgets (windows.md §Not measured yet, `tools/lint.py POPUPS`): popups 1C8/1C9 (item full /
     can't equip), 244 (`quit_nosave`), 28D/28E (`C5:A4B5`), labels FF (`C0:D938`) and 203 (`C5:183B`), the
     `C1:6011` party-name screen, jutsu/shikigami lists outside battle (`C1:2E0E`, `C1:57C0`). Find each trigger from
     the caller's mode/sub, add a scene, shoot the marker build, update the budget.
  2. Opening palace scene (ids 29B-2A5: speaker line + 3 lines): find its trigger, measure, and teach the lint the
     speaker line. Province card 1B9: shoot mid-card (`SHOTS_AFTER`) to confirm 176.
  3. Then phase 6 (glossary first; translators get the `max` column and `tools/lint.py`).
  4. Non-table Japanese (battle command labels, status labels, captions, help screen): graphics, phase 8.
  5. Leads kept: staff roll near `C2:CA80` (credits redraw), small-font tilemap text (`script/tilemaps.tsv`),
     story-progress flags unmapped, item inventory and squad roster not mapped in the save (`--qa ID=...` stands
     in for items and party names).
- **Open bugs:** none. Untranslated (Japanese) party names show only their top half in the party list until phase 6
  fills `en` (by design of the one-row slots).
- **Waiting on the user:** GUI keyboard input in `tools/mesen/Mesen.exe` not checked (headless session); not blocking. Title logo 平安風雲伝 kept Japanese under D5 (no official English logo); say if an English subtitle is wanted.
