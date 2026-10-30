"""Project-local evidence state; dependencies are declared per request, never linear."""
from __future__ import annotations
import argparse
import copy
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common

STATUSES = ('pending', 'running', 'complete', 'blocked', 'failed', 'stale', 'not_applicable')
OUTCOMES = ('supported', 'no_go', 'inconclusive', 'collect_data', 'retain_baseline', 'needs_research')


class GateError(ValueError):
    """An evidence dependency, version, or completion contract is unsatisfied."""


def canonical(stage):
    stage = common.STAGE_ALIASES.get(stage, stage)
    if stage not in common.STAGE_ORDER:
        raise GateError(f'unknown task: {stage}')
    return stage


def init_project(root, name='ml-project', goal='', notebook=common.DEFAULT_NOTEBOOK):
    paths = common.project_paths(str(root))
    with common.file_lock(paths['state_dir'] / '.state.lock'):
        if paths['state_file'].exists():
            raise FileExistsError(f"State already exists: {paths['state_file']}; resume it.")
        document = {'version': 2, 'revision': 0,
                    'project': {'name': name, 'goal': goal, 'notebook': notebook,
                                'created_at': common.utcnow()},
                    'stages': {s: common.blank_stage() for s in common.STAGE_ORDER}, 'sources': []}
        common.write_json(paths['state_file'], document)
    return document


def load_state(root):
    path = common.project_paths(str(root))['state_file']
    document = common.read_json(path)
    version = document.get('version')
    if version not in (1, 2):
        raise GateError(f'unsupported state version: {version}')
    if version == 1:
        legacy = copy.deepcopy(document.get('stages', {}))
        document['legacy_stages'] = legacy
        document['stages'] = {s: common.blank_stage() for s in common.STAGE_ORDER}
        for name, record in legacy.items():
            dest = common.STAGE_ALIASES.get(name, name)
            if dest not in document['stages']:
                continue
            current = document['stages'][dest]
            for key in ('conclusions', 'questions', 'decisions', 'cells', 'rule_matches'):
                current[key].extend(record.get(key, []))
            if record.get('status') != 'pending':
                current['status'] = 'stale'
                current['reason'] = 'Legacy evidence requires verification against current task contract.'
        document['version'] = 2
    document.setdefault('revision', 0)
    for name in common.STAGE_ORDER:
        record = document.setdefault('stages', {}).setdefault(name, common.blank_stage())
        for key, value in common.blank_stage().items():
            record.setdefault(key, value)
    return document


def save_state(root, document):
    paths = common.project_paths(str(root))
    with common.file_lock(paths['state_dir'] / '.state.lock'):
        current = common.read_json(paths['state_file'])
        if current.get('revision', 0) != document['revision']:
            raise GateError('state revision changed; reload and reconcile before saving')
        if current.get('version') == 1:
            backup = paths['state_dir'] / 'state.v1.json'
            if not backup.exists():
                common.write_json(backup, current)
        updated = copy.deepcopy(document)
        updated['revision'] += 1
        updated['updated_at'] = common.utcnow()
        common.write_json(paths['state_file'], updated)
        document.update(updated)


def _merge(record, **findings):
    for key, values in findings.items():
        for value in values or []:
            if value not in record[key]:
                record[key].append(value)


def _invalidate(document, stage, reason):
    affected = {stage}
    while True:
        more = {name for name, rec in document['stages'].items()
                if affected.intersection(rec['dependencies'])}
        if more <= affected:
            break
        affected |= more
    for name in affected:
        record = document['stages'][name]
        snapshot = {key: copy.deepcopy(value) for key, value in record.items() if key != 'history'}
        record['history'].append(snapshot)
        record.update(status='stale', outcome=None, reason=reason, updated_at=common.utcnow())
    return sorted(affected)


def invalidate(root, stage, reason):
    if not reason or not reason.strip():
        raise GateError('invalidation requires a reason')
    document = load_state(root)
    affected = _invalidate(document, canonical(stage), reason)
    save_state(root, document)
    return affected


def configure_stage(root, stage, dependencies):
    stage = canonical(stage)
    dependencies = list(dict.fromkeys(canonical(d) for d in dependencies))
    document = load_state(root)
    record = document['stages'][stage]
    old = record['dependencies']
    record['dependencies'] = dependencies
    def visit(name, active, done):
        if name in active:
            raise GateError('dependency cycle: ' + ' -> '.join(active + [name]))
        if name in done:
            return
        for dependency in document['stages'][name]['dependencies']:
            visit(dependency, active + [name], done)
        done.add(name)
    visit(stage, [], set())
    if old != dependencies and record['status'] not in ('pending', 'stale'):
        _invalidate(document, stage, 'Task prerequisites changed.')
    save_state(root, document)
    return record


def _ready(record):
    return record['status'] == 'not_applicable' or (
        record['status'] == 'complete' and record['outcome'] in ('supported', 'retain_baseline'))


