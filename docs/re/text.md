# Text engine (dialogue, names, items, system messages)

ROM: HiROM + FastROM (`$FFD5=$31`), 1.5 MB file, header size byte `$0B` (2 MB), SRAM. File offset = `addr & 0x3FFFFF`.

## Encoding (verified)
- **16-bit little-endian codes, code = glyph index** into the dialogue font (`font.md`). No Shift-JIS anywhere.
- Verified by decoding the opening scene: file `0x33D74` reads 「で、広行、そなたいったい／どうするつもりだ、勝てるか？」
  then 「いえ、たぶん勝てませぬ・・」, exactly as on screen (`work/qa/newgame`, frame 4200, route `tools/routes/newgame.txt`).
- Kana block, gojuon order from `0x01`: `01-2E` あ..ん (あいうえお かきくけこ さしすせそ たちつてと なにぬねの はひふへほ
  まみむめも やゆよ らりるれろ わをん), `2F-37` ぁぃぅぇぉゃゅょっ, `38-4B` dakuten が..ぼ, `4C-50` ぱ..ぽ, `51` 。 `52` 、
  `53` ！ `54` ー `55` ？ (from the glyph sheet, `tools/fontview.py 0x90000 128 out.png`; spot-checked in decoded text).
- `0x0000` is the blank glyph, used as a full-width space (verified: 「　　　きろくしますか？」).
- `0x56` is drawn as a glyph slot `?!`-like in the font but the engine treats it as a control code (below).
- `0x58-0x3B6`: kanji and symbols (`0x18A` = ・, used in pairs as ・・ / ……). `0x380-0x3B6` are credit-only kanji
  (神楽 伝記 企画 原作 脚本 監督 …). `0x3C0-0x3CF` are logo cells (1995 ©NATSUME, TEAM 3D), not text.
- **`tbl/jp.tbl` (verified, phase 4)**: every glyph 0x00-0x376 and 0x380-0x3B6, keys are the two bytes as stored
  (`5800=東`). Kanji read by eye from `tools/kanjisheet.py` sheets (glyph x3 beside the MS Gothic guess), then every
  kanji used 8 times or fewer was checked in context with `tools/kanjictx.py` (fixes from context: 終 2CF, 勾 180,
  拠 2B8, 諏 2BC, 奴 330, 技 2DB, 条 27C, 馗 28E, 磯 2A0). Still a guess: 豚 0x110 (only in spell 豚木, maybe 啄),
  夷 0x0A8 (a name; looks like 275 夷 with extra bars), 奏 0x25A (歌会だ奏会だ). 0x57 and 0x377-0x37F are blank.
  Duplicates (0x0A8/0x275 夷, 0x0B0/0x334 深, and the credit set 0x380+) decode as `[lo][hi]` past the first code.
- 50 codes in 0x58-0x376 are used by no table string (e.g. 庵 拝 阪 蜘蛛 祭祀 蝦夷 鈴鹿; list:
  `tools/kanjictx.py --unused`): maybe other screens, maybe cut text.

## Control codes (verified from the reader at `C1:7270`; no code takes arguments)
| code | meaning | where handled |
|---|---|---|
| `FF` | end of string | `C1:7333` |
| `FB` | end of string, variant (sets `$1516=$0C`); ends 26 strings incl. 「きろくしますか？」 (0x229-0x22E), so probably end + Yes/No prompt (guess) | `C1:7338` |
| `FE` | newline (line step `$02C0` bytes in the WRAM tile buffer, 2 lines per box) | `C1:734B` |
| `FD` | wait for a key, then clear the box (page break, ▼ shown) | `C1:72C8` |
| `FC` | insert a name: string id from `$144E` mapped to a table id (`C1:74B5`: v<0x100 → v+0x54, <0x160 → v-0x100, <0x1A0 → v+0x22, <0x200 → v+0xAA, <0x210 → v-0x59) | `C1:7296` |
| `56` | insert a number: `$144C` printed as decimal digits, glyphs `0x2E1+digit` | `C1:72B1` / `C1:7507` |

## Pointer table (verified)
- `C3:0000` (file `0x30000`): **0x614 (1556) 16-bit pointers**, bank-relative. The first entry is `0x0C28`, which is also
  where the table ends.
- Bank by id (`C1:7276`): `id*2 < 0x600` → C3; `< 0x800` → **C6**; `< 0xA00` → C3; else **C6**. So ids 0x000-0x2FF and
  0x400-0x4FF are in C3 (file 0x30000), ids 0x300-0x3FF and 0x500-0x613 in C6 (file 0x60000).
