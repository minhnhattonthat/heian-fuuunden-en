; Heian Fuuunden English patch: engine hooks (asar 1.91, `tools/asar/asar.exe --fix-checksum=off`).
; build.py writes the relocated strings and the pointer table (PTRS) into the expanded ROM first, then runs this.
; Hook list and why: docs/re/hooks.md. Register widths at every hook: M=16, X=16 (checked in the disassembly).
hirom

PTRS = $D80000          ; 0x614 entries x 4 bytes: string address lo16, bank (16-bit), written by build.py
JPFONT = $C1F2F4        ; original glyph-address table (code*2 -> C9:addr)
LINE_PX = 176           ; dialogue line buffer: 22 tiles (0x160 bytes per half-row)
MENU_PX = 128           ; renderer 2: the bottom half-row sits 16 tiles (0x100 bytes) after the top in VRAM
SMALL = $0401           ; {small}: the rest of the string is two 8-px lines (renderer 2; ignored by the dialogue)
SBR = $040A             ; {sbr}: second small line (renderer 2); a space in the dialogue
NARROW = $0402          ; {narrow}: like {small}, in the narrow 8-px font (3-px letters); ignored by the dialogue
; Free WRAM (never written non-zero in 18 warp scenes: tools/lua/wramuse.lua, $7E:1B25-1CFF unused)
PARTY = $7E1CF0         ; 1 while PartyName draws a party-list name
NARROWF = $7E1CF2       ; 1 after {narrow} in the current renderer-2 string (MenuPtr clears it)
PARTY_PX = 40           ; party-list slot: 5 tiles on one 8-px row (tools/gfx_edits.py)
PADPX = $7E1CF4         ; renderer 2: when non-zero, MenuEnd paper-fills whole tiles up to this x (LabelName)
LABEL_PX = 48           ; overworld squad/province label: 6 tiles (the Japanese uploads 4 glyphs x 12 px)

; ---- party list: 8 slots of 5 tiles (was 3), names in the narrow font on one row --------------------------
org $C12C04             ; JSL $C1753B (party panel, all 8 slots)
    jsl PartyName
org $C132AE             ; JSL $C1753B (squad panels)
    jsl PartyName
org $C13327             ; JSL $C1753B (two slots redrawn after an exchange)
    jsl PartyName
org $C12C0D             ; ADC #$0030: buffer step per slot
    dw $0050
org $C132B7
    dw $0050
org $C13360
    dw $0050
org $C1A3CB             ; slot VRAM addresses, panel A ($C1A3DB: panel B = +$200)
    dw $7200,$7228,$7250,$7278,$72A0,$72C8,$72F0,$7318
    dw $7400,$7428,$7450,$7478,$74A0,$74C8,$74F0,$7518

; ---- squad formation screen: the same panels (C8:939E slots 0-3, C8:9450, C8:9506), same 5-tile slots ------
org $C16011             ; JSL $C1753B (one name slot, buffer $7F:0000)
    jsl PartyName
org $C1E6CE             ; slot VRAM addresses: 0-3 panel C8:939E, 4-11 C8:9450, 12-19 C8:9506
    dw $7200,$7228,$7250,$7278
    dw $7400,$7428,$7450,$7478,$74A0,$74C8,$74F0,$7518
    dw $7600,$7628,$7650,$7678,$76A0,$76C8,$76F0,$7718

; ---- string pointers: 24-bit table instead of the C3/C6 16-bit table --------------------------------------
org $C17270             ; LDA $C30000,x / bank select by id (dialogue reader); X = id*2
    jml TextPtr
org $C174F1             ; LDA $C30000,x / LDA #$C3 ({name} reader); X = id*2
    jml NamePtr
org $C1754D             ; LDA $C30000,x / LDA #$C3 (renderer 2, menus); X = id*2
    jml MenuPtr

; ---- numbers: {num} digits drawn with English codes ('0' = $430) --------------------------------------------
org $C17537
    adc #$0430

; ---- glyph draw: codes >= $400 go to the VWF -------------------------------------------------------------
org $C173A5             ; LDA $C1F2F4,x (dialogue glyph lookup); X = code*2
    jml VwfMain
org $C175B8             ; LDA $C1F2F4,x (renderer 2 glyph lookup); X = code*2
    jml VwfMenu
org $C17564             ; renderer 2 upload size from the glyph count -> from the VWF pixel width
    jml MenuEnd

