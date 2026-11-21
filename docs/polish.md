# Polish list (Minors from review; tick each [x] when fixed or `waived: reason`)

- [x] 1D9 - 長老さま rendered "Elder..." without -sama -> "Elder-sama... I could not{br}keep my promise..."
- [x] 421 - Kagura is named after the month he was brought (神楽月, the 11th month) -> "He named you Kagura, after Kagurazuki, the month in which you were brought to us."
- [x] 2A2/glossary - prologue 芦屋道満 (Ashiya Doman) and 道摩 (Doma) are historically one man; 5B3 has Doma raising the "buried" twin. waived: the game itself writes 芦屋道満 in the prologue and 道摩 afterwards; the English keeps both as the Japanese does, and 5B3 makes the link
- [x] 5B3 - long Doma monologue (40 pages): re-read in game for pacing; "two halves of one ... yin and yang" check against 陰と陽. Story pass 13 (worker 7): every page ends on a full clause and follows the Japanese page for page; "two halves of one, with the same power, split into yin and yang" = 二人で一人 同じ力 陰と陽にわかれている. waived: no in-game re-read; msgview already showed every page fits (textcover 1556/1556)
- [x] 612 - 天太祝詞移転法呪 rendered "Heavenly Norito, Curse of Transference!": checked against 1CA-1D3 (invocation then a short exclaimed name, "Namu, Four Heavenly Kings, descend!") and the glossary ruling; kept
- [x] 205 and other `{name}` lines (204, 20D, 20E, 1B9 cards) - centred by a fixed indent that fits the widest name the line can take (205 also takes enemy full names, e.g. Tachibana no Morohide 118 px), so "Kagura's turn." sits ~35 px left of centre; the Japanese also uses a fixed indent. Fix needs runtime centring (pad by the name's width at the `{name}` reader C1:74F1) or waive. waived: the Japanese places these lines by the same fixed indent, every name fits its box (stress scenes, phase 8), and runtime centring would touch the shared `{name}` reader for a cosmetic gain; listed under Known issues in both READMEs
- [x] 470 - 似合いの夫婦 "but his fine bride" was loose -> "might have been his fitting bride, not the Ise Priestess"
- [x] 562 - Moritaka says "Aye, that is just what I did" in formal register; elsewhere he is casual -> "Yeah... that's just what I did, Kuji Hogen... There's nothing past here but the house I used to live in... Don't tell me... my brother...?"
- [x] 353/38D/3D1/51B/564/567 - British "travell-" forms -> American (glossary style rule added)
- [x] 554/556/5B5 - sentences ran across a `{page}` break; re-flowed
- [x] tilemaps option0/option1 - "Text speed"/"Walk speed" were 10 cells in an 8-cell label: now "Messages"/"Walking" (D14); `lint.py` checks every tilemap row's cell budget
- [x] phase 6 harness review M1 - 2AC/401/41F/426/470/4E0/3A3/3A5/3DC/558 re-flowed so no box ends mid-clause; `lint.py` warns on it (`page_warnings`); waived: chants 1CA-1D3 are paced one phrase per box like the Japanese (`lint.PAGE_WAIVED`). 549 checked: its page ends on a full clause
- [x] phase 6 harness review M2 - 3DC 中納言 -> "Middle Counselor" (the game gives Tamemitsu three titles; glossary 為光 row: translate the one each line uses)
- [x] phase 6 harness review M3 - 426 "Saigu Uzuki-dono of Ise". waived: kana さま/どの not added to the `batches.py` honorific check (どの = "which", さまに/さまざま give false hits); reviewers check kana honorifics by eye
- [x] phase 6 harness review M5 - stale "Aimi" in `work/tl/b002.out.tsv` and `terms.out.tsv` (gitignored) -> Aizen; `batches.py check b002` OK
- [x] story pass 08 minor - 3CA "plague (smallpox)" kept the JP furigana gloss as a parenthesis in speech: now "smallpox spread through the capital"
- [x] story pass 11 minor - 56D Doma double "I'll tell you this" was the only contraction in his voice: now "I will"
- [x] story pass 15 minor - 2EC Kazan's farewell "how you've grown" was his only contraction: now "how you have grown"
