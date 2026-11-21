# Polish list (Minors from review; tick each [x] when fixed or `waived: reason`)

- [x] 1D9 - 長老さま rendered "Elder..." without -sama -> "Elder-sama... I could not{br}keep my promise..."
- [ ] 421 - Kagura is named after the month he was brought (神楽月, the 11th month): consider "Kagurazuki, the month..." so the name's origin reads
- [ ] 2A2/glossary - prologue 芦屋道満 (Ashiya Doman) and 道摩 (Doma) are historically one man; 5B3 has Doma raising the "buried" twin. Decide whether the prologue should say Doma or keep Doman (game text differs)
- [ ] 5B3 - long Doma monologue (40 pages): re-read in game for pacing; "two halves of one ... yin and yang" check against 陰と陽
- [ ] 612 - 天太祝詞移転法呪 rendered "Heavenly Norito, Curse of Transference!": check against the chant style of 1CA-1D3
- [x] 470 - 似合いの夫婦 "but his fine bride" was loose -> "might have been his fitting bride, not the Ise Priestess"
- [ ] 562 - Moritaka says "Aye, that is just what I did" in formal register; elsewhere he is casual ("Yeah, that's just it")
- [x] 353/38D/3D1/51B/564/567 - British "travell-" forms -> American (glossary style rule added)
- [x] 554/556/5B5 - sentences ran across a `{page}` break; re-flowed
- [x] tilemaps option0/option1 - "Text speed"/"Walk speed" were 10 cells in an 8-cell label: now "Messages"/"Walking" (D14); `lint.py` checks every tilemap row's cell budget
- [x] phase 6 harness review M1 - 2AC/401/41F/426/470/4E0/3A3/3A5/3DC/558 re-flowed so no box ends mid-clause; `lint.py` warns on it (`page_warnings`); waived: chants 1CA-1D3 are paced one phrase per box like the Japanese (`lint.PAGE_WAIVED`). 549 checked: its page ends on a full clause
- [x] phase 6 harness review M2 - 3DC 中納言 -> "Middle Counselor" (the game gives Tamemitsu three titles; glossary 為光 row: translate the one each line uses)
- [x] phase 6 harness review M3 - 426 "Saigu Uzuki-dono of Ise". waived: kana さま/どの not added to the `batches.py` honorific check (どの = "which", さまに/さまざま give false hits); reviewers check kana honorifics by eye
- [x] phase 6 harness review M5 - stale "Aimi" in `work/tl/b002.out.tsv` and `terms.out.tsv` (gitignored) -> Aizen; `batches.py check b002` OK
