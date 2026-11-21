"""Dialogue table banks (docs/re/text.md): unpack to a layout list, pack back.

The table at C3:0000 holds 0x614 16-bit pointers; an id's bank is C3 or C6 (`bank_of`). Strings are 16-bit LE
words ended by 0xFF or 0xFB, stored back to back. Some ids share one string. Id 0x4FF is a dummy pointing at a zero
run that reaches the bank end with no terminator.

A bank's layout is a list of items in address order, each either
    {"ids": [..], "words": [..]}   a string (terminator included) and every id that points at it
    {"raw": "hex"}                 bytes no pointer reaches (kept as they are)
`pack_bank` writes the items back to back from the bank's first string and returns the pointer for every id, so
unpack -> pack is the identity (tests/test_identity.py).
"""
import struct

TABLE = 0x30000
COUNT = 0x614
BANKS = {"C3": (0x30000, 0x30000 + 2 * COUNT), "C6": (0x60000, 0x60000)}  # file base, first string
ENDS = (0xFF, 0xFB)


def bank_of(i):
    x = i * 2
    return "C6" if x >= 0xA00 or 0x600 <= x < 0x800 else "C3"


def pointers(rom):
    return list(struct.unpack_from("<%dH" % COUNT, rom, TABLE))


def read_words(rom, base, ptr):
    out, j = [], ptr
    while j < 0x10000:
        w = rom[base + j] | rom[base + j + 1] << 8
        out.append(w)
        j += 2
        if w in ENDS:
            break
    return out


def unpack(rom):
    """{bank: [items]} for C3 and C6."""
    ptrs = pointers(rom)
    layout = {}
    for name, (base, first) in BANKS.items():
        by_ptr = {}
        for i, p in enumerate(ptrs):
            if bank_of(i) == name:
                by_ptr.setdefault(p, []).append(i)
        items, pos = [], first - base
        for p in sorted(by_ptr):
            if p < pos:
                raise ValueError("%s: pointer 0x%04X inside the previous string" % (name, p))
            if p > pos:
                items.append({"raw": rom[base + pos:base + p].hex()})
            words = read_words(rom, base, p)
            items.append({"ids": by_ptr[p], "words": words})
            pos = p + 2 * len(words)
        if pos < 0x10000:
            items.append({"raw": rom[base + pos:base + 0x10000].hex()})
        layout[name] = items
    return layout


def pack_bank(name, items):
    """(bytes from the bank's first string to the bank end, {id: pointer})."""
    base, first = BANKS[name]
    buf, ptrs = bytearray(), {}
    for it in items:
        if "raw" in it:
            buf += bytes.fromhex(it["raw"])
            continue
        p = first - base + len(buf)
        for i in it["ids"]:
            ptrs[i] = p
        buf += b"".join(struct.pack("<H", w) for w in it["words"])
    if first - base + len(buf) > 0x10000:
        raise ValueError("%s overflows by %d bytes" % (name, first - base + len(buf) - 0x10000))
    return bytes(buf), ptrs


def pack(rom, layout):
    """Write both banks and the pointer table into a copy of rom."""
    out = bytearray(rom)
    table = pointers(rom)
    seen = set()
    for name, items in layout.items():
        base, first = BANKS[name]
        data, ptrs = pack_bank(name, items)
        out[first:first + len(data)] = data
        for i, p in ptrs.items():
            if bank_of(i) != name:
                raise ValueError("id 0x%X belongs in %s, not %s" % (i, bank_of(i), name))
            table[i] = p
            seen.add(i)
    missing = set(range(COUNT)) - seen
    if missing:
        raise ValueError("ids with no string: %s" % sorted(missing)[:10])
    struct.pack_into("<%dH" % COUNT, out, TABLE, *table)
    return bytes(out)
