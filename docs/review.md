# Phase 6 review verdicts (per batch)

Read-only pass over `python -X utf8 tools/pairs.py bNNN --out work/qa/review` (JP from `work/tl/bNNN.tsv`,
English from `script/*.tsv`). Critical/Important are fixed in the script before a batch is marked; Minors go to
`docs/polish.md`. Codex is out of quota until 2026-11-26, so these passes are by the controller in a fresh read.

| batch | verdict | date | notes |
|---|---|---|---|
| b001 | ok | 2026-11-22 | battle/system lines, chants, death lines, peddler, prologue 290-2A4; Minor 1D9 |
| b002 | fixed | 2026-11-22 | Important 2D6 fixed: Kaede said "I ain't no bandit" for あたしは山賊 (meaning reversed) |
| b003 | ok | 2026-11-22 | 410-435 read; Minor 421 |
| b004 | ok | 2026-11-22 | 436-45E |
| b005 | ok | 2026-11-22 | 45F-486; Minor 470 |
| b006 | ok | 2026-11-22 | 487-4BC |
| b007 | ok | 2026-11-22 | 4BD-4EA |
| b008 | ok | 2026-11-22 | 4EB-4FE, 300-328 |
| b009 | ok | 2026-11-22 | 329-374; spelling 353 fixed (Minor) |
| b010 | ok | 2026-11-22 | 375-3B4; 38D spelling, 399 Tamba -> Tanba (Minor, fixed) |
| b011 | ok | 2026-11-22 | 3B5-3EE; 3D1 spelling (Minor, fixed) |
| b012 | ok | 2026-11-22 | 3EF-544; 51B, 538 (Minor, fixed) |
| b013 | ok | 2026-11-22 | 545-56C; 554/556 sentences ran across a page break, 564/567 spelling (Minor, fixed); Minor 562 |
| b014 | ok | 2026-11-22 | 56D-596; 584 "I could not do it" read as a contradiction -> "nor could I side with it" (fixed) |
| b015 | ok | 2026-11-22 | 597-5B2; 599 "charms" -> "spells" (Minor, fixed) |
| b016 | ok | 2026-11-22 | 5B3-5E4; 5B5 page split (Minor, fixed) |
| b017 | ok | 2026-11-22 | 5E5-613 |
| terms, pilot | fixed | 2026-11-22 | 466 fields and 18 pilot rows read; Important 139 fixed (pilot called Kagura "her"; Kagura is a boy) |
| tilemaps | fixed | 2026-11-22 | 16 rows read against the JP; option0/option1 overflowed 8 cells -> "Messages"/"Walking" (D14); now linted (`check_tilemap`) |

## Harness review of phase 6 (2026-11-22, `.harness/reviews/heian-fuuunden-en-phase6.md`)

An outside read-only review found one Important meaning error the pass above missed, across b003/b005/b011:
先の帝 ("the former Emperor") was "the late Emperor" in 41F, 463 and 3CB, telling the player Kazan is dead while he
is alive as the Retired Emperor. Fixed in all three (38C "The last emperor" -> "The former Emperor" too), glossary row
added with "late Emperor" in Avoid, synopsis corrected. Its Minors are ticked in `docs/polish.md`.

Follow-up pass by a fresh worker (not the translator; read-only over the shipped English): every use of "late",
"Emperor", "Minister", "Counselor" and Kagura with she/her in C3/C6 read in context against the JP. No other dead/alive,
title or pronoun error found ("late" is otherwise "too late" / "of late"). This is still not the independent
reviewer the skill asks for (D13): a full independent re-read of every batch by `codex exec -s read-only` is due once
its quota returns (2026-11-26), and the phase 9 story pass reads every chapter in game anyway.
