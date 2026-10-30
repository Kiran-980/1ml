"""Check the actual public artifact, its navigation and indexing metadata."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit, unquote
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]

class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids, self.links, self.meta, self.canonical = set(), [], {}, []
        self.h1 = self.main = 0
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.ids.add(a['id'])
        if tag in ('a', 'link') and 'href' in a:
            self.links.append(a['href'])
        if tag in ('script', 'img') and 'src' in a:
            self.links.append(a['src'])
        if tag == 'meta':
            self.meta[a.get('name', a.get('property'))] = a.get('content')
        if tag == 'link' and a.get('rel') == 'canonical':
            self.canonical.append(a['href'])
        self.h1 += tag == 'h1'
        self.main += tag == 'main'


class WebsiteTests(unittest.TestCase):
    def test_public_artifact_navigation_and_metadata(self):
        spec = importlib.util.spec_from_file_location('website_builder', ROOT / 'website/build.py')
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'site'
            builder.build(output)
            htmls = sorted(output.rglob('*.html'))
            self.assertEqual(len(htmls), 9)
            canonicals, descriptions, titles = set(), set(), set()
            for path in htmls:
                text = path.read_text(encoding='utf-8')
                parsed = Page(text)
                self.assertEqual(parsed.h1, 1, path)
                self.assertEqual(parsed.main, 1, path)
                self.assertEqual(len(parsed.canonical), 1, path)
                self.assertIn('viewport', parsed.meta)
                import re
                title = re.search(r'<title>(.*?)</title>', text).group(1)
                self.assertNotIn(title, titles)
                titles.add(title)
                self.assertNotIn(parsed.meta['description'], descriptions)
                descriptions.add(parsed.meta['description'])
                canonical = parsed.canonical[0]
                self.assertTrue(canonical.startswith(builder.BASE_URL))
                if path.name != '404.html':
                    canonicals.add(canonical)
                    self.assertNotIn('noindex', parsed.meta.get('robots', ''))
                else:
                    self.assertIn('noindex', parsed.meta['robots'])
                for href in parsed.links:
                    target_url = urljoin(canonical, href)
                    if not target_url.startswith(builder.BASE_URL):
                        continue
                    target = urlsplit(target_url)
                    rel = unquote(target.path.removeprefix('/1ml/'))
                    local = output / rel
                    if target.path.endswith('/'):
                        local /= 'index.html'
                    self.assertTrue(local.is_file(), f'{path.name}: {href}')
                    if target.fragment:
                        self.assertIn(unquote(target.fragment), Page(local.read_text(encoding='utf-8')).ids)
                for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', text, re.S):
                    json.loads(raw)
            sitemap = ET.parse(output / 'sitemap.xml')
            urls = {node.text for node in sitemap.findall('.//{*}loc')}
            self.assertEqual(urls, canonicals)
            files = [p for p in output.rglob('*') if p.is_file()]
            self.assertTrue(all(p.suffix in ('.html', '.css', '.js', '.svg', '.xml') or p.name == '.nojekyll' for p in files))
            self.assertLess(sum(p.stat().st_size for p in files), 200_000)
            self.assertFalse(any(p.name.startswith('.env') for p in files))
            self.assertFalse((output / 'tools').exists())
            self.assertFalse((output / '.github').exists())
            self.assertFalse((output / '.runtime').exists())
            # Build is repeatable without accumulating unrelated project files.
            first = {p.relative_to(output): p.read_bytes() for p in files}
            builder.build(output)
            self.assertEqual(first, {p.relative_to(output): p.read_bytes() for p in output.rglob('*') if p.is_file()})

    def test_install_commands_come_from_maintained_guide(self):
        spec = importlib.util.spec_from_file_location('website_builder', ROOT / 'website/build.py')
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        guide = (ROOT / 'docs/installation.md').read_text(encoding='utf-8')
        for host in ('Claude Code', 'Codex'):
            command = builder.install_commands(host)
            self.assertIn(command, guide)
            self.assertIn('main', command)


if __name__ == '__main__':
    unittest.main()
