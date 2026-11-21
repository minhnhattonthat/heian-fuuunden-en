# Skill gotchas (one line each: reference file, then the fact)

- SKILL.md Step 0: the plugin was enabled in `.claude/settings.json` but neither its skill nor its guard hook loaded in a dispatched (Orca) session; the `sed -i` canary passed until the hooks block was added to the project settings with the stable marketplace path.
- references/platform-snes.md: `lua/probes/snes_romreads.lua` logs one line per distinct (PC, bank), so it hides data streams; a per-(PC, 256-byte page) count (`tools/lua/readhist.lua` here) found the font loop at once. Its offsets also assume LoROM; on HiROM use `addr & 0x3FFFFF`.
- references/pipeline.md §Recon: a hot ROM-read loop during dialogue was the sprite builder, not text; filter histograms by the text banks first.
- references/graphics.md: menu captions here are raw BG3 tilemap words in ROM (`0x20xx`), not strings; searching the ROM for the low bytes of the dumped map row with a wildcard high byte (`54 . 35 . 5E . 58`) found the table when relative search found nothing.
- references/graphics.md §Survey: blocks stored back to back let a chain walker (decode, jump to the end, decode again; keep chains of ≥5) enumerate every compressed block without a pointer table; chains of 3 were noise in text and code banks.
- SKILL.md ground rules: with context-mode active, Bash output over ~4 KB and Read of files over ~4 KB come back as a stub; write to a file and Read with offset/limit, or filter in Python first.
- references/pipeline.md §Recon: system-font matching (MS Gothic, bbox-normalised NCC) identified only ~half of a 16×16 2bpp kanji font; read the sheets by eye.
- references/emulator-qa.md §emu.py: `STATE_OUT` is a driver global, so a `--var STATE_OUT=` for a warp script is rejected ("use NAME=LUA with a non-driver global name"); name the warp's own savestate var something else (`WARP_STATE` here).
- references/emulator-qa.md §Hooks: Mesen's Lua working folder was not `tools/mesen` here (`../debug/scenes.tsv` failed to open); derive repo paths from `OUT` or pass them absolute.
- references/emulator-qa.md §Debug tool: this game keeps its live state in SRAM and New Game writes slot 1 at once, so a warp = New Game -> edit slot 1 + checksum in Lua -> soft reset -> Continue; ~3 s per scene, no playthrough.
- scripts/dis65816.py: defaults to LoROM and prints nothing at all (exit 0) for a HiROM address like C0CB90; pass `--map hirom` (an empty-output warning would help).
- references/emulator-qa.md §Debug tool: a strategy-RPG battle here has its own state word (`$38`) under mode 7; route waits on the mode alone fired during the intro, before the player turn. Wait on the battle state word too (warp.lua `wait MM.SS.TT`).
