"""Build only the explicitly selected public website files; no runtime dependencies."""
from html import escape
import json
from pathlib import Path
import re
from string import Template
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'website'
BASE_URL = 'https://kiran-980.github.io/1ml/'
REPO = 'https://github.com/Kiran-980/1ml'


def install_commands(host):
    guide = (ROOT / 'docs/installation.md').read_text(encoding='utf-8')
    section = guide.split(f'## {host}\n', 1)[1].split('\n## ', 1)[0]
    return re.search(r'```\w*\n(.*?)\n```', section, re.S).group(1)


def build(output):
    output = Path(output)
    pages = json.loads((SOURCE / 'pages.json').read_text(encoding='utf-8'))
    template = Template((SOURCE / 'template.html').read_text(encoding='utf-8'))
    substitutions = dict(base='/1ml/', repo=REPO,
                         claude_install=escape(install_commands('Claude Code')),
                         codex_install=escape(install_commands('Codex')))
    urls = []
    for page in pages:
        slug = page['slug']
        relative = '404.html' if slug == '404' else (f'{slug}/index.html' if slug else 'index.html')
        canonical = BASE_URL + ('404.html' if slug == '404' else f'{slug}/' if slug else '')
        body = Template((SOURCE / 'content' / page['content']).read_text(encoding='utf-8')).substitute(substitutions)
        if not slug:
            schema = {'@context': 'https://schema.org', '@type': 'SoftwareSourceCode',
                      'name': '1ml', 'description': page['description'], 'url': canonical,
                      'codeRepository': REPO, 'license': REPO + '/blob/main/LICENSE',
                      'programmingLanguage': 'Python', 'isAccessibleForFree': True,
                      'author': {'@type': 'Person', 'name': 'Kiran', 'url': 'https://github.com/Kiran-980'}}
        else:
            schema = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': '1ml', 'item': BASE_URL},
                {'@type': 'ListItem', 'position': 2, 'name': page['label'], 'item': canonical}]}
        nav = ''.join(f'<a href="/1ml/{route}/"' + (' aria-current="page"' if slug == route else '') + f'>{label}</a>'
                      for route, label in [('machine-learning-skills', 'Skills'), ('examples', 'Examples'), ('getting-started', 'Get started')])
        document = template.substitute(title=escape(page['title']), description=escape(page['description'], quote=True),
            canonical=canonical, robots='noindex, follow' if slug == '404' else 'index, follow',
            schema=json.dumps(schema, ensure_ascii=False).replace('<', '\\u003c'), body=body, nav=nav,
            page_class='home' if not slug else 'guide', repo=REPO)
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(document, encoding='utf-8', newline='\n')
        if slug != '404':
            urls.append(canonical)
    for name in ('styles.css', 'site.js', 'favicon.svg'):
        target = output / 'assets' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((SOURCE / 'assets' / name).read_bytes())
    (output / '.nojekyll').write_text('', encoding='utf-8')
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += ''.join(f'  <url><loc>{xml_escape(url)}</loc></url>\n' for url in urls) + '</urlset>\n'
    (output / 'sitemap.xml').write_text(sitemap, encoding='utf-8')
    return output


if __name__ == '__main__':
    result = build(ROOT / 'build/site')
    print(f'Built public website: {result}')
