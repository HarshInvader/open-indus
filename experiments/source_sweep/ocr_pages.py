"""Render/OCR data-only PDFs with installed readers; do not execute attachments."""
import argparse,pathlib,subprocess
import pymupdf
p=argparse.ArgumentParser();p.add_argument('pdf');p.add_argument('source');p.add_argument('pages',help='1-based comma-separated ranges');a=p.parse_args()
root=pathlib.Path(__file__).resolve().parent/'evidence'/a.source;root.mkdir(parents=True,exist_ok=True)
d=pymupdf.open(a.pdf)
nums=[]
for term in a.pages.split(','):
 parts=[int(x) for x in term.split('-')];nums+=list(range(parts[0],parts[-1]+1))
for n in nums:
 out=root/f'p{n:03d}';image=out.with_suffix('.png');txt=out.with_suffix('.txt')
 if txt.exists():continue
 d[n-1].get_pixmap(matrix=pymupdf.Matrix(2,2)).save(image)
 subprocess.run(['tesseract',str(image),str(out)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
 print(n,flush=True)
