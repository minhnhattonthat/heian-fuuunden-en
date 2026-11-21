# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 7. Insert, fit, check: in progress. Phase 6 met except the independent review (D13): every row
  translated, lint 0 errors/0 warnings (tilemaps now linted), `batches.py check` 0 problems; the harness review's
  Important findings fixed (先の帝 = "the former Emperor", not "late"; tilemap cell check; D13 recorded); full Codex
  re-read of every batch due when its quota returns (2026-11-26).
  Last build: `build/heian_en.sfc` 2026-11-22 sha1 7eb7f27372c6 (2 MB, smoke ok); marker `build/heian_marker.sfc`
  2026-11-22 sha1 6a70b2581615 (135/135 warp scenes ok, shots in `work/qa/marker_warp/`). No build since English.
- **Next (phase 7):** build the English ROM (`build.py`), `lint.py --strict`, `romdiff.py` (no writes outside the
  allowed ranges), smoke + `warp_all.py --rom build/heian_en.sfc` and look at the shots for overflow/garble.
  Minors left for phase 9 are in `docs/polish.md`.
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
