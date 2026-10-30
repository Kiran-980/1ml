"""Immutable, content-versioned inputs with run-local hard-link aliases.

Only immutable source inputs (including frozen plugin files) are interned. Never use this for notebooks, generated outputs,
model weights or mutable configuration. Existing notebook paths remain valid.
"""
import hashlib
import json
import os
from pathlib import Path
import stat
import uuid


def unlink_alias(path, workspace):
    """Delete one confined file without clearing shared Windows read-only flags."""
    path = within(path, workspace)
    if not path.is_file():
        raise ValueError('Expected a file alias')
    if os.name != 'nt' or path.stat().st_mode & stat.S_IWRITE:
        path.unlink()
        return
    import ctypes
    from ctypes import wintypes
    api = ctypes.WinDLL('kernel32', use_last_error=True)
    api.CreateFileW.argtypes = [wintypes.LPCWSTR,wintypes.DWORD,wintypes.DWORD,wintypes.LPVOID,wintypes.DWORD,wintypes.DWORD,wintypes.HANDLE]
    api.CreateFileW.restype = wintypes.HANDLE
    api.SetFileInformationByHandle.argtypes = [wintypes.HANDLE,ctypes.c_int,wintypes.LPVOID,wintypes.DWORD]
    api.SetFileInformationByHandle.restype = wintypes.BOOL
    api.CloseHandle.argtypes = [wintypes.HANDLE]
    handle = api.CreateFileW(str(path),0x10000,7,None,3,0x00200000,None)
    if handle == ctypes.c_void_p(-1).value: raise ctypes.WinError(ctypes.get_last_error())
    try:
        flags = wintypes.DWORD(1|2|16)
        if not api.SetFileInformationByHandle(handle,21,ctypes.byref(flags),ctypes.sizeof(flags)):
            raise ctypes.WinError(ctypes.get_last_error())
    finally:
        api.CloseHandle(handle)


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def within(path, root):
    path, root = Path(path).resolve(), Path(root).resolve()
    if not path.is_relative_to(root) or path == root:
        raise ValueError(f'Path outside allowed storage workspace: {path}')
    return path


def intern_input(path, store, workspace):
    """Preserve bytes, then atomically replace a duplicate with a read-only alias.

    Requires hard-link support on one filesystem; fail rather than silently copy.
    Changed content gets a new version. Do not modify or chmod shared aliases in
    place: create a new source version instead.
    """
    path = within(path, workspace)
    store = within(store, workspace)
    if not path.is_file():
        raise ValueError(f'Expected an input file: {path}')
    digest = sha256(path)
    canonical = store / digest / path.name
    canonical.parent.mkdir(parents=True, exist_ok=True)
    if canonical.exists():
        if sha256(canonical) != digest:
            raise ValueError(f'Static source identity mismatch: {canonical}')
    else:
        # Exclusive creation keeps a simultaneous writer from replacing a version.
        with canonical.open('xb') as target, path.open('rb') as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b''):
                target.write(chunk)
        if sha256(canonical) != digest:
            raise ValueError('Source changed during static publication; preserve and investigate')
    if not os.path.samefile(path, canonical):
        temporary = path.with_name(f'.{path.name}.{uuid.uuid4().hex}.link')
        try:
            os.link(canonical, temporary)
            if sha256(path) != digest:
                raise ValueError('Input changed during deduplication; original retained')
            os.replace(temporary, path)
        finally:
            if temporary.exists():
                temporary.unlink()
    # Windows maps this to the read-only attribute, shared by the hard links.
    canonical.chmod(stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)
    assert sha256(path) == digest and os.path.samefile(path, canonical)
    return {'path': str(path), 'static': str(canonical), 'sha256': digest,
            'bytes': path.stat().st_size, 'storage': 'read-only hard-link alias'}


def share_run_inputs(run, store, workspace):
    run = within(run, workspace)
    records = []
    for folder in ('inputs/data', 'inputs/docs'):
        for path in sorted((run / folder).glob('*')):
            if path.is_file():
                record = intern_input(path, store, workspace)
                record['path'] = path.relative_to(run).as_posix()
                record['static'] = os.path.relpath(record['static'], run).replace('\\', '/')
                records.append(record)
    manifest = run / 'inputs/storage.json'
    manifest.write_text(json.dumps({'policy': 'immutable inputs; new bytes create a new version',
                                    'files': records}, indent=2), encoding='utf-8')
    return records


def share_frozen_plugin(run, store, workspace):
    """Deduplicate a copied snapshot, never the editable repository plugin.

    Paths stay run-local for relative skill links; equal bytes share storage.
    The manifest is outside the snapshot and is not itself an immutable source.
    """
    run = within(run, workspace)
    plugin = within(run / 'agent/plugin', run)
    records = []
    for path in sorted(plugin.rglob('*')):
        if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
            record = intern_input(path, store, workspace)
            record['path'] = path.relative_to(run).as_posix()
            record['static'] = os.path.relpath(record['static'], run).replace('\\', '/')
            records.append(record)
    (run / 'agent/plugin-storage.json').write_text(json.dumps({
        'policy': 'immutable plugin source versions; editable repository files are never linked',
        'files': records}, indent=2), encoding='utf-8')
    return records
