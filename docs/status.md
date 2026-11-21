# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 8. QA in the emulator: in progress. Graphics text is all English (worker 3, 2026-11-22, `tools/gfx_en.py`,
  D18-D20): battle command labels, game-over card, staff roll + end card, file select, help panels, prologue
  (details `docs/re/graphics.md` §Phase 8 progress; test `test_gfx_lettering`). Left for phase 8: the visual-QA gate
  (`qa_gate.py` over a full warp tour), `inkbox.py` on choice/centred boxes, stress-save menu sheets, `textcover.py`.
  Non-blocking for the owner: staff-name readings in the credits are Hepburn guesses except the two composers; 能 剛
  = "Tsuyoshi No" is the least sure (D19). Earlier: Phase 7 review fixes done 2026-11-22 (f9acb91):
  `tools/centre.py` (D15) centres the Japanese-centred messages and pads renderer-2 popups to the window width
  (this also fixed a see-through hole after short popup text); lint `blank_errors`; tests build their own ROMs
  (`tests/conftest.py` `built_rom`); build.py deletes a ROM that fails romdiff. Review Minors left: #2 write log
  for romdiff (`--writes`) + asar `assert read`s; #3 reader/branch-target scan as a standing test.
  Phase 8 so far: small font + T1-T6 English (`tools/smallfont_en.py`, D16; `docs/re/graphics.md` §Phase 8
  progress lists what is left). warp.lua now re-presses A when the file-select scroll stalls (mode 3 sub 4).
  Session 2026-11-22 (worker 2): はい/いいえ box after 229 = small-font map `C8:BBEE` -> "Yes No" (tilemaps.tsv
  yesno0, `tilemap_text.SPAN`; `gfx_blocks.RELOC_PTRS` now also takes code operands (lo16, bank) for blocks named by
  `LDA #` pairs; scene `battle_save_no` checks the cursor on No). Portrait name plates (G15) = 94 raw images at
  `C7:A1FF` -> English (`tools/plates.py`, D17; test `test_name_plates`). 蘆太 (font code 0x9B) is a variant 藤:
  name 05C/0CB and line 480 now say Tota (glossary). `tilemap_text.py dump --force` keeps notes now.
  Last build `build/heian_en.sfc` sha1 849e2f78cab2 (2026-11-22, worker 3). Phase 7 met 2026-11-22: `build.py` green with English,
  `lint.py --strict` 0 errors / 0 warnings / 0 untranslated (control codes matched; tilemaps linted), romdiff clean
  (build.py now fails on any byte outside `tools/romdiff_ranges.txt`; `tests/test_romdiff.py` builds en + marker),
  smoke ok, `warp_all.py --rom build/heian_en.sfc --out work/qa/en_warp` 135/135 scenes ok (sheets in
  `work/qa/en_warp_sheets/`: no overflow or garble seen in dialogue, menus, shop, status, squad screens).
  Phase 6 met except the independent review (D13): full Codex re-read of every batch due when its quota returns
  (2026-11-26), before the phase 9 story pass.
- **Next (phase 8):** (1) a fresh full warp tour of the current build (`warp_all.py --rom build/heian_en.sfc --out
  work/qa/en_warp`), sheets into `qa_gate.py init`, verdicts from a fresh read-only pass (no reviewer agents: Orca
  refuses nested workers; write the verdicts yourself or with `codex exec`), `qa_gate.py check` exit 0; zoomed shots
  of every former graphics-text scene (`battle_cmd_*`, `game_over`, `credits`/`credits_end` with SHOTS_AFTER,
  `prologue` late frames, `battle_help`, `help_menu`, file select = `boot.txt` final frame) and every chapter card
  `card_p*` at a late frame. (2) `inkbox.py` on choice/centred boxes (Yes/No 229, squad confirm 28E, centred
  popups D15). (3) stress saves (`tools/debug/save.py`: longest names, full lists, max numbers) with menu sheets.
  (4) `textcover.py` over the tour logs (textcover.lua probe), waive what is unreachable (D12 palace ids 297-2A6).
  - Tools for this: `warp.lua --var DUMP_PPU=1` (VRAM/CGRAM/OAM with the shot); `--var SHOTS_AFTER=N`; a scenes
    file of your own via `warp_all.py --scenes F` (e.g. a longer hold for the staff roll: credits hold 11500).
  - Small-font text is monospace (one 8-px cell per letter); "Messages" fills its 8 cells and touches the arrow.
  Chapter cards (`card_p*`) were shot mid-typing: shoot later frames when checking them. The place_banner shot is
  empty in the marker build too (shot before the text draws). Minors left for phase 9 are in `docs/polish.md`.
