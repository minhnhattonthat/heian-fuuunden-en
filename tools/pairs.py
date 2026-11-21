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


# Story-pass chapters (phase 9): id ranges in story order. The game is open (provinces in any order), so a chapter
# is one stretch of the script as the translators batched it; ids below 112 are names/items, not story.
CHAPTERS = [
    ('01_opening', ['112-13B', '290-2A4']),
    ('02_kumano', ['400-435']),
    ('03_briefings', ['436-486']),
    ('04_recruits_a', ['487-4BC']),
    ('05_recruits_b', ['4BD-4FF', '300-328']),
    ('06_shitennoji_abeno', ['329-374']),
    ('07_kyoto', ['375-3B4']),
    ('08_palace_kishi', ['3B5-3EF']),
    ('09_provinces', ['3F0-3FF', '500-544']),
    ('10_doubles_shikoku', ['545-56C']),
    ('11_west', ['56D-596']),
    ('12_endgame', ['597-5B2']),
    ('13_doma_akoya', ['5B3-5FF']),
    ('14_finale', ['600-613']),
    ('15_epilogues', ['2A5-2FF']),
    ('16_battle_system', ['13C-28F']),
]


def _script_jp():
    jp = {}
    sdir = os.path.join(ROOT, 'script')
    for name in ('C3.tsv', 'C6.tsv'):
        rows = _rows(os.path.join(sdir, name))
        col = rows[0].index('jp')
        for r in rows[1:]:
            if len(r) > col and '+' not in r[0]:
                jp[r[0]] = r[col]
    return jp


def chapters(outdir):
    """Write one `>> id | JP` / `EN` file per chapter; return ids that are in no chapter (text only)."""
    jp, en = _script_jp(), _script_en()
    seen = set()
    os.makedirs(outdir, exist_ok=True)
    for name, ranges in CHAPTERS:
        lines = []
        for rg in ranges:
            lo, hi = (int(x, 16) for x in rg.split('-'))
            for i in range(lo, hi + 1):
                k = '%03X' % i
                if k in jp and jp[k].strip('　 '):
                    seen.add(k)
                    lines.append('>> %s | %s' % (k, _flat(jp[k])))
                    lines.append('   %s' % _flat(en.get(k, '<missing>')))
        with open(os.path.join(outdir, name + '.txt'), 'w', encoding='utf-8', newline='\n') as f:
            f.write('\n'.join(lines) + '\n')
    return sorted(k for k in jp if int(k, 16) >= 0x112 and k not in seen and jp[k].strip('　 '))


def main():
    if '--chapters' in sys.argv:
        ap = argparse.ArgumentParser()
        ap.add_argument('--chapters', required=True, metavar='OUTDIR')
        a = ap.parse_args()
        left = chapters(a.chapters)
        if left:
            sys.exit('ids in no chapter: ' + ' '.join(left))
        return
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
