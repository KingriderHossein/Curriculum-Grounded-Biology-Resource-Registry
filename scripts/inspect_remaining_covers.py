#!/usr/bin/env python3
"""Bounded image candidates requiring visual review; no data mutation. v1.0.0."""
import hashlib
import json
from pathlib import Path
from audit_book_covers import ROOT, fetch_image, decode

CANDIDATES = [
 ('lewin-exact', 'https://images.booksense.com/images/834/189/9781284189834.jpg'),
 ('lewin-package', 'https://images.booksense.com/images/130/173/9781284173130.jpg'),
 ('brock-publisher', 'https://www.pearson.com/store/pmccommercewebservices/v2/medias/size-W370-A1030-00-25-75-A103000257574-A103000257574-Lrg.jpg?context=bWFzdGVyfGltYWdlc3wyMzg3MnxpbWFnZS9qcGVnfHN5cy1tYXN0ZXIvaW1hZ2VzL2g3Mi9oN2QvMTU0NDE0MzAxNTExOTgvc2l6ZV9XMzcwXy9BMTAzMC8wMC8yNS83NS9BMTAzMDAwMjU3NTc0L0ExMDMwMDAyNTc1NzRfTHJnLmpwZ3wzOTdjOTEzMWE5ZjVjY2MyZWEzNjUzYmY1YTk1Nzk2YjU0NTFjOWIzYTVmZWIzMjNjYmI3ZTYwYjgwN2RjZDA4&imwidth=3840'),
 ('brock-booksense', 'https://images.booksense.com/images/790/404/9781292404790.jpg'),
 ('prescott-2026-ise', 'https://www.mheducation.com/cover-images/Jpeg_400-high/1265827176.jpeg'),
 ('openstax-biology-full', 'https://covers.openlibrary.org/b/isbn/9781947172517-L.jpg?default=false'),
]

def main():
    out = ROOT / 'cover-audit/remaining'; out.mkdir(parents=True, exist_ok=True)
    rows = []
    for label, url in CANDIDATES:
        row = {'label': label, 'url': url}
        try:
            data, ct, final_url = fetch_image(url)
            sha = hashlib.sha256(data).hexdigest()
            if sha == '3d3ab3559f97b4b8cffe892742c94cae15789e151490f8f875c793ae40826964':
                raise ValueError('Known generic book placeholder')
            im = decode(data, ct); size = im.size
            im.thumbnail((500, 700)); im.save(out / (label+'.png'))
            row.update(status='decoded', dimensions=size, sha256=sha, content_type=ct, final_url=final_url)
        except Exception as exc:
            row.update(status='failed', error=str(exc))
        rows.append(row); print(json.dumps(row), flush=True)
    (out/'report.json').write_text(json.dumps(rows, indent=2))

if __name__ == '__main__':
    main()
