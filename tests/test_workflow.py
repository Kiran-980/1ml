"""Behavior contracts for dependency routing and recoverable notebook writes."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import common
import state
import render
import append_cells


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        state.init_project(self.root)

    def test_direct_data_entry_and_no_go_completion(self):
        result = state.set_stage(self.root, 'data', 'complete', outcome='collect_data',
                                 conclusions=['Source lacks mature outcomes.'])
        self.assertEqual(result['outcome'], 'collect_data')
        self.assertEqual(state.load_state(self.root)['stages']['frame']['status'], 'pending')
        self.assertIsNone(state.next_stage(self.root, 'data')['stage'])

    def test_dependencies_block_completion_and_invalidate_transitively(self):
        state.configure_stage(self.root, 'train', ['evaluation'])
        state.configure_stage(self.root, 'validate', ['train'])
        with self.assertRaises(state.GateError):
            state.set_stage(self.root, 'train', 'complete', conclusions=['Not enough evidence.'])
        self.assertEqual(state.next_stage(self.root, 'train')['stage'], 'evaluation')
        for name in ['evaluation', 'train', 'validate']:
            state.set_stage(self.root, name, 'complete', conclusions=['Verified evidence reference.'])
        state.invalidate(self.root, 'evaluation', 'Split changed')
        saved = state.load_state(self.root)
        for name in ['evaluation', 'train', 'validate']:
            self.assertEqual(saved['stages'][name]['status'], 'stale')
            self.assertTrue(saved['stages'][name]['history'])
        self.assertEqual(saved['stages']['data']['status'], 'pending')

    def test_cycle_rejected_without_mutating_state(self):
        state.configure_stage(self.root, 'train', ['prepare'])
        before = (self.root/'1ml/state.json').read_bytes()
        with self.assertRaises(state.GateError):
            state.configure_stage(self.root, 'prepare', ['train'])
        self.assertEqual(before, (self.root/'1ml/state.json').read_bytes())

    def test_init_never_overwrites_and_stale_writer_rejected(self):
        with self.assertRaises(FileExistsError):
            state.init_project(self.root)
        old = state.load_state(self.root)
        state.add_source(self.root, 'data.csv')
        with self.assertRaises(state.GateError):
            state.save_state(self.root, old)
        self.assertEqual(len(state.load_state(self.root)['sources']), 1)

    def test_completion_requires_evidence_and_skip_requires_reason(self):
        with self.assertRaises(state.GateError):
            state.set_stage(self.root, 'data', 'complete')
        with self.assertRaises(state.GateError):
            state.set_stage(self.root, 'experiment', 'not_applicable')
        state.set_stage(self.root, 'experiment', 'not_applicable', reason='No intervention claim.')

    def test_migration_preserves_legacy_and_does_not_certify_old_fit(self):
        legacy = {'version': 1, 'project': {'name': 'old'}, 'sources': [],
                  'stages': {'model': {'status': 'done', 'conclusions': ['old fit'], 'cells': ['c1']}}}
        path = self.root/'1ml/state.json'
        path.write_text(json.dumps(legacy), encoding='utf-8')
        migrated = state.load_state(self.root)
        self.assertEqual(migrated['version'], 2)
        self.assertEqual(migrated['stages']['train']['status'], 'stale')
        self.assertEqual(migrated['legacy_stages'], legacy['stages'])
        self.assertEqual(json.loads(path.read_text())['version'], 1)
        state.save_state(self.root, migrated)
        self.assertEqual(json.loads((self.root/'1ml/state.v1.json').read_text()), legacy)


class NotebookBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.nb = self.root/'analysis.ipynb'
        state.init_project(self.root, notebook='analysis.ipynb')
        self.plan = {'stage': 'data', 'cells': [{'id': 'load', 'type': 'code', 'source': 'x = 1'}]}

    def test_forward_or_circular_dependency_rejected(self):
        plan = copy.deepcopy(self.plan)
        plan['cells'][0]['depends_on'] = ['later']
        plan['cells'].append({'id': 'later', 'type': 'code', 'source': 'y = 2', 'depends_on': ['load']})
        with self.assertRaises(render.PlanError):
            render.render_plan(plan, self.nb)
        self.assertFalse(self.nb.exists())

    def test_changed_existing_id_preserves_user_edit_and_rejects(self):
        render.render_plan(self.plan, self.nb)
        nb = append_cells.load_notebook(self.nb)
        nb.cells[0].source = 'x = 99 # user edit'
        import nbformat
        nbformat.write(nb, self.nb)
        with self.assertRaises(ValueError):
            render.render_plan(self.plan, self.nb)
        self.assertEqual(append_cells.load_notebook(self.nb).cells[0].source, 'x = 99 # user edit')

    def test_retry_after_state_failure_records_existing_cells(self):
        with patch.object(state, 'record_stage', side_effect=RuntimeError('interrupted')):
            with self.assertRaises(RuntimeError):
                render.render_plan(self.plan, self.nb, self.root, 'data')
        render.render_plan(self.plan, self.nb, self.root, 'data')
        saved = state.load_state(self.root)['stages']['data']
        self.assertEqual(saved['cells'], ['load'])
        self.assertEqual(saved['status'], 'pending')
        self.assertEqual(len(append_cells.load_notebook(self.nb).cells), 1)

    def test_stage_mismatch_rejected_before_write(self):
        with self.assertRaises(render.PlanError):
            render.render_plan(self.plan, self.nb, self.root, 'train')
        self.assertFalse(self.nb.exists())

    def test_active_notebook_writer_is_rejected(self):
        lock = self.nb.with_suffix(self.nb.suffix + '.lock')
        lock.write_text('another writer', encoding='utf-8')
        with self.assertRaises(FileExistsError):
            render.render_plan(self.plan, self.nb)
        self.assertFalse(self.nb.exists())

    def test_failed_atomic_notebook_replace_preserves_original(self):
        render.render_plan(self.plan, self.nb)
        original = self.nb.read_bytes()
        extra = {'stage': 'data', 'cells': [{'id': 'extra', 'type': 'code', 'source': 'y = 2'}]}
        with patch.object(Path, 'replace', side_effect=OSError('simulated full disk')):
            with self.assertRaises(OSError):
                render.render_plan(extra, self.nb)
        self.assertEqual(self.nb.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()


class DataBoundaryTests(unittest.TestCase):
    def test_sqlite_limit_is_applied_and_missing_source_not_created(self):
        import sqlite3
        import data_profile as profile
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'source.db'
            with self.assertRaises(FileNotFoundError):
                profile.profile_frame(path, table='events', max_rows=2)
            self.assertFalse(path.exists())
            with sqlite3.connect(path) as con:
                con.execute('create table events (value integer)')
                con.executemany('insert into events values (?)', [(i,) for i in range(10)])
            con.close()
            facts = profile.profile_frame(path, table='events', max_rows=2)
            self.assertEqual(facts['dataset']['n_rows'], 2)
            self.assertEqual(facts['source']['max_rows'], 2)

    def test_nonfinite_profile_is_json_serializable_without_values_by_default(self):
        import pandas as pd
        import data_profile as profile
        facts = profile.profile_dataframe(pd.DataFrame({'x': [1.0, float('inf'), None],
                                                        'private': ['secret-a', 'secret-b', 'secret-a']}), {})
        serialized = json.dumps(facts, allow_nan=False)
        self.assertNotIn('secret-a', serialized)
        self.assertEqual(facts['features'][0]['nonfinite_count'], 1)

    def test_row_limit_must_be_positive(self):
        import data_profile as profile
        with self.assertRaises(ValueError):
            profile.profile_frame('unused.csv', max_rows=-1)


class RuleRoutingTests(unittest.TestCase):
    def test_missingness_is_investigation_not_imputation_or_forced_approval(self):
        import match_rules
        rules = match_rules.load_rules(Path(__file__).resolve().parents[1]/'rules/preprocess.yaml')
        facts = {'features': [{'name': 'income', 'kind': 'numeric', 'missing_fraction': 0.8}]}
        results = match_rules.match_rules(facts, rules)
        self.assertTrue(results['matched'])
        for row in results['details']:
            self.assertEqual(row['recommend']['action'], 'inspect')
            self.assertFalse(row['escalate'])
            self.assertTrue(row.get('reference'))
