"""Offline regression tests for the cover gate. Version 1.0.0."""
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from audit_book_covers import decode, image_urls, public_url


def png(width=180, height=260, flat=False):
    im = Image.new('RGB', (width, height), 'white')
    if not flat:
        for x in range(width // 2):
            for y in range(height):
                im.putpixel((x, y), (20, 40, 60))
    output = io.BytesIO(); im.save(output, format='PNG')
    return output.getvalue()


class CoverAuditTests(unittest.TestCase):
    def test_valid_raster_decodes(self):
        self.assertEqual(decode(png(), 'image/png').size, (180, 260))

    def test_uniform_placeholder_fails(self):
        with self.assertRaisesRegex(ValueError, 'uniform'):
            decode(png(flat=True), 'image/png')

    def test_tracking_pixel_fails(self):
        with self.assertRaisesRegex(ValueError, 'Placeholder-sized'):
            decode(png(1, 1), 'image/png')

    def test_html_is_not_an_image(self):
        with self.assertRaises(Exception):
            decode(b'<html><h1>404 Not Found</h1></html>', 'text/html')

    def test_safe_standalone_svg_decodes(self):
        svg = b'<svg xmlns="http://www.w3.org/2000/svg" width="180" height="260"><rect width="180" height="260" fill="white"/><rect width="90" height="260" fill="black"/></svg>'
        self.assertEqual(decode(svg, 'image/svg+xml').width, 320)

    def test_svg_external_dependency_is_rejected(self):
        svg = b'<svg xmlns="http://www.w3.org/2000/svg"><image href="https://example.org/cover.jpg"/></svg>'
        with self.assertRaisesRegex(ValueError, 'external'):
            decode(svg, 'image/svg+xml')

    def test_html_entity_url_is_normalized(self):
        self.assertEqual(image_urls('<img src="https://example.org/a.jpg?x=1&amp;y=2">'), {'https://example.org/a.jpg?x=1&y=2'})

    def test_private_address_is_rejected_without_fetch(self):
        with patch('socket.getaddrinfo', return_value=[(2, 1, 6, '', ('127.0.0.1', 443))]):
            with self.assertRaisesRegex(ValueError, 'non-public'):
                public_url('https://example.org/cover.jpg')


if __name__ == '__main__':
    unittest.main()