- The message id comes from `$1416`; `$142C` is the word index inside the string.
- `tools/textmap.py` decodes every id and reports unreferenced ranges.
- Layout (verified by the identity build, `tests/test_identity.py`): strings are back to back in pointer order, 24
  strings are shared by several ids (123 ids), no pointer lands inside another string, all pointers even.
  `tools/kss_text.py` unpacks each bank to an ordered list of strings + unreferenced raw runs and packs it back.

## Text ranges (verified by `tools/textmap.py`)
- C3: strings `0x30C28-0x3F865`. Id 0x4FF is a dummy that points at `0x3F866`, a zero run to the bank end with no
  terminator (0x79A bytes, likely free: confirm with a trap fill). Unreferenced (verified orphans, phase 4: no table
  pointer, no 24-bit `ptr C3` anywhere): `0x3143A` (a lone FF), `0x33AA4` and `0x33B98` (・・・・。), `0x347CC`
  (おいていくぞ！！; its 16-bit value appears nowhere). `tests/test_script.py` fails on any new unexplained run.
- C6: strings `0x60000-0x6FFA3`; `0x6FFA4-0x6FFFF` unreferenced (92 bytes).
- Contents by id: 0x00-0x1BF short names (characters, items, spells, places: e.g. ほうじゅ, めのう), 0x1C0-0x23F battle and
  system messages (どうぐがいっぱいです, きろくしますか？, death lines, spell chants), 0x240+ field dialogue and events.

## Script files (phase 4)
- `tools/kss_script.py dump [--force]` writes `script/C3.tsv` (964 strings) and `script/C6.tsv` (493): columns `id kind
  jp en max notes`; id = table ids in hex joined by `+` when shared; final `{end}` left off; kind `data` for the 0x4FF
  zero run. Controls: `{br}` FE, `{page}` FD, `{name}` FC, `{num}` 56, `{end2}` FB. Decoding goes word by word (an
  unknown word is `[lo][hi]` and never misaligns). `--force` keeps en/max/notes.
- `tools/tilemap_text.py dump` writes `script/tilemaps.tsv` (T1-T5: 6 captions, save menu, options, quit/saved
  messages); these go in by redrawing small-font cells, not through the table.
- Tests: `tests/test_script.py` (roundtrip every id, no unknown codes, files match ROM, full bank coverage, orphans,
  dump never clobbers English).

## Other text (not in the table)
- **Staff roll** (lead for G9/G10, not verified): line records around `C2:CA80-CCFF` (file `0x2CA80`): a position
  byte, 16-bit tile words, `FFFF` / `FEFF` line ends. Some words fall in 0x380-0x3B6, so the credit kanji cells may
  be drawn from here. Handle with the credits redraw (phase 8).
- **Menu captions** (field menu, X button) are BG3 tilemap words in ROM, not strings: pointer table at `C1:9E7F`
  (file `0x19E7F`, 16-bit pointers `9E8B 9ED3 9F1B 9F63 9FAB 9FF3`), each entry 2 rows × 18 words (top row, then bottom
  row) of `0x20xx`, tile = 8×16 small-font cell (top tile `t`, bottom `t+0x10`). Verified: caption 3 at `0x19ED3` =
  「なかまの　のうりょくを　みます」 matches the BG3 map of `work/qa/menudump` frame 178. More tilemap-text tables are
  likely (status labels, battle menus): find them the same way (BG3 row from the VRAM dump, search the ROM for the words).
- Small 8×16 font tile order (from the caption): `30-3E` あ..そ, `3F` た, `50-5F` ち..み, `70-7A` む め も や ゆ よ わ
  を ん ら り (guess past `77`). Small kana sit in the bottom tile only (ょ = top `01`, bottom `2C`). Source of the font
  tiles: **`C8:8954`** (file 0x88954), LZ type 1, 0x1600 bytes → BG3 VRAM `$6000` (`compression.md`); full layout
  in `tools/smallfont.py`. More small-font tilemap text (save menu, options, status labels) is in `graphics.md` §T.
- Name plates under portraits and the party list (神楽, 藤太) use the dialogue font: names come from the table.

## Engine facts for later phases
- Dialogue font is 16×16 2bpp, 64 bytes per glyph, copied by `C1:73C1` into a WRAM buffer at `$7F:A000` (+`$1422`),
  two 32-byte halves 0x160 bytes apart. English needs a VWF or an 8×16 half-width path here (phase 5).
- Every string is in two full banks; English will not fit in place. Plan: expand the file to 2 MB (the header already
  says 2 MB) and relocate strings with a hook on the `LDA $C30000,x` / bank select at `C1:7270-728D` (and the name
  reader `C1:74F1`, the caption reader) to 24-bit pointers.