- **Phase 6 record (2026-11-22):**
  - Review pass finished: b003-b017 ok, terms/pilot fixed (Important: pilot 139 called Kagura "her"). Minor fixes
    (American spelling, sentences re-flowed off `{page}` breaks, 丹波 = Tanba, まじない = spells) are now style
    rules in `glossary.md`.
  - `glossary.md` (policy, style, characters, places, terms; enforced by `tools/batches.py check`, also a test),
    `docs/translator-brief.md`, `docs/style-reference.md` (pilot 131-13B), `docs/synopsis.md`.
  - Wave 0: every name/item/jutsu/shikigami/class/place/province field (466 rows) fitted with `batches.py fit`.
  - b001 (battle/system messages, death lines, spell chants, medicine peddler, prologue 290-2A4) and b002
    (Michinaga/Hiroyuki, epilogues 2B1-2EE, Kumano opening 401-40F) merged.
  - **Kagura is a boy** (id 295 男子; surviving twin of Emperor Kazan and Lady Kishi): he/him everywhere.
  - Tools: `tools/batches.py` (split/check/merge/fit; honorifics 殿/様 enforced), lint `NAME_CLASSES` (per-row
    `{name}` width: squad msgs = party names, 214 shikigami, 112/218/21E items, 1B9 provinces; others = widest
    name, ~119 px), `kss_script.write_tsv` atomic and quote-safe (a `"` once truncated C3.tsv mid-write).
  - b008 (Moritaka and Takato, Kaede/Aoi/Kikyo at Togakushi, Kumano townsfolk 300-323, Seimei's Kansai-dialect
    apprentice 324-328) merged. 夷 renamed Natsume (furigana なつめ, 315) in 064/0D3. `batches.py` honorific skip
    now has 本殿 (main hall).
  - b003-b007 (Kumano after Tenkai's death, Seimei's and Michinaga's briefings, Kagura's parentage told 41F/463,
    Yamawaro elder, recruits: Morohide, Yorimitsu, Semimaru, Uzuki/Hazuki, Jogu, Hida, Aizen/Horen, Saeki daughter,
    Yorinobu/Sugimaru, Takato) merged 2026-11-22. New terms are in `glossary.md` "Decisions" (b003-b007).
    愛深 renamed Aizen (game furigana) in 06A/0D9/2DA. Dev placeholder rows まさだ -> "Not yet.".
  - b009-b013 (329-56C: apprentice, Shitennoji, Abeno and Kyoto townsfolk, Kebiishi and Palace guards, Kishi's
    Yamawaro birth 3DC, the Retired Emperor incognito 3E8-3F3, road bandits, Masamitsu, Kainki, Kaede/Aoi vs
    Chobukumaru, Doma's doubles, Usagino, Kuji Hogen, Boke Tengu) merged 2026-11-22; terms in `glossary.md`
    "Decisions" (b009-b013). Honorific skip now also has 有り様 and る様.
  - b014 (56D-596: Doma's doubles, Sumitomo, Tenkai controlled by Doma and his death 584-586, Akana, the Suwa
    hidden village, Moriya; Tenkai was born a Yamawaro) merged. 反魂宝珠 (variant of 反魂法珠) -> Hangon Jewel.
  - Codex CLI is out of quota until 2026-11-26 (no codex translators/reviewers before then).
  - b015-b017 (597-613: Moriya's death, Doma's doubles, Masakado sealed, Isogami, Doma's truth about Akoya, Momiji,
    boatmen, field notes, Sumitomo crumbles, Semimaru's sacrifice) merged; terms in `glossary.md` "b014-b017".
    `script/tilemaps.tsv` en filled (cell budgets in `max`; option labels 10 cells vs 8: `docs/polish.md`).
  - Review: `tools/pairs.py bNNN.. --out work/qa/review` writes `>> id | JP` / EN pairs (English from `script/`).
    Verdicts in `docs/review.md`, Minors in `docs/polish.md`. 2D6 (Kaede, meaning reversed) fixed.
  - `work/tl/` is gitignored: in a fresh clone the batch files are gone; `docs/review.md` lists each batch's id range.
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
  - Check: 43 passed.
- **Next:**
  1. Phase 7: see "Next (phase 7)" above. Id 100 (empty squad slot, `　　`) stays blank by design.
  2. Non-table Japanese (battle command labels, status labels, captions, help screen, title logo under D5):
     graphics, phase 8.
  3. Leads kept: staff roll near `C2:CA80`, small-font tilemap text (`script/tilemaps.tsv`, incl. the New Game
     scrolling prologue), story-progress flags unmapped, item inventory and squad roster not mapped in the save
     (`--qa ID=...` stands in). Which unit opens the 音楽 battle menu (`$1516=6`) is not mapped.
- **Open bugs:** none. Untranslated (Japanese) party names show only their top half in the party/squad slots until
  phase 6 fills `en` (by design of the one-row slots).
- **Waiting on the user:** GUI keyboard input in `tools/mesen/Mesen.exe` not checked (headless session); not blocking. Title logo 平安風雲伝 kept Japanese under D5 (no official English logo); say if an English subtitle is wanted.
