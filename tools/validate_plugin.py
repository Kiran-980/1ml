"""Validate local skill discovery, resource containment and reference connectivity."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
from urllib.parse import unquote
import yaml

EXPECTED = {'lifecycle', 'frame', 'data', 'evaluation', 'explore', 'statistics',
            'prepare', 'train', 'validate', 'experiment', 'release', 'operate'}


def slug(text):
    return re.sub(r'[^\w\- ]', '', text.lower()).replace(' ', '-')


def validate(root):
    root = Path(root).resolve()
    errors = []
    skills = sorted((root/'skills').glob('*/SKILL.md'))
    files = sorted(set((root/'skills').rglob('*.md')) | set((root/'references').rglob('*.md')))
    names = set()
    graph = {}
    link_count = 0
    for file in files:
        text = file.read_text(encoding='utf-8')
        if not text.strip():
            errors.append(f'{file.relative_to(root)}: empty')
        if file.name == 'SKILL.md':
            match = re.match(r'^---\n(.*?)\n---(?:\n|$)', text, re.S)
            if not match:
                errors.append(f'{file.relative_to(root)}: missing frontmatter')
            else:
                try:
                    meta = yaml.safe_load(match.group(1))
                    name = meta.get('name')
                    if name != file.parent.name or not isinstance(meta.get('description'), str) or not meta['description'].strip():
                        errors.append(f'{file.relative_to(root)}: invalid name/description')
                    names.add(name)
                    if meta.get('disable-model-invocation'):
                        errors.append(f'{file.relative_to(root)}: coordinator cannot automatically invoke this skill')
                except (ValueError, AttributeError, TypeError, yaml.YAMLError) as exc:
                    errors.append(f'{file.relative_to(root)}: invalid frontmatter: {exc}')
        if sum(line.startswith('```') for line in text.splitlines()) % 2:
            errors.append(f'{file.relative_to(root)}: unclosed code fence')
        graph[file] = []
        for destination in re.findall(r'\]\(([^\s)]+)\)', text):
            if destination.startswith(('https://', 'http://', 'mailto:')):
                continue
            link_count += 1
            base, _, anchor = unquote(destination).partition('#')
            target = (file.parent/base).resolve() if base else file
            if not target.is_relative_to(root):
                errors.append(f'{file.relative_to(root)}: outside package: {destination}')
                continue
            if not target.is_file():
                errors.append(f'{file.relative_to(root)}: missing: {destination}')
                continue
            if 'ml-lifecycle' in target.relative_to(root).parts or target.name.startswith('ML-LIFECYCLE'):
                errors.append(f'{file.relative_to(root)}: runtime depends on ignored research: {destination}')
            graph[file].append(target)
            if anchor and target.suffix == '.md':
                headings = re.findall(r'^#{1,6} (.+)$', target.read_text(encoding='utf-8'), re.M)
                if anchor not in [slug(h) for h in headings]:
                    errors.append(f'{file.relative_to(root)}: missing anchor: {destination}')
    if names != EXPECTED:
        errors.append(f'skill inventory differs: missing {sorted(EXPECTED-names)}, extra {sorted(names-EXPECTED)}')
    reached = set(skills)
    queue = list(skills)
    while queue:
        for target in graph.get(queue.pop(), []):
            if target not in reached:
                reached.add(target)
                queue.append(target)
    for file in files:
        if file not in reached:
            errors.append(f'unreachable reference: {file.relative_to(root)}')
    for table in (root/'rules').glob('*.yaml'):
        payload = yaml.safe_load(table.read_text(encoding='utf-8'))
        for rule in payload.get('rules', []):
            reference = rule.get('reference', '')
            target = (root/reference).resolve()
            if not reference or not target.is_relative_to(root) or not target.is_file():
                errors.append(f'{table.name}: missing/outside rule reference {reference}')
    manifest = root/'.claude-plugin/plugin.json'
    if not manifest.is_file():
        errors.append('missing plugin manifest')
    else:
        try:
            if json.loads(manifest.read_text(encoding='utf-8')).get('name') != '1ml':
                errors.append('unexpected plugin name')
        except ValueError as exc:
            errors.append(f'invalid plugin manifest: {exc}')
    return {'skill_count': len(skills), 'markdown_files': len(files),
            'local_links': link_count, 'errors': errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', nargs='?', default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    result = validate(args.root)
    print(json.dumps(result, indent=2))
    return int(bool(result['errors']))


if __name__ == '__main__':
    raise SystemExit(main())