; ---- overworld labels: squad name (VRAM 6B00) and province (6B30), 6 tiles each; pad short English to all 6 ----
org $C14FF3             ; JSL $C1753B (squad label)
    jsl LabelName
org $C15018             ; JSL $C1753B (province label)
    jsl LabelName

org $DF0000
TextPtr:
    txa
    asl
    tax
    lda.l PTRS,x
    sta $00
    lda.l PTRS+2,x
    sta $02
    jml $C1728F

NamePtr:
    txa
    asl
    tax
    lda.l PTRS,x
    sta $04
    lda.l PTRS+2,x
    sta $06
    jml $C174FC

MenuPtr:
    txa
    asl
    tax
    lda.l PTRS,x
    sta $0E
    lda.l PTRS+2,x
    sta $10
    stz $1426           ; VWF pixel x for this string
    lda #$0000
    sta.l NARROWF
    jml $C17558

; Party list: JSL'd instead of C1:753B by the three party-list callers (A = VRAM, [$00] = the slot's buffer).
; Paper over the slot's 5 tiles, then draw with PARTY set: VwfMenu uses the narrow font on the top half-row only
; and MenuEnd uploads exactly those 5 tiles (no bottom half-row: the tilemap shows one row).
PartyName:
    pha
    lda #$FF00
    ldy #$0000
-   sta [$00],y
    iny
    iny
    cpy.w #PARTY_PX*2
    bcc -
    lda #$0001
    sta.l PARTY
    pla
    jsl $C1753B
    lda #$0000
    sta.l PARTY
    rtl

; Z clear (BNE taken) when the 8-px glyphs come from the narrow font.
IsNarrow:
    lda.l PARTY
    ora.l NARROWF
    rts

; A = code*2 (X too). Returns A = glyph index 0..$5E in the English font.
GlyphIndex:
    txa
    lsr
    sec
    sbc #$0420
    bcc .bad
    cmp #$005F
    bcs .bad
    rts
.bad:
    lda #$0000
    rts

; Dialogue: $1422 = byte offset of the current tile in the $7F:A000 buffer, $1426 = pixel x in the line
; (the original used $1426 as the glyph count for its 12-px pairs; every line start zeroes it).
VwfMain:
    cpx #$0800
    bcs .en
    lda.l JPFONT,x
    jml $C173A9
.en:
    cpx.w #SMALL*2              ; {small} / {narrow} (a menu name inserted with {name}): draw nothing
    beq ++
    cpx.w #NARROW*2
    bne +
++  inc $142C
    jml $C17491
+                               ; {sbr} falls through GlyphIndex as a space
    jsr GlyphIndex
    pha                         ; [glyph]
    lda $1426
    lsr
    lsr
    lsr
    asl
    asl
    asl
    asl
    sta $04
    lda $1422
    sec
    sbc $04                     ; line base offset
    pha                         ; [linebase][glyph]
    clc
    adc #$A000
    sta $00
    lda #$007F
    sta $02
    lda $03,s
    tax
    lda.l WIDTHS,x
    and #$00FF
    clc
    adc $1426
    cmp.w #LINE_PX+1
    bcs .skip                   ; past the line end: drop the glyph (the lint keeps lines inside)
    lda #$0160
    sta $04
    lda $03,s
    jsr VwfDraw
.skip:
    pla
    sta $04                     ; line base offset
    pla
    lda $1426
    lsr
    lsr
    lsr
    asl
    asl
    asl
    asl
    clc
    adc $04
    sta $1422
    inc $142C
    jml $C17491                 ; upload the line buffer, RTL

; Renderer 2 (menus): buffer at [$20], bottom half-row +$400, one call draws the whole string.
VwfMenu:
    cpx #$0800
    bcs .en
    lda.l JPFONT,x
    jml $C175BC
.en:
    lda $20
    sta $00
    lda $22
    sta $02
    lda.l PARTY
    beq +
    jmp .party
+   cpx.w #SMALL*2
    beq .small
    cpx.w #NARROW*2
    beq .narrow
    cpx.w #SBR*2
    beq .sbr
    lda $1426
    bpl +
    jmp .smallglyph
+   jsr GlyphIndex
    pha
    lda $20
    sta $00
    lda $22
    sta $02
    lda $01,s
    tax
    lda.l WIDTHS,x
    and #$00FF
    clc
    adc $1426
    cmp.w #MENU_PX+1
    bcs .skip
    lda #$0400
    sta $04
    lda $01,s
    jsr VwfDraw
.skip:
    pla
    lda $1426
    lsr
    lsr
    lsr
    asl
    asl
    asl
    asl
    sta $1422
    inc $142C
    jml $C17558

