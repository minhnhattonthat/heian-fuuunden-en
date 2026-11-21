; Heian Fuuunden English patch: engine hooks (asar 1.91, `tools/asar/asar.exe --fix-checksum=off`).
; build.py writes the relocated strings and the pointer table (PTRS) into the expanded ROM first, then runs this.
; Hook list and why: docs/re/hooks.md. Register widths at every hook: M=16, X=16 (checked in the disassembly).
hirom

PTRS = $D80000          ; 0x614 entries x 4 bytes: string address lo16, bank (16-bit), written by build.py
JPFONT = $C1F2F4        ; original glyph-address table (code*2 -> C9:addr)
LINE_PX = 176           ; dialogue line buffer: 22 tiles (0x160 bytes per half-row)
MENU_PX = 128           ; renderer 2: the bottom half-row sits 16 tiles (0x100 bytes) after the top in VRAM

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
    jml $C17558

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
    jsr GlyphIndex
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

MenuEnd:
    lda $1426
    beq .jp
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

; Draw English glyph A at pixel x = $1426 into the line at [$00] (tile 0, top half); $04 = offset of the bottom
; half-row. Ink = colour 3 (bp0 set), paper = colour 2 (bp1 set). Then $1426 += advance.
; A tile is first written either by a glyph starting at its left edge (s = 0, stored) or by a glyph spilling into
; it (stored); later glyphs OR into it. So stale pixels from an earlier string never survive.
; DP: $00-$02 pointer, $04 bottom offset, $06 = s (x & 7), $07 = 1 if the glyph spills into the next tile.
VwfDraw:
    pha                         ; [glyph]
    tax
    lda.l WIDTHS,x
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
    lda $01,s
    asl
    asl
    asl
    asl
    tax                         ; X = glyph * 16 (font rows)
    lda $1426
    lsr
    lsr
    lsr
    asl
    asl
    asl
    asl
    tay                         ; Y = tile offset in the half-row
    phy
    jsr .rows8
    pla
    clc
    adc $04
    tay
    jsr .rows8
    pla
    tax
    lda.l WIDTHS,x
    and #$00FF
    clc
    adc $1426
    sta $1426
    rts

.rows8:                         ; 8 rows from X, to [$00],y (Y += 2 per row)
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
    beq ..noshift
..shift:
    lsr
    dex
    bne ..shift
..noshift:
    pha                         ; [right byte | left byte << 8]
    xba
    and #$00FF
    ora #$FF00
    tax                         ; X = new word for the left tile
    lda $06
    and #$00FF
    beq ..store
    txa
    ora [$00],y
    tax
..store:
    txa
    sta [$00],y
    lda $07
    and #$00FF
    beq ..noright
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
..noright:
    pla
    plx
    iny
    iny
    inx
    txa
    and #$0007
    bne .rows8
    rts

FONT:
    incbin "../build/gen/font_en.bin"
WIDTHS:
    incbin "../build/gen/font_en_w.bin"
warnpc $DF8000
