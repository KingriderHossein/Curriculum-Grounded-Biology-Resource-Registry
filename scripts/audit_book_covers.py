#!/usr/bin/env python3
"""Read-only cover network, decoding, identity-drift and page audit. v1.1.0.

Visual review is a separate recorded action, not an outcome inferred from HTTP 200.
Requires Pillow and CairoSVG. Writes evidence only; never changes source data.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import io
import ipaddress
import json
from pathlib import Path
import re
import socket
import subprocess
import time
from urllib.parse import urlparse
from urllib.request import Request, build_opener, HTTPRedirectHandler
from PIL import Image, ImageStat
import cairosvg

ROOT = Path(__file__).resolve().parents[1]
VERSION = '1.1.0'
MAX_BYTES = 8 * 1024 * 1024
Image.MAX_IMAGE_PIXELS = 16_000_000
PLACEHOLDER_HASHES = {'3d3ab3559f97b4b8cffe892742c94cae15789e151490f8f875c793ae40826964'}


def public_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Only public HTTPS URLs without credentials are allowed')
    if parsed.port not in (None, 443):
        raise ValueError('Non-standard image URL port')
    addresses = socket.getaddrinfo(parsed.hostname, 443, type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):
        raise ValueError('Image host resolves to a non-public address')


class SafeRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        public_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_image(url: str) -> tuple[bytes, str, str]:
    public_url(url)
    request = Request(url, headers={'User-Agent': 'BiologyResourceRegistry-CoverAudit/1.1', 'Accept': 'image/*'})
    with build_opener(SafeRedirect()).open(request, timeout=20) as response:
        data = response.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise ValueError('Image exceeds 8 MiB')
        return data, response.headers.get('Content-Type', ''), response.geturl()


def decode(data: bytes, content_type: str) -> Image.Image:
    if hashlib.sha256(data).hexdigest() in PLACEHOLDER_HASHES:
        raise ValueError('Known generic book placeholder, not a cover')
    if 'svg' in content_type or b'<svg' in data[:2048]:
        if re.search(rb'<!ENTITY|<!DOCTYPE|<script|<foreignObject|(?:xlink:)?href\s*=|@import|url\(', data, re.I):
            raise ValueError('SVG requires unsafe or external resources')
        data = cairosvg.svg2png(bytestring=data, output_width=320)
    with Image.open(io.BytesIO(data)) as im:
        im.verify()
    with Image.open(io.BytesIO(data)) as im:
        im.load()
        rgb = im.convert('RGB')
    if rgb.width < 90 or rgb.height < 120:
        raise ValueError(f'Placeholder-sized image: {rgb.width}x{rgb.height}')
    if max(ImageStat.Stat(rgb).stddev) < 2:
        raise ValueError('Blank or near-uniform image')
    return rgb


def image_urls(text: str) -> set[str]:
    return {html.unescape(s) for s in re.findall(r'<img\b[^>]*\bsrc=[\"\']([^\"\']+)', text, re.I)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default='cover-audit')
    args = parser.parse_args()
    out = Path(args.out).resolve(); out.mkdir(parents=True, exist_ok=True)
    image_dir = out / 'images'; image_dir.mkdir(exist_ok=True)
    resources = json.loads((ROOT/'data/resources.json').read_text(encoding='utf-8'))['resources']
    placements = json.loads((ROOT/'data/placements.json').read_text(encoding='utf-8'))['placements']
    by_id = {r['id']: r for r in resources}
    paths = [ROOT/'README.md', *sorted((ROOT/'subjects').glob('*/README.md'))]
    page_urls = {str(p.relative_to(ROOT)): image_urls(p.read_text(encoding='utf-8')) for p in paths}
    usage: dict[str, list[str]] = {}
    for path, urls in page_urls.items():
        for url in urls: usage.setdefault(url, []).append(path)
    covers = [r for r in resources if r.get('cover', {}).get('url') or r['resource_type']=='textbook']
    rows = []; cache: dict[str, dict] = {}
    for resource in covers:
        cover = resource.get('cover', {}); url = cover.get('url', '')
        row = {'resource_id': resource['id'], 'title': resource['title'], 'edition': resource.get('edition'), 'isbn': resource.get('isbn'), 'url': url, 'pages': sorted(usage.get(url, [])), 'visual_identity': 'not_reviewed'}
        if url not in cache:
            try:
                data, ct, final_url = fetch_image(url)
                image = decode(data, ct)
                name = hashlib.sha256(url.encode()).hexdigest()[:16]+'.png'
                size = [image.width, image.height]; image.thumbnail((400, 600)); image.save(image_dir/name)
                result = {'load_status': 'decoded', 'content_type': ct, 'bytes': len(data), 'dimensions': size, 'sha256': hashlib.sha256(data).hexdigest(), 'final_url': final_url, 'thumbnail': 'images/'+name}
            except Exception as exc:
                result = {'load_status': 'failed', 'error': f'{type(exc).__name__}: {exc}'}
            cache[url] = result; time.sleep(1.1)
        row.update(cache[url])
        if cover.get('visual_review_status') == 'title_and_edition_checked' and cover.get('visual_reviewed_on') and cover.get('source_url'):
            row['visual_identity'] = 'reviewed_bytes_match' if row.get('sha256') == cover.get('expected_sha256') else 'changed_since_review'
        rows.append(row); print(json.dumps(row, ensure_ascii=False), flush=True)
    known = set(cache)
    unregistered = sorted(set(usage)-known)
    missing = []
    for p in placements:
        r = by_id[p['resource_id']]; url = r.get('cover', {}).get('url')
        if not url: continue
        page = 'subjects/'+p['subject_id'].lower()+'/README.md'
        if url not in page_urls.get(page, set()): missing.append({'placement': p['id'], 'page': page, 'url': url})
    commit = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
    report = {'version': VERSION, 'commit': commit, 'checked_at_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'covers': rows, 'page_images_without_registry_cover': unregistered, 'placements_missing_visible_cover': missing, 'note': 'Only exact bytes previously reviewed visually pass identity checks. These checks do not establish copyright permission or guarantee future availability.'}
    (out/'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    cards = []
    for row in rows:
        image = '<img src="'+row['thumbnail']+'" style="max-width:180px;height:250px;object-fit:contain">' if row.get('thumbnail') else '<strong>IMAGE FAILED</strong>'
        cards.append('<section style="border:1px solid #aaa;padding:16px;width:250px">'+image+'<h3>'+html.escape(row['title'])+'</h3><p>'+html.escape(str(row.get('edition')))+'</p><p>'+html.escape(str(row.get('isbn')))+'</p><p>'+html.escape(row.get('error', row['visual_identity']))+'</p></section>')
    (out/'gallery.html').write_text('<!doctype html><meta charset="utf-8"><title>Book-cover audit</title><main style="display:flex;flex-wrap:wrap;gap:12px">'+''.join(cards)+'</main>', encoding='utf-8')
    failures = sum(r['load_status']!='decoded' or r['visual_identity']!='reviewed_bytes_match' for r in rows)
    print(f'COVER AUDIT: {len(rows)} covers; {failures} image/review failures; {len(missing)} missing page covers; {len(unregistered)} unregistered URLs')
    return 1 if failures or missing or unregistered else 0

if __name__ == '__main__':
    raise SystemExit(main())