def set_stage(root, stage, status, conclusions=None, questions=None, decisions=None,
              cells=None, rule_matches=None, outcome=None, reason=None):
    stage = canonical(stage)
    status = {'done': 'complete', 'active': 'running'}.get(status, status)
    if status not in STATUSES or (outcome is not None and outcome not in OUTCOMES):
        raise GateError('unknown status or outcome')
    if status in ('blocked', 'failed', 'stale', 'not_applicable') and not (reason and reason.strip()):
        raise GateError(f'{status} requires a reason')
    document = load_state(root)
    record = document['stages'][stage]
    if status == 'complete':
        if not conclusions and not decisions:
            raise GateError('completion requires fresh findings with evidence references')
        missing = [d for d in record['dependencies'] if not _ready(document['stages'][d])]
        if missing:
            raise GateError('unsatisfied prerequisites: ' + ', '.join(missing))
    if record['status'] in ('complete', 'not_applicable') or status == 'stale':
        _invalidate(document, stage, reason or 'Upstream findings changed.')
    _merge(record, conclusions=conclusions, questions=questions, decisions=decisions,
           cells=cells, rule_matches=rule_matches)
    record.update(status=status, outcome=(outcome or 'supported') if status == 'complete' else None,
                  reason=reason, updated_at=common.utcnow())
    save_state(root, document)
    return record


def record_stage(root, stage, conclusions=None, questions=None, decisions=None,
                 cells=None, rule_matches=None):
    stage = canonical(stage)
    document = load_state(root)
    record = document['stages'][stage]
    findings = dict(conclusions=conclusions, questions=questions, decisions=decisions,
                    cells=cells, rule_matches=rule_matches)
    changed = any(v not in record[k] for k, values in findings.items() for v in values or [])
    if not changed:
        return record
    if record['status'] in ('complete', 'not_applicable'):
        _invalidate(document, stage, 'Additional findings need revalidation.')
    _merge(record, **findings)
    record['updated_at'] = common.utcnow()
    save_state(root, document)
    return record


def next_stage(root, stage=None):
    document = load_state(root)
    if stage is None:
        return {'stage': None, 'status': 'needs_request', 'blocked': False,
                'reason': 'Choose the requested task from intent and evidence; no universal next stage.'}
    stage = canonical(stage)
    def resolve(name, visited):
        if name in visited:
            raise GateError('dependency cycle in saved state')
        rec = document['stages'][name]
        for dep in rec['dependencies']:
            if not _ready(document['stages'][dep]):
                return resolve(dep, visited | {name})
        return name
    current = document['stages'][stage]
    if current['status'] in ('complete', 'not_applicable'):
        return {'stage': None, 'status': current['status'], 'outcome': current['outcome'], 'blocked': False}
    target = resolve(stage, set())
    rec = document['stages'][target]
    blocked = rec['status'] in ('blocked', 'failed') or (rec['status'] == 'complete' and not _ready(rec))
    return {'stage': target, 'title': common.STAGE_TITLES[target], 'status': rec['status'],
            'outcome': rec['outcome'], 'blocked': blocked, 'reason': rec['reason']}


def add_source(root, path, kind='csv'):
    document = load_state(root)
    entry = {'path': path, 'kind': kind, 'added_at': common.utcnow()}
    document['sources'].append(entry)
    save_state(root, document)
    return entry


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('init', 'show', 'set-stage', 'next', 'configure', 'invalidate', 'add-source'):
        cmd = sub.add_parser(name)
        cmd.add_argument('--project', required=True)
        if name in ('set-stage', 'configure', 'invalidate', 'next'):
            cmd.add_argument('--stage', required=name != 'next')
        if name in ('set-stage', 'invalidate'):
            cmd.add_argument('--reason')
        if name == 'init':
            cmd.add_argument('--name', default='ml-project')
            cmd.add_argument('--goal', default='')
            cmd.add_argument('--notebook', default=common.DEFAULT_NOTEBOOK)
        elif name == 'show':
            cmd.add_argument('--summary', action='store_true')
        elif name == 'set-stage':
            cmd.add_argument('--status', default='running')
            cmd.add_argument('--outcome', choices=OUTCOMES)
            for flag in ('conclusion', 'question', 'decision', 'cell', 'rule-match'):
                cmd.add_argument('--'+flag, action='append', default=[])
        elif name == 'configure':
            cmd.add_argument('--depends-on', nargs='*', default=[])
        elif name == 'add-source':
            cmd.add_argument('--path', required=True)
            cmd.add_argument('--kind', default='csv')
    args = parser.parse_args(argv)
    try:
        if args.command == 'init':
            result = init_project(args.project, args.name, args.goal, args.notebook)
        elif args.command == 'show':
            result = load_state(args.project)
            if args.summary:
                result = {**{k: result[k] for k in ('version', 'revision', 'project')},
                          'stages': {k: {f: v[f] for f in ('status', 'outcome', 'reason', 'dependencies')}
                                     for k, v in result['stages'].items() if v['status'] != 'pending' or v['dependencies']}}
        elif args.command == 'set-stage':
            result = set_stage(args.project, args.stage, args.status, args.conclusion,
                               args.question, [json.loads(v) for v in args.decision],
                               args.cell, args.rule_match, args.outcome, args.reason)
        elif args.command == 'next':
            result = next_stage(args.project, args.stage)
        elif args.command == 'configure':
            result = configure_stage(args.project, args.stage, args.depends_on)
        elif args.command == 'invalidate':
            result = invalidate(args.project, args.stage, args.reason)
        else:
            result = add_source(args.project, args.path, args.kind)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError) as error:
        print(f'error: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
