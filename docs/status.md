# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 9. Release built and verified (worker 7, 2026-11-22): `release/Heian_Fuuunden_EN_v1.0.zip` ready (rebuilt with the English title logo, D23; sums below under "after the release"); publishing is the user's call.
- **Phase 9 done (worker 7):** story pass 16/16 chapters ok (`qa_gate.py check work/qa/story/manifest.tsv
  work/qa/story/verdicts` exit 0; verdicts by the worker itself, D22). Minors fixed and ticked in polish.md: 3CA
  "plague (smallpox)" gloss, 56D and 2EC stray contractions (Doma double, Kazan); 5B3 closed (pacing and yin/yang
  checked in the story read). Rebuilt (sha1 7b61cd2550a6), re-toured 139/139; 7 sheets changed by typing timing only:
  `work/qa/verdicts/final_2.tsv` 7/7 ok, visual gate exit 0. `tools/release.py` passed every gate: 52 tests, lint,
  smoke, jp_left 0 runs, both QA gates, textcover 1556/1556, polish all ticked, README, debug off, patch re-apply ==
  build. Zip 82169 B; patch `Heian_Fuuunden_EN_v1.0.bps` sha1 0916ee05f53a; base CRC32 4640D1A2; result CRC32
  47208D73 sha1 7b61cd2550a6 (`build/Heian_Fuuunden_EN_v1.0.sfc`).
