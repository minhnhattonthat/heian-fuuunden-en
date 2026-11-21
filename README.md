# Heian Fuuunden English translation

Unofficial English fan translation of **Heian Fuuunden** (平安風雲伝; Super Famicom, KSS, 1995): the source text and
tools that build the patch.

**Just want to play?** Download the patch from [Releases](../../releases) and follow its README. This repository holds
no game data you can play; you need your own dump of the Japanese game.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## Translation status

| Part | Status |
|---|---|
| Dialogue / story, epilogues | Translated (every line, 1556 strings) |
| Menus, items, jutsu, shikigami, provinces, battle and system messages | Translated |
| Graphics with text (battle commands, status labels, help panels, chapter and province cards, game over) | Translated |
| Title logo 平安風雲伝 | Left in Japanese (no official English logo exists); PUSH START and the company logos were English already |
| Name entry | None in this game |
| Staff roll | Translated |

Known issues: see [Issues](../../issues). A line that names a unit (e.g. "Kagura's turn.") is indented for the
widest name it can take, as in the Japanese, so short names sit left of centre.

## What's here

| Path | What it is |
|---|---|
| `script/` | Every text block: original Japanese and English. Translation fixes go here. |
| `glossary.md` | Binding names, terms and style rules. |
| `tools/` | Python build chain: extract, insert, lint, release. |
| `tests/` | pytest suite (ROM-dependent tests skip when the ROM is absent). |
| `docs/re/` | Reverse-engineering notes. |
| `docs/decisions.md`, `docs/status.md` | Rulings with their reasons; current progress and open bugs. |
| `docs/fonts.md` | Fonts used and their licences. |
| `AGENTS.md` | Instructions for coding agents (`CLAUDE.md` points to it). |
| `.codex/agents/`, `.opencode/agents/` | Subagent types (translator, reviewer, visual QA, playtester, graphics) for Codex and opencode; Claude Code gets them from the plugin. |

## Build your own patched ROM

Needs Python 3.12+, [asar](https://github.com/RPGHacker/asar) 1.91 in `tools/asar/`, and your own dump of the
Japanese game.

```sh
git clone https://github.com/minhnhattonthat/heian-fuuunden-en
cd heian-fuuunden-en
# copy your dump to: rom/Heian Fuuunden (Japan).sfc
#   (1572864 bytes, no header; CRC32 4640D1A2, MD5 1d00c833f280c50e3e015f45b9bde75f,
#    SHA-1 3b0ca4a24a02c683f8ad140242f6dff96d0d8339; the build refuses any other dump, see rom.sha1)
python -X utf8 build.py                                # -> build/heian_en.sfc
python -X utf8 tools/check.py                          # tests + text lint
python -X utf8 tools/release.py                        # every release gate, then release/Heian_Fuuunden_EN_v1.0.zip
```

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

## Licence

Tools and English translation: MIT. The original Japanese text in `script/` is KSS's and is included only so
the translation can be checked against it. Heian Fuuunden is (c) 1995 KSS; this project is not affiliated with them.
Fonts: Pixel Operator and Pixel Operator 8 by Jayvee Enaguas (CC0), see `docs/fonts.md`.
Do not share patched ROMs.

The translation was made with extensive AI assistance (Claude by Anthropic). Corrections are very welcome.
