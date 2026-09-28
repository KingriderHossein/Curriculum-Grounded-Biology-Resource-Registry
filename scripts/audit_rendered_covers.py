#!/usr/bin/env python3
"""Verify real GitHub-rendered cover images with Chromium. Version 1.1.0.

Public pages only. No login, browser extensions, account actions or source edits.
The report distinguishes network/render failures from successful source decoding.
Transient GitHub/Camo failures are retried a small, bounded number of times.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess
import time
from urllib.parse import quote
from playwright.sync_api import sync_playwright
from audit_book_covers import ROOT, image_urls

REPO = 'KingriderHossein/Curriculum-Grounded-Biology-Resource-Registry'
MAX_ATTEMPTS = 3
RETRYABLE_HTTP = {429, 500, 502, 503, 504}


def retryable_failure(row: dict) -> str | None:
    status = row.get('http_status')
    if status in RETRYABLE_HTTP:
        return f'GitHub HTTP {status}'
    if status == 200:
        if row.get('missing_images'):
            return 'expected image not present in rendered page'
        if any(not item.get('loaded') for item in row.get('images', [])):
            return 'rendered image did not finish loading'
    error = row.get('error', '')
    if 'TimeoutError' in error or 'net::ERR_' in error:
        return 'transient browser/network error'
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default='cover-audit/browser')
    args = parser.parse_args()
    out = Path(args.out).resolve(); out.mkdir(parents=True, exist_ok=True)
    sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    paths = ['README.md', *[str(p.relative_to(ROOT)) for p in sorted((ROOT/'subjects').glob('*/README.md'))]]
    subject_paths = [path for path in paths if path.startswith('subjects/')]
    cases = [(path, 1440, 1000) for path in paths] + [(path, 390, 844) for path in subject_paths]
    reports = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for path, width, height in cases:
            expected = image_urls((ROOT/path).read_text(encoding='utf-8'))
            label = path.replace('/', '-').replace('.md', '') + f'-{width}'
            url = f'https://github.com/{REPO}/blob/{sha}/{quote(path, safe="/")}'
            row = None
            for attempt in range(1, MAX_ATTEMPTS + 1):
                row = {
                    'path': path,
                    'width': width,
                    'commit': sha,
                    'expected_images': len(expected),
                    'url': url,
                    'attempt': attempt,
                }
                page = browser.new_page(viewport={'width': width, 'height': height}, device_scale_factor=1)
                try:
                    response = page.goto(url, wait_until='domcontentloaded', timeout=60000)
                    row['http_status'] = response.status if response else None
                    if not response or response.status != 200:
                        raise RuntimeError(f'GitHub page HTTP {row["http_status"]}')
                    body = page.locator('.markdown-body').first
                    body.wait_for(state='visible', timeout=45000)
                    body.locator('details').evaluate_all('(items) => items.forEach(e => {e.open=true})')
                    images = body.locator('img')
                    rendered = []
                    for index in range(images.count()):
                        image = images.nth(index)
                        canonical = image.get_attribute('data-canonical-src') or image.get_attribute('src') or ''
                        if canonical not in expected:
                            continue
                        image.scroll_into_view_if_needed(timeout=15000)
                        page.wait_for_function('(e) => e.complete', arg=image.element_handle(), timeout=30000)
                        state = image.evaluate('(e) => ({src:e.currentSrc,width:e.naturalWidth,height:e.naturalHeight,visibleWidth:e.getBoundingClientRect().width,visibleHeight:e.getBoundingClientRect().height})')
                        state['canonical_url'] = canonical
                        state['loaded'] = state['width'] >= 90 and state['height'] >= 120 and state['visibleWidth'] > 0
                        if state['loaded']:
                            image.screenshot(path=str(out/f'{label}-cover-{len(rendered)+1}.png'))
                        rendered.append(state)
                    row['images'] = rendered
                    found = {item['canonical_url'] for item in rendered}
                    row['missing_images'] = sorted(expected-found)
                    row['status'] = 'passed' if not row['missing_images'] and all(x['loaded'] for x in rendered) else 'failed'
                    if not expected:
                        row['status'] = 'failed'; row['error'] = 'No expected source images'
                    if path.startswith('subjects/'):
                        body.scroll_into_view_if_needed(timeout=15000)
                        page.screenshot(path=str(out/f'{label}-page-top.png'), full_page=False)
                        row['rtl_containers'] = body.locator('[dir=rtl]').count()
                        row['ltr_containers'] = body.locator('[dir=ltr]').count()
                except Exception as exc:
                    row.update(status='failed', error=f'{type(exc).__name__}: {exc}')
                    try:
                        page.screenshot(path=str(out/f'{label}-failure-attempt-{attempt}.png'), full_page=False)
                    except Exception:
                        pass
                finally:
                    page.close()

                reason = retryable_failure(row)
                if row['status'] == 'passed' or not reason or attempt == MAX_ATTEMPTS:
                    break
                print(json.dumps({
                    'path': path,
                    'width': width,
                    'attempt': attempt,
                    'status': 'retrying',
                    'reason': reason,
                }, ensure_ascii=False), flush=True)
                time.sleep(attempt * 2)

            assert row is not None
            reports.append(row)
            print(json.dumps(row, ensure_ascii=False), flush=True)
            (out/'report.json').write_text(json.dumps({'version':'1.1.0','commit':sha,'cases':reports}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        browser.close()
    failures = sum(x['status']!='passed' for x in reports)
    print(f'GITHUB BROWSER AUDIT: {len(reports)} cases; {failures} failures')
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
