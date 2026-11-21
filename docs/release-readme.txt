Heian Fuuunden - English translation patch v{version}
=====================================================

Unofficial English fan translation of Heian Fuuunden (Super Famicom, KSS, 1995; Japan only), a strategy RPG of
onmyoji and shikigami in Heian-period Japan.
This zip holds only the patch. No game data is included; you need your own dump of the Japanese cartridge.
Do not ask for or share patched ROMs.

How to apply
------------
1. Get a clean dump of the Japanese game, with no copier header. It must match exactly:
     No-Intro name: Heian Fuuunden (Japan)
     Size:   {o_size} bytes
     CRC32:  {o_crc}
     MD5:    {o_md5}
     SHA-1:  {o_sha1}
2. Apply {patch} with any BPS patcher (Floating IPS / flips, beat, or the web patcher at
   https://www.marcrobledo.com/RomPatcher.js/). The patcher checks the base ROM's CRC and refuses a wrong dump.
3. The patched ROM is 2 MiB (the English text lives in an added 512 KiB):
     Size:   {b_size} bytes
     CRC32:  {b_crc}
     SHA-1:  {b_sha1}

Play from a cold boot: emulator savestates made on the Japanese ROM or an older patch carry the old code and font
in memory and will show garbled text. Use in-game saves instead.
Tested in Mesen (MesenCE build, SNES core).

What is translated
------------------
- Dialogue and story, every ally's epilogue: all of it.
- Menus, items, jutsu, shikigami, squads, provinces and places, battle and system messages: all of it.
- Graphics with text (battle command buttons, status labels, help panels, province cards, game over, the staff roll
  and its end card): redrawn in English. The title logo stays in its Japanese calligraphy; PUSH START and the
  company logos were English already. The game has no name entry.

Style: Western name order; historical names keep their "no" (Abe no Seimei, Taira no Masakado); honorifics are
kept (Seimei-sama, Hiroyuki-dono). Readings follow the game's own furigana, otherwise Hepburn without macrons.

Known issues
------------
- A line that names a unit ("Kagura's turn.") is indented for the widest name it can take, as in the Japanese, so
  short names sit a little left of centre. Cosmetic only.
- Report bugs at https://github.com/minhnhattonthat/heian-fuuunden-en/issues (a savestate helps most).

Credits
-------
Translation, tools and hacking: minhnhattonthat, with extensive AI assistance (Claude by Anthropic). Corrections are very welcome.
Fonts: Pixel Operator and Pixel Operator 8 by Jayvee Enaguas (CC0).
Heian Fuuunden is (c) 1995 KSS. This project is not affiliated with them.