; Small mode: {small} first, then line 1, {sbr}, line 2 in the 8-px font: line 1 in the top half-row, line 2 in
; the bottom one, so a 6-tile field holds two 48-px lines. $1426 = $8000 | x (line 1),
; $C000 | (line-1 width << 8) | x (line 2). {narrow} starts the same mode with the narrow font (NARROWF).
.narrow:
    lda #$0001
    sta.l NARROWF
.small:
    lda #$FF00                  ; paper on both half-rows, 16 tiles each (no stale pixels under short lines)
    ldy #$0000
-   sta [$00],y
    iny
    iny
    cpy #$0100
    bcc -
    ldy #$0400
-   sta [$00],y
    iny
    iny
    cpy #$0500
    bcc -
    lda #$8000
    sta $1426
    inc $142C
    jml $C17558
.sbr:
    lda $1426
    and #$00FF
    xba
    ora #$C000
    sta $1426
    inc $142C
    jml $C17558
.smallglyph:
    pha                         ; [flags]
    and #$00FF
    sta $1426                   ; plain x for VwfDraw8
    lda $01,s
    and #$4000
    beq +
    lda #$0400
+
    sta $04                     ; line 2 -> bottom half-row
    jsr GlyphIndex
    jsr VwfDraw8
    pla
    and #$FF00
    ora $1426
    sta $1426
    inc $142C
    jml $C17558

; Party list (PartyName): narrow font, top half-row only, glyphs past PARTY_PX dropped; control codes draw nothing.
.party:
    cpx.w #$0420*2
    bcc .ctl
    jsr GlyphIndex
    pha
    tax
    jsr Width8
    clc
    adc $1426
    cmp.w #PARTY_PX+2           ; advance includes the 1-px gap after the last glyph
    bcs +
    stz $04                     ; top half-row
    lda $01,s
    jsr VwfDraw8
+   pla
.ctl:
    inc $142C
    jml $C17558

MenuEnd:
    lda.l PARTY
    bne .party
    lda $1426
    beq .jp
    bpl .big
    xba                         ; small: upload the wider of the two lines
    and #$003F
    sta $04
    lda $1426
    and #$00FF
    cmp $04
    bcs .big
    lda $04
.big:
    jsr PadLabel
    clc
    adc #$0007
    lsr
    lsr
    lsr
    asl
    asl
    asl
    asl
    sta $04                     ; bytes per half-row = tiles used * 16
    stz $1426
    jml $C17581
.jp:                            ; untouched original (Japanese string)
    lda $142C
    lsr
    sta $00
    lda #$0030
    sta $02
    jsl $C10A38
    lda $142C
    lsr
    bcc +
    lda $04
    clc
    adc #$0020
    sta $04
+
    jml $C17581
.party:                         ; C1:7581 without its bottom half-row DMA: the slot's 5 top tiles only
    lda.w #PARTY_PX*2
    sta $06
    lda $0C
    sta $00
    lda $20
    sta $02
    lda $22
    sta $04
    jsl $C100C6
    lda #$0000
    sta $142C
    sta $1422
    stz $1416
    stz $1426
    rtl

; Overworld labels (C1:4FF3 squad, C1:5018 province): renderer 2 with PADPX = LABEL_PX, so MenuEnd fills and
; uploads all 6 tiles. Without it a short name ("Kii") uploads 2 tiles and the rest of the label shows stale tiles
; from an earlier string or a see-through hole (phase 8, scene overworld / battle_win_overworld).
LabelName:
    pha
    lda.w #LABEL_PX
    sta.l PADPX
    pla
    jsl $C1753B
    lda #$0000
    sta.l PADPX
    rtl

; MenuEnd helper: A = drawn px -> A = px to upload. With PADPX set and wider than the text, draws a space at the
; left edge of every whole tile from the text's end to PADPX: a glyph at s = 0 stores its tile (both half-rows),
; so each is paper over stale pixels.
PadLabel:
    pha
    lda.l PADPX
    beq .keep
    cmp $01,s
    beq .keep
    bcc .keep
    lda $01,s
    clc
    adc #$0007
    and #$FFF8
.tile:
    cmp.l PADPX
    bcs .done
    sta $1426
    lda $20
    sta $00
    lda $22
    sta $02
    lda #$0400
    sta $04
    lda #$0000                  ; glyph 0 = space (code $420)
    jsr VwfDraw
    lda $1426
    clc
    adc #$0007
    and #$FFF8
    bra .tile
