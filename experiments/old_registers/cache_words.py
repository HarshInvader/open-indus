import sys, os, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from djvu_rows import page_words
for src in sys.argv[1:]:
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "work", os.path.basename(os.path.dirname(src)) + ".words.pkl")
    pickle.dump(page_words(src), open(out, "wb")); print(out)
