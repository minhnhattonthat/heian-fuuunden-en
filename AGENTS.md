# Heian Fuuunden (SNES) English translation

Skill: translate-retro-game (Claude Code: plugin, enabled in .claude/settings.json; other agents: `<SKILL_DIR>/SKILL.md`; `$SKILL` = the directory holding its SKILL.md, printed by `python tools/skill.py`). Read it before ROM, text or QA work.

## Commands (run from repo root)
- Build:    `python -X utf8 build.py` -> build/heian_en.sfc (checks the dump against `rom.sha1` first); `build.py identity [--recompress]` = unpack to `work/unpack/`, repack, compare (must say IDENTICAL)
- Check:    `python -X utf8 tools/check.py`  (tests + lint; the pre-commit hook runs this; `git config core.hooksPath tools/hooks` once per clone)
- Smoke:    `python -X utf8 $SKILL/scripts/emu.py build/heian_en.sfc --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Warp:     `python -X utf8 tools/debug/warp_all.py [--rom F] [--only a,b]` (cold boot -> each scene in `tools/debug/scenes.tsv`, shots in `work/qa/warp/<scene>/`, states regenerated in `work/states/`; ~3 s per scene). One scene by hand: `emu.py ROM --out DIR --script tools/debug/warp.lua --var "SCENE='<name>'" --frames 9000`. Save editor: `tools/debug/save.py` (`docs/re/save.md`). God mode in battle: add `--script tools/lua/god.lua`. Never ask the user to play to a scene.
- Release:  `python -X utf8 tools/release.py` (patch + verify; never publish without the user; phase 9)
- Clean:    `python -X utf8 tools/clean.py` (published projects: lists rebuildable/downloadable files; `--yes` deletes)

## Paths
- Original ROM: `rom/Heian Fuuunden (Japan).sfc` (gitignored; SHA-1 in `rom.sha1`, checked by `tools/check_rom.py`). HiROM+FastROM, 1.5 MB, SRAM.
- Emulator: this repo's own MesenCE QA fork in `tools/mesen/` (release `qa-1`, https://github.com/minhnhattonthat/MesenCE/releases/download/qa-1/Mesen_qa-1_Windows.zip; gitignored; `python -X utf8 $SKILL/scripts/fetch_emu.py mesen` restores it; settings in `tools/emu-config/`). Savestates: `work/states/`.
- Text: `script/` (TSV). Tables: `tbl/`. Glossary: `glossary.md`. RE notes index: `docs/re/README.md`. Fonts and their licences: `docs/fonts.md`. Lua probes: `tools/lua/`.

## Rulings
- Edit source files (.py .lua .asm .tbl .json) only with the file-edit tool; scripts here read and analyse, never `.replace()` and write back.
- Subagents: dispatch the agent types (translator, reviewer, visual-qa, playtester, graphics) shipped by the plugin as `translate-retro-game:<type>` (Claude Code), `.codex/agents/` (Codex) or `.opencode/agents/` (opencode), never general-purpose: their short tool list cuts each agent's start-up context from ~43k to ~9k tokens.
- The user's decisions, with the options and reasons: `docs/decisions.md`. Read it before asking the user anything; add each new ruling there the same session.
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update `docs/status.md`.
- The guard hook is wired in `.claude/settings.json` by its stable marketplace path (the plugin's own hook did not load in the first session).
- Gotchas met while working: `docs/skill-gotchas.md`.

## Status
`docs/status.md`: done, next, open bugs. Update it at the end of every session.
