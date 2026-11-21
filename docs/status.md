# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2. Debug tool in progress (warp + save editor work; battle, game over and name entry not reached yet). Last build: none yet.
- **Done:**
  - Step 0 setup and phase 1 recon (text, compression, graphics survey): see `docs/re/`.
  - Phase 2 so far (`docs/re/save.md`): SRAM slot layout and checksum, live-state fields (map/x/y per squad), main
    mode table `$34`. `tools/debug/warp.lua` warps from a cold boot (New Game -> edit slot 1 + checksum -> soft
    reset -> Continue -> scene pokes/route steps `N btn`, `wait MM.SS`, `poke`, `mash N`). `tools/debug/warp_all.py`
    runs every scene in parallel: **36/36 ok** (`work/qa/warp/index.tsv`, sheets `work/qa/warp/_all/sheet.png`,
    `menus.png`): 25 field maps 01-19, start town, 6 field menus (T1 captions, T2 save menu, T3 settings, T6 status),
    save message (T5), prologue (G8 ruby text), ending -> credits (vertical staff kanji, G9 screen). States in
    `work/states/<scene>.mss`.
  - `tools/debug/save.py` show/edit/scene with checksum fix; an edited save loads via Continue into the edited map
    (`tools/routes/continue.txt`, `work/qa/savetest`). Test `tests/test_save.py`.
  - Recon helpers: `tools/lua/poke.lua`, `slotpoke.lua`, `modelog.lua` (mode/sub/`$0A00` change log).
- **Next (phase 2 still open):**
  1. **Battle** (G6 command buttons): mode 7 needs the overworld. Get there for real: find an exit tile on map 02
     (walk with `modelog.lua`; mode 5 -> 4 marks the exit), put that x/y in the slot (`138=`, `144=`), then in the
     scene route `wait 04.05;poke 7E0036=0019;wait 07`. Or trace `C1:501D` (enemy group -> `$12AC`). Then add a
     `GOD` option (find party HP; per-squad data near `$30:6180`?) and scenes battle_win / battle_lose / game over.
  2. Overworld scene (mode 4, kanji place-name labels: a graphics-text row to add to `graphics.md`).
  3. Shikigami creation / name entry (G7 kana grid?): `menu_shikigami` shows a refusal message on a new game;
     needs items or a story flag. T4 おつかれさまでした (save + quit).
  4. Chapter structure: find the story progress variable (event flags `$30:6240+`) so chapter starts can be scenes.
  5. Ending scene is a forced `$34=9` from the field; confirm the full credits roll (longer `mash`, shots every 120).
- **Open bugs:** none.
- **Waiting on the user:** GUI keyboard input in `tools/mesen/Mesen.exe` not checked (headless session); not blocking. Title logo 平安風雲伝 kept Japanese under D5 (no official English logo); say if an English subtitle is wanted.
