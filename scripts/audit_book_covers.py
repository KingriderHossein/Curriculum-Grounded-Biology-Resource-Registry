#!/usr/bin/env python3
"""Audit book-cover GET responses, decoded images, and Markdown usage. v1.0.0.

Read-only: writes reports and review thumbnails, never changes registry data.
Requires Pillow and CairoSVG. Successful decoding is NOT title/edition approval.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import io
import ipaddress
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import time
from urllib.parse import urlparse, urljoin
from urllib.request import Request, build_opener, HTTPRedirectHandler

from PIL import Image, ImageStat
import cairosvg

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 8 * 1024 * 1024
Image.MAX_IMAGE_PIXELS = 16_000_000


def public_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Only public HTTPS image URLs without credentials are allowed')
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
    request = Request(url, headers={'User-Agent': 'BiologyResourceRegistry-CoverAudit/1.0', 'Accept': 'image/*'})
    with build_opener(SafeRedirect()).open(request, timeout=20) as response:
        data = response.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise ValueError('Image exceeds 8 MiB')
        return data, response.headers.get('Content-Type', ''), response.geturl()


def decode(data: bytes, content_type: str) -> Image.Image:
    if 'svg' in content_type or b'<svg' in data[:2048]:
        # No scripts, external references, fonts or stylesheets in accepted SVGs.
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default='cover-audit')
    args = parser.parse_args()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    image_dir = out / 'images'
    image_dir.mkdir(exist_ok=True)
    resources = json.loads((ROOT / 'data/resources.json').read_text(encoding='utf-8'))['resources']
    pages = [ROOT / 'README.md', *sorted((ROOT / 'subjects').glob('*/README.md'))]
    usage: dict[str, list[str]] = {}
    for path in pages:
        text = path.read_text(encoding='utf-8')
        for source in re.findall(r'<img\b[^>]*\bsrc=[\"\']([^\"\']+)', text, re.I):
            source = html.unescape(source)
            usage.setdefault(source, []).append(str(path.relative_to(ROOT)))
    covers = [r for r in resources if r.get('cover', {}).get('url') or r['resource_type'] == 'textbook']
    rows = []
    cache: dict[str, dict] = {}
    for resource in covers:
        url = resource.get('cover', {}).get('url', '')
        row = {'resource_id': resource['id'], 'title': resource['title'], 'edition': resource.get('edition'), 'isbn': resource.get('isbn'), 'url': url, 'pages': sorted(set(usage.get(url, []))), 'visual_identity': 'not_reviewed'}
        if url in cache:
            row.update(cache[url])
        else:
            try:
                if not url:
                    raise ValueError('Missing cover URL')
                data, content_type, final_url = fetch_image(url)
                image = decode(data, content_type)
                filename = hashlib.sha256(url.encode()).hexdigest()[:16] + '.png'
                size = [image.width, image.height]
                image.thumbnail((400, 600))
                image.save(image_dir / filename)
                result = {'load_status': 'decoded', 'content_type': content_type, 'bytes': len(data), 'dimensions': size, 'sha256': hashlib.sha256(data).hexdigest(), 'final_url': final_url, 'thumbnail': 'images/' + filename}
            except Exception as exc:
                result = {'load_status': 'failed', 'error': f'{type(exc).__name__}: {exc}'}
            cache[url] = result
            row.update(result)
            time.sleep(1.1)
        rows.append(row)
        print(json.dumps(row, ensure_ascii=False), flush=True)
    known_urls = set(cache)
    unregistered = sorted(set(usage) - known_urls)
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'version': '1.0.0', 'commit': commit, 'checked_at_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'covers': rows, 'page_images_without_registry_cover': unregistered, 'note': 'Decoded images still require visual title/edition review. Network checks describe this run only.'}
    (out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    cards = []
    for row in rows:
        image = '<img src="' + row['thumbnail'] + '" style="max-width:180px;height:250px;object-fit:contain">' if row.get('thumbnail') else '<strong>IMAGE FAILED</strong>'
        cards.append('<section style="border:1px solid #aaa;padding:16px;width:250px">' + image + '<h3>' + html.escape(row['title']) + '</h3><p>' + html.escape(str(row.get('edition'))) + '</p><p>' + html.escape(str(row.get('isbn'))) + '</p><p>' + html.escape(row.get('error', row['load_status'])) + '</p></section>')
    (out / 'gallery.html').write_text('<!doctype html><meta charset="utf-8"><title>Book-cover audit</title><main style="display:flex;flex-wrap:wrap;gap:12px">' + ''.join(cards) + '</main>', encoding='utf-8')
    failed = sum(r['load_status'] != 'decoded' for r in rows)
    print(f'COVER AUDIT: {len(rows)} records; {failed} load failures; {len(unregistered)} unregistered page image URLs', flush=True)
    return 1 if failed or unregistered else 0


if __name__ == '__main__':
    raise SystemExit(main())
