"""Make viewing slices: python3 tools/sheet.py <png> [maxh] -> /tmp/qa/view/<name>-N.png"""
import sys, os
from PIL import Image
p = sys.argv[1]; maxh = int(sys.argv[2]) if len(sys.argv) > 2 else 99999
os.makedirs('/tmp/qa/view', exist_ok=True)
im = Image.open(p); w, h = im.size; h = min(h, maxh)
step = 1800 if w > 500 else 2000
name = os.path.basename(p)[:-4]
for i in range(0, h, step):
    c = im.crop((0, i, w, min(h, i + step)))
    if w > 500: c = c.resize((720, int(c.height / 2)))
    c.save(f'/tmp/qa/view/{name}-{i // step}.png'); print(f'/tmp/qa/view/{name}-{i // step}.png')
