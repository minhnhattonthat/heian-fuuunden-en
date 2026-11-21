"""Review pairs per batch: `>> id | JP` / `EN` lines, ids from work/tl/<batch>.tsv, English from script/*.tsv.

usage: python -X utf8 tools/pairs.py b001 [b002 ...] [--out DIR]   (default: print to stdout)
Breaks are shown as ' / ' (line) and ' // ' (page) so each entry stays on two lines.
"""
import argparse
import csv
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = os.path.join(ROOT, 'work', 'tl')


def _rows(path):
    with open(path, encoding='utf-8', newline='') as f:
        return list(csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE))


def _flat(s):
    return s.replace('{page}', ' // ').replace('{br}', ' / ')


def _script_en():
    """English as merged into script/*.tsv (the truth; .out.tsv files go stale after renames)."""
    en = {}
    sdir = os.path.join(ROOT, 'script')
    for name in sorted(os.listdir(sdir)):
        if name.endswith('.tsv'):
            rows = _rows(os.path.join(sdir, name))
            col = rows[0].index('en')
            for r in rows[1:]:
                if len(r) > col:
                    en[r[0]] = r[col]
    return en


def pairs(batch, en=None):
    src = _rows(os.path.join(TL, batch + '.tsv'))
    out = en if en is not None else _script_en()
    lines = []
    for r in src:
        if not r or r[0] == 'id':
            continue
        lines.append('>> %s | %s' % (r[0], _flat(r[-1])))
        lines.append('   %s' % _flat(out.get(r[0], '<missing>')))
    return '\n'.join(lines) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('batches', nargs='+')
    ap.add_argument('--out')
    a = ap.parse_args()
    en = _script_en()
    for b in a.batches:
        text = pairs(b, en)
        if a.out:
            os.makedirs(a.out, exist_ok=True)
            with open(os.path.join(a.out, b + '.txt'), 'w', encoding='utf-8', newline='\n') as f:
                f.write(text)
        else:
            sys.stdout.write(text)


if __name__ == '__main__':
    main()
