#!/usr/bin/env python3
"""Collect candidate images for human review; never automatically approve them. v1.0.0."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import time
from audit_book_covers import ROOT, fetch_image, decode


def isbn10(isbn: str) -> str:
    raw = isbn.replace('-', '')
    if len(raw) != 13 or not raw.startswith('978'):
        raise ValueError('ISBN-10 conversion requires a 978-prefixed ISBN-13')
    body = raw[3:12]
    digit = (-sum((10 - i) * int(n) for i, n in enumerate(body))) % 11
    return body + ('X' if digit == 10 else str(digit))


def main() -> None:
    out = ROOT / 'cover-audit/candidates'
    out.mkdir(parents=True, exist_ok=True)
    resources = json.loads((ROOT / 'data/resources.json').read_text(encoding='utf-8'))['resources']
    report = json.loads((ROOT / 'cover-audit/report.json').read_text(encoding='utf-8'))
    failed = {x['resource_id'] for x in report['covers'] if x['load_status'] == 'failed'}
    records = []
    for r in resources:
        if r['id'] not in failed:
            continue
        isbn = r.get('isbn', '')
        urls = []
        if 'Macmillan' in r.get('publisher', ''):
            urls.append(('publisher_isbn_candidate', f'https://prod-cat-files.macmillan.cloud/MediaResources/Jackets/258W/{isbn}.jpg'))
        if 'Norton' in r.get('publisher', ''):
            urls.append(('publisher_isbn_candidate', f'https://cdn2.wwnorton.com/wwnproducts/COLLEG/{isbn[-1]}/{isbn[-2]}/{isbn}/{isbn}_198.jpg'))
        if 'Wiley' in r.get('publisher', ''):
            urls.append(('publisher_isbn_candidate', f'https://media.wiley.com/product_data/coverImage300/{isbn[-2:]}/{isbn}.jpg'))
        if 'McGraw' in r.get('publisher', ''):
            urls.append(('publisher_isbn_candidate', f'https://www.mheducation.com/cover-images/Jpeg_400-high/{isbn10(isbn)}.jpeg'))
        if 'Pearson' in r.get('publisher', ''):
            urls.append(('publisher_isbn_candidate', f'https://www.pearson.com/store/medias/{isbn}.jpg'))
        urls.append(('isbn_matched_retailer_candidate', f'https://dynamic.indigoimages.ca/v1/books/books/{isbn10(isbn)}/1.jpg'))
        for source, url in urls:
            rec = {'resource_id': r['id'], 'title': r['title'], 'edition': r.get('edition'), 'isbn': isbn, 'source': source, 'url': url, 'visual_identity': 'not_reviewed'}
            try:
                data, ct, final_url = fetch_image(url)
                im = decode(data, ct)
                name = hashlib.sha256(url.encode()).hexdigest()[:16] + '.png'
                rec.update({'status': 'decoded', 'dimensions': [im.width, im.height], 'sha256': hashlib.sha256(data).hexdigest(), 'content_type': ct, 'final_url': final_url, 'thumbnail': name})
                im.thumbnail((500, 700))
                im.save(out / name)
            except Exception as exc:
                rec.update({'status': 'failed', 'error': f'{type(exc).__name__}: {exc}'})
            records.append(rec)
            print(json.dumps(rec), flush=True)
            time.sleep(1)
    (out / 'report.json').write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
