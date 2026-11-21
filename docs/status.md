# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 6. Translate: not started (phase 5 width gate met 2026-11-22; glossary first).
  Last build: `build/heian_en.sfc` 2026-11-22 sha1 7eb7f27372c6 (2 MB, smoke ok); marker `build/heian_marker.sfc`
  2026-11-22 sha1 6a70b2581615 (135/135 warp scenes ok, shots in `work/qa/marker_warp/`).
- **Done:**
  - **Phase 5 met** (engine spike + marker build + width gate): every box variant is measured in-game
    (`docs/re/windows.md`; every row's budget is in the `max` column of `script/*.tsv`, no "(guess)" left).
    Last session: squad formation screen names got the D11 remedy (`PartyName` at `C1:6011`, slot table `C1:E6CE`,
    panel C8:9506 widened; scene `squad_form`); squad exchange screen reached (scene `squad_xchg`: mode 0E, Yes)
    and shown whole with a 10-name stress build; province card 1B9 = one 176-px line in the top box; palace ids
    297-2A6 are unreferenced (cut scene), translated anyway as speaker line + 3 lines (D12, `lint.SPEAKER`).
  - Lint `tools/lint.py` (in `tools/check.py`): dialogue 176 px/line, 160 on a 3rd line before `{page}`, 3
    lines/page (+ speaker line on 297-2A5), `{name}` = widest English name (64 until names exist), `{num}` =
    "99999"; fields via `fit_field`; party names 40 px narrow (`party_fits`); popups; codes multiset, encodable, no
    JP, no ordinal after a variable, stub last line. `--max` fills `max`; `--strict` (phase 7+) errors on
    untranslated rows.
  - Engine (`docs/re/hooks.md`): 2 MB ROM, strings relocated to `$D8-$DE` with 24-bit `PTRS`; VWF on both glyph
    paths; fonts `fonts/en16.png`, `fonts/en8.png`, `fonts/en_narrow.png` (D9-D11); small mode (D10); party and
    squad slots 5 tiles narrow (D11, D12).
  - Phases 1-4: recon (`docs/re/`), warp tool (135 scenes) + save editor + god mode, identity build, `tbl/jp.tbl`
    + `script/`.
  - Check: 41 passed.
- **Next:**
  1. Phase 6: glossary first (`glossary.md`: party/unit names 054-083 at 40 px narrow, provinces 280-288 / 1A0+
     as 48-px fields, jutsu/shikigami 48 px, items 48 px), then batches with the translator agents; each gets the
     `max` column and runs `python -X utf8 tools/lint.py`. Id 100 (empty squad slot, `　　`) must stay blank.
  2. Non-table Japanese (battle command labels, status labels, captions, help screen, title logo under D5):
     graphics, phase 8.
  3. Leads kept: staff roll near `C2:CA80`, small-font tilemap text (`script/tilemaps.tsv`, incl. the New Game
     scrolling prologue), story-progress flags unmapped, item inventory and squad roster not mapped in the save
     (`--qa ID=...` stands in). Which unit opens the 音楽 battle menu (`$1516=6`) is not mapped.
- **Open bugs:** none. Untranslated (Japanese) party names show only their top half in the party/squad slots until
  phase 6 fills `en` (by design of the one-row slots).
- **Waiting on the user:** GUI keyboard input in `tools/mesen/Mesen.exe` not checked (headless session); not blocking. Title logo 平安風雲伝 kept Japanese under D5 (no official English logo); say if an English subtitle is wanted.
