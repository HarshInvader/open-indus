import sys, pickle, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from djvu_rows import pages, page_text
src = sys.argv[1]; pat = sys.argv[2].lower()
cache = os.path.join(os.path.dirname(os.path.abspath(__file__)), "work", os.path.basename(os.path.dirname(src)) + ".pkl")
os.makedirs(os.path.dirname(cache), exist_ok=True)
if os.path.exists(cache): P = pickle.load(open(cache, "rb"))
else:
    P = pages(src); pickle.dump(P, open(cache, "wb"))
print(len(P), "leaves")
print([i for i, p in enumerate(P) if pat in page_text(p).lower()])
