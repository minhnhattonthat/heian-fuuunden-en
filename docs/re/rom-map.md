# ROM map and free space

File `rom/Heian Fuuunden (Japan).sfc`, 0x180000 bytes (1.5 MB), HiROM (`addr & 0x3FFFFF`), FastROM, header at
`0xFFC0`: title ﾍｲｱﾝﾌｳｳﾝﾃﾞﾝ (half-width katakana), map `$31`, type `$02` (ROM+RAM+battery), size `$0B` (2 MB),
checksum `$F5A2` / complement `$0A5D`. Developer KSS (copyright 1995 KSS; font cells also name NATSUME / TEAM 3D).

| File range | Contents | State |
|---|---|---|
| 0x010000-0x01FFFF (C1) | text engine (`C1:7270` reader, `C1:73C1` glyph copy), sprite builder `C1:6E70`, menu caption table `C1:9E7F` | verified |
| 0x020000-0x02FFFF (C2) | sprite/OAM tables (read by `C1:6EF5` etc.) | guess |
| 0x030000-0x03FFFF (C3) | dialogue pointer table + strings (full) | verified |
| 0x060000-0x06FFFF (C6) | dialogue strings (full to 0x6FFA4) | verified |
| 0x090000-0x09F3FF (C9) | dialogue font, 16×16 2bpp, 64 B/glyph, 0x3D0 glyphs | verified |
| 0x050000 (C5) | sound driver interface (`C5:4EA2` writes APU ports) | verified |

## Free space
- No 0xFF fill anywhere. Zero runs ≥ 0x200 (candidates only, not proven free): `0x07D86`(0x27A), `0x0F25C`(0xD54),
  `0x1FAF4`(0x50C), `0x2EACA`(0x1536), `0x3F865`(0x79B, inside C3 strings: not free), `0x4DE54`(0x21AC),
  `0x8F9E4`(0x61D), `0xBFA26`(0x5E0), `0xDFEF8`(0x290), `0x16F476`(0xB8A), `0x17FA77`(0x589).
- **Planned:** extend the file to 2 MB (0x180000-0x1FFFFF, banks `$D8-$DF` / `$58-$5F`), which the header size byte
  already declares, for relocated English text and the VWF font. 4 MB (`$0C`) if 512 KB is not enough.