.done:
    pla
    lda.l PADPX
    rts
.keep:
    pla
    rts

; Draw English glyph A at pixel x = $1426 into the line at [$00] (tile 0, top half); $04 = offset of the bottom
; half-row. Ink = colour 3 (bp0 set), paper = colour 2 (bp1 set). Then $1426 += advance.
; A tile is first written either by a glyph starting at its left edge (s = 0, stored) or by a glyph spilling into
; it (stored); later glyphs OR into it. So stale pixels from an earlier string never survive.
; DP: $00-$02 pointer, $04 bottom offset, $06 = s (x & 7), $07 = 1 if the glyph spills into the next tile.
VwfDraw:
    pha                         ; [glyph]
    tax
    lda.l WIDTHS,x
    jsr VwfSetup
    lda $01,s
    asl
    asl
    asl
    asl
    tax                         ; X = glyph * 16 (font rows)
    phy
    jsr VwfRows8
    pla
    clc
    adc $04
    tay
    jsr VwfRows8
    pla
    tax
    lda.l WIDTHS,x
    and #$00FF
    clc
    adc $1426
    sta $1426
    rts

; Same for the 8-px font: one 8-row pass into the half-row at [$00] + $04.
; Font: FONT8 (Pixel Operator 8) or FONTN when IsNarrow.
VwfDraw8:
    pha                         ; [glyph]
    tax
    jsr Width8
    jsr VwfSetup
    tya
    clc
    adc $04
    tay
    lda $01,s
    asl
    asl
    asl
    pha
    jsr IsNarrow
    beq +
    pla
    clc
    adc.w #FONTN-FONT
    bra ++
+   pla
    clc
    adc.w #FONT8-FONT
++  tax                         ; X = $600 (or $900) + glyph * 8
    jsr VwfRows8
    pla
    tax
    jsr Width8
    clc
    adc $1426
    sta $1426
    rts

; X = glyph -> A = its 8-px advance (narrow font when IsNarrow). Keeps X.
Width8:
    jsr IsNarrow
    beq +
    lda.l WIDTHSN,x
    and #$00FF
    rts
+   lda.l WIDTHS8,x
    and #$00FF
    rts

; A = glyph width (low byte). Sets $06 = s (x & 7), $07 = 1 if the glyph spills into the next tile;
; returns Y = tile offset of x in the half-row.
VwfSetup:
    and #$00FF
    sta $06
    lda $1426
    and #$0007
    clc
    adc $06                     ; s + w
    cmp #$0009
    lda #$0000
    rol                         ; 1 if s + w > 8
    xba
    sta $06
    lda $1426
    and #$0007
    ora $06
    sta $06                     ; $06 = s, $07 = spill
    lda $1426
    lsr
    lsr
    lsr
    asl
    asl
    asl
    asl
    tay
    rts

VwfRows8:                       ; 8 rows from FONT+X, to [$00],y (Y += 2 per row)
    lda.l FONT,x
    and #$00FF
    xba                         ; g << 8
    phx
    pha
    lda $06
    and #$00FF
    tax
    pla
    cpx #$0000
    beq .noshift
.shift:
    lsr
    dex
    bne .shift
.noshift:
    pha                         ; [right byte | left byte << 8]
    xba
    and #$00FF
    ora #$FF00
    tax                         ; X = new word for the left tile
    lda $06
    and #$00FF
    beq .store
    txa
    ora [$00],y
    tax
.store:
    txa
    sta [$00],y
    lda $07
    and #$00FF
    beq .noright
    tya
    clc
    adc #$0010
    tay
    lda $01,s
    and #$00FF
    ora #$FF00
    sta [$00],y
    tya
    sec
    sbc #$0010
    tay
.noright:
    pla
    plx
    iny
    iny
    inx
    txa
    and #$0007
    bne VwfRows8
    rts

FONT:
    incbin "../build/gen/font_en.bin"
FONT8:                          ; must follow FONT: VwfRows8 reads FONT+X with X = FONT8-FONT + glyph*8
    incbin "../build/gen/font_en8.bin"
FONTN:                          ; narrow 8-px font, same layout (tools/font_narrow.py)
    incbin "../build/gen/font_enn.bin"
WIDTHS:
    incbin "../build/gen/font_en_w.bin"
WIDTHS8:
    incbin "../build/gen/font_en8_w.bin"
WIDTHSN:
    incbin "../build/gen/font_enn_w.bin"
warnpc $DF8000
