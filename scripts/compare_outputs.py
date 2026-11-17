"""Compare outputs regenerated in a scratch copy against the committed repo.

usage: .venv/bin/python scripts/compare_outputs.py WORK_DIR MARK_FILE area [area ...]

Every file under WORK_DIR/experiments/<area>/ newer than MARK_FILE is compared with the same path in
the repo. SAME = byte-identical. For JSON, DIFF lists how many leaves changed and the largest
relative change, with a few example keys. Non-JSON files are reported as identical or not.
"""
import json, os, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def leaves(x, p=''):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from leaves(v, f'{p}.{k}')
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from leaves(v, f'{p}[{i}]')
    else:
        yield p, x


def main():
    work, mark, areas = Path(sys.argv[1]), os.path.getmtime(sys.argv[2]), sys.argv[3:]
    n_same = n_diff = 0
    for a in areas:
        for f in sorted((work / 'experiments' / a).rglob('*')):
            if not f.is_file() or f.stat().st_mtime < mark or '__pycache__' in str(f):
                continue
            rel = f.relative_to(work)
            o = REPO / rel
            if not o.exists():
                print(f'NEW   {rel}')
                continue
            if f.read_bytes() == o.read_bytes():
                print(f'SAME  {rel}'); n_same += 1
                continue
            n_diff += 1
            if f.suffix != '.json':
                print(f'DIFF  {rel} (non-JSON)')
                continue
            try:
                A, B = dict(leaves(json.load(open(o)))), dict(leaves(json.load(open(f))))
            except Exception as e:
                print(f'DIFF  {rel} (unparsable: {e})')
                continue
            diffs = []
            for k in set(A) | set(B):
                x, y = A.get(k), B.get(k)
                if x == y or (isinstance(x, float) and isinstance(y, float) and x != x and y != y):
                    continue
                if isinstance(x, (int, float)) and isinstance(y, (int, float)) and not isinstance(x, bool):
                    diffs.append((abs(x - y) / max(abs(x), abs(y), 1e-300), k, x, y))
                else:
                    diffs.append((float('inf'), k, str(x)[:40], str(y)[:40]))
            diffs.sort(key=lambda d: -d[0])
            print(f'DIFF  {rel}: {len(diffs)} of {len(A)} leaves changed')
            for d in diffs[:6]:
                print('       ', d[1], d[2], '->', d[3])
    print(f'\n{n_same} identical, {n_diff} differ')


if __name__ == '__main__':
    main()
