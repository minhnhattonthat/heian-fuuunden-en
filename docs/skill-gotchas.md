# Skill gotchas (one line each: reference file, then the fact)

- SKILL.md Step 0: the plugin was enabled in `.claude/settings.json` but neither its skill nor its guard hook loaded in a dispatched (Orca) session; the `sed -i` canary passed until the hooks block was added to the project settings with the stable marketplace path.
- references/platform-snes.md: `lua/probes/snes_romreads.lua` logs one line per distinct (PC, bank), so it hides data streams; a per-(PC, 256-byte page) count (`tools/lua/readhist.lua` here) found the font loop at once. Its offsets also assume LoROM; on HiROM use `addr & 0x3FFFFF`.
- references/pipeline.md §Recon: a hot ROM-read loop during dialogue was the sprite builder, not text; filter histograms by the text banks first.
- references/graphics.md: menu captions here are raw BG3 tilemap words in ROM (`0x20xx`), not strings; searching the ROM for the low bytes of the dumped map row with a wildcard high byte (`54 . 35 . 5E . 58`) found the table when relative search found nothing.
- references/pipeline.md §Recon: system-font matching (MS Gothic, bbox-normalised NCC) identified only ~half of a 16×16 2bpp kanji font; read the sheets by eye.