- **2026-11-22, after the release:** English title logo (D23, user's request): `tools/logo_en.py` renders
  fonts/Shojumaru-Regular.ttf (OFL) to the committed `gfx/logo_en.png`; gfx_en.apply_blocks writes it to the logo
  tiles C8:31F3 and the shadow sprites C8:0000 (both repack smaller, in place; ranges added to romdiff_ranges.txt).
  Cold-boot title shot `work/qa/logo/built/final.png` == the approved preview; fade-in checked; `tests/test_logo.py`;
  check.py 54 passed. Build sha1 74ed182dd65b. New tour scene `title_logo` (scenes.tsv; waits for step 01.01.0C);
  re-toured 140/140, `qa_gate init --build`, 5 changed sheets re-read (`work/qa/verdicts/final_3.tsv`, all ok:
  018 = logo, the rest typing timing), gate exit 0, inkbox 5/5. Release rebuilt by the user (`release.py --force`, every
  gate passed): zip 86776 B, patch sha1 5e6ff3d959c9, base CRC32 4640D1A2, result CRC32 66693CE8 sha1 74ed182dd65b.
- **Next:** publish only when the user asks (`$SKILL/references/pipeline.md` §Publish; never `gh release create`
  unprompted). Optional: D13's Codex re-read of the batches once its quota returns (2026-11-26); any fix then means
  rebuild, re-tour, re-verdict the changed sheets and `release.py --force`.
- **Phase 9 tooling (worker 6):** `tools/release.py` (every gate of pipeline.md §Release; `--help` safe; checksum
  fixed in the release step); `tools/jp_slots.py` + `jp_left.py --tbl tbl/jp.tbl --slots build/jp_slots.txt`;
  README.md filled, zip README `docs/release-readme.txt`; 421 "Kagurazuki" and 562 Moritaka register fixed.
- Phase 8 met 2026-11-22 (worker 5): visual-QA verdicts
  `work/qa/verdicts/final_1.tsv` 18/18 ok (fresh read-only pass by the worker itself, no reviewer available),
  `qa_gate.py check work/qa/manifest.tsv work/qa/verdicts` exit 0 on build sha1 92f0225dc7e1; smoke ok, check.py 52
  passed, textcover 1556/1556. Verdict notes: 205 "Kagura's turn." sits ~35 px left (fixed indent sized for enemy full
  names, as the Japanese indent): new `docs/polish.md` line; shop plate "Mer/chant" is D17's syllable split.
- **Phase 8 record (2026-11-22, worker 4):** Done:
  - **Text coverage 1556/1556, no waivers** (`textcover.py work/qa/cover build/strings.tsv`): `tools/lua/textids.lua`
    logs the id each reader opens; `tools/debug/msgview.py --uncovered work/qa/cover/warp` forces every other id into
    the new-game opening's dialogue box (cold boots, ~25 ids each, page shots `work/qa/cover/view/*/msg_*.png`).
    build.py writes `build/strings.tsv` (ids). Re-run: coverage warp tour `warp_all.py --out work/qa/cover/warp
    --no-states -- --script tools/lua/textids.lua`, then msgview.
  - **inkbox 5/5** (`tools/inkbox_check.py` over `work/qa/en_warp`): Yes/No 229 box, 229, 0B8, 221, 243. Not centred by
    design (Japanese fills from the left or cursor-fixed): 244, 28B, 1C8/1C9, 28D/28E (D21).
  - Fixes (D21): save popup 243 / quit 244 padded to the 120 px the Japanese uploads (a see-through tile showed);
    overworld squad/province labels padded to 6 tiles in the engine (`LabelName`/`PadLabel`, hooks.md; "Kii" showed
    stale tiles or a hole); 0B8 battle help prompt was inside an item-name field range (now a centred message);
    `centre.py` rounds to the nearest space (14 battle messages moved ≤4 px); narrow font got a comma (place 10E).
  - Scenes: card_p* hold 245 (cards shot complete: all 63 checked); `title_slots` route fixed (it never reached the
    slot list); stress scenes `stress_items` (every unit's 4 slots = 8 widest item names x99; items live at slot
    offset 08A + unit*8, id + count), `stress_status`, `stress_slots` (map 0E = widest place). All look right.
  - Smoke ok; `warp_all` 139/139 on en and on the original (`work/qa/tour_jp`).
- **Phase 8 gate (done by worker 5):** (1) Read every sheet in `work/qa/tour/sheet_*.png` (English left, Japanese right; scene list
  `work/qa/tour/sheets.tsv`) with `docs/visual-qa-brief.md` as a fresh read-only pass, write
  `work/qa/verdicts/final_1.tsv` (`sheet_NNN<TAB>ok|issue<TAB>note`), then `qa_gate.py check work/qa/manifest.tsv
  work/qa/verdicts` must exit 0. The previous session already read an older tour of the same scenes and fixed what it
  found; known ok: EN/JP shot timing differs in battle_enemy_attack, shop, ending, ending_win (mid-typing). Any fix
  means rebuild, re-tour (`warp_all.py --rom build/heian_en.sfc --out work/qa/en_warp --no-states --jobs 6`),
  `tools/qa_sheets.py`, `qa_gate.py init ... --build build/heian_en.sfc`, `tools/inkbox_check.py`. Then phase 8 is
  met: move Phase to 9.
  - Not mapped (optional stress, add when found): levels/HP/exp/money fields, learned jutsu lists. Polish candidate
    for phase 9: `{name}` messages (205 turn, 1B9 cards) are centred for a typical name, not each name (no runtime
    centring); mixed small/narrow fonts in two-line lists (D10).
  - Tools: `warp.lua --var DUMP_PPU=1`, `--var SHOTS_AFTER=N`, `warp_all.py --scenes F`; `tools/boxedges.py SHOT x,y`
    finds a window's inner rect; `tools/lua/namelog.lua` logs which `{name}` ids a message takes.
  - Small-font text is monospace (one 8-px cell per letter); "Messages" fills its 8 cells and touches the arrow.
    The place_banner shot is empty in the marker build too. Minors left for phase 9 are in `docs/polish.md`.
- **Earlier:** Phase 7 met 2026-11-22 (lint --strict clean, romdiff gate in build.py). Phase 6 met except the
  independent review (D13): a full Codex re-read of every batch is due when its quota returns (2026-11-26),
  before the phase 9 story pass. Review Minors left: romdiff `--writes` log + asar `assert read`s; a standing
  reader/branch-target scan test.
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
- **Waiting on the user:** GUI keyboard input in `tools/mesen/Mesen.exe` not checked (headless session); not blocking. Release v1.0 zip rebuilt with the English logo (D23); publishing (repo, GitHub release) waits for the user; not blocking.
