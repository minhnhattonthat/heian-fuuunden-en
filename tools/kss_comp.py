"""Heian Fuuunden graphics/tilemap codec (the decompressor at C1:05CF).

A block starts with a type byte, then a 16-bit little-endian output size:
  type 0  raw: `size` bytes copied as words (C1:0724)
  type 1  LZ (C1:05E6): 16-bit flag words, LSB first. Flag word 0 with >=16 bytes left = 16 literals.
          bit 0 -> one literal byte; bit 1 -> word w: offset = w & 0x7FF, length = (w >> 11) + 3,
          copy from out[pos - offset - 1].
  type 2  word RLE (C1:074F): if size is odd one extra byte follows (the last output byte). Then command bytes
          c until the output is full: c>>6 = 0 literal words (n+1), 1 repeat one word (n+2), 2 incrementing
          word (n+2), 3 decrementing word (n+2), n = c & 0x3F.

    python -X utf8 tools/kss_comp.py ROM OFFSET [OUT.bin]   (decode one block; prints type, sizes)
"""
import struct
import sys


class Bad(Exception):
    pass


def decode(data, off, limit=0x10000):
    """Return (output bytes, compressed length). Raises Bad on a stream the game could not have meant."""
    typ = data[off]
    if typ > 2:
        raise Bad("type %d" % typ)
    if off + 3 > len(data):
        raise Bad("truncated")
    size = struct.unpack_from("<H", data, off + 1)[0]
    if size == 0 or size > limit:
        raise Bad("size %d" % size)
    p = off + 3
    out = bytearray()
    if typ == 0:
        out += data[p:p + size]
        if len(out) < size:
            raise Bad("short")
        return bytes(out), 3 + size
    if typ == 1:
        while len(out) < size:
            flags = data[p] | data[p + 1] << 8
            p += 2
            if flags == 0 and size - len(out) >= 16:
                out += data[p:p + 16]
                p += 16
                continue
            for _ in range(16):
                if flags & 1:
                    w = data[p] | data[p + 1] << 8
                    p += 2
                    ofs, n = (w & 0x7FF) + 1, (w >> 11) + 3
                    if ofs > len(out):
                        raise Bad("offset before start at 0x%X" % p)
                    for _ in range(n):
                        out.append(out[-ofs])
                else:
                    out.append(data[p])
                    p += 1
                flags >>= 1
                if len(out) >= size:
                    break
        if len(out) > size + 34:
            raise Bad("overrun")
        return bytes(out[:size]), p - off
    # type 2
    last = None
    if size & 1:
        last = data[p]
        p += 1
    words = []
    want = size // 2
    while len(words) < want:
        c = data[p]
        p += 1
        mode, n = c >> 6, c & 0x3F
        if mode == 0:
            for _ in range(n + 1):
                words.append(data[p] | data[p + 1] << 8)
                p += 2
        else:
            w = data[p] | data[p + 1] << 8
            p += 2
            for _ in range(n + 2):
                words.append(w)
                w = (w + (1 if mode == 2 else -1 if mode == 3 else 0)) & 0xFFFF
    if len(words) != want:
        raise Bad("overrun %d/%d" % (len(words), want))
    out = bytearray(b"".join(struct.pack("<H", w) for w in words))
    if last is not None:
        out.append(last)
    return bytes(out), p - off


def main(argv):
    rom = open(argv[1], "rb").read()
    off = int(argv[2], 16)
    out, n = decode(rom, off)
    print("type %d at 0x%X: %d -> %d bytes, ends 0x%X" % (rom[off], off, n, len(out), off + n))
    if len(argv) > 3:
        open(argv[3], "wb").write(out)


if __name__ == "__main__":
    main(sys.argv)
