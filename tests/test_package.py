"""Distribution checks run against a copy without local research files."""
import shutil
import tempfile
import unittest
from pathlib import Path
import sys
import subprocess
import json

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))


class PackageTests(unittest.TestCase):
    def test_host_manifests_share_version_and_skill_tree(self):
        claude = json.loads((ROOT/'.claude-plugin/plugin.json').read_text())
        codex = json.loads((ROOT/'.codex-plugin/plugin.json').read_text())
        gemini = json.loads((ROOT/'gemini-extension.json').read_text())
        pi = json.loads((ROOT/'package.json').read_text())
        for manifest in (codex, gemini, pi):
            self.assertEqual(manifest['name'], claude['name'])
            self.assertEqual(manifest['version'], claude['version'])
        self.assertEqual((ROOT/codex['skills']).resolve(), (ROOT/'skills').resolve())
        self.assertEqual([(ROOT/p).resolve() for p in pi['pi']['skills']], [(ROOT/'skills').resolve()])
        catalog = json.loads((ROOT/'.claude-plugin/marketplace.json').read_text())
        self.assertEqual(catalog['plugins'][0]['name'], claude['name'])
        self.assertEqual((ROOT/catalog['plugins'][0]['source']).resolve(), ROOT)

    def test_installed_copy_has_all_skill_reference_paths_without_research(self):
        import validate_plugin
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)/'plugin'
            ignored = shutil.ignore_patterns(
                '.runtime', 'notes', 'node_modules', '.test-tmp', '__pycache__', 'ml-lifecycle', 'ML-LIFECYCLE.md', '.git', '.claude', '.env', '.env.*')
            def ignore(path, names):
                excluded = set(ignored(path, names))
                if Path(path).resolve() == ROOT:
                    excluded.add('evals')
                if Path(path).resolve() == ROOT / 'tests/evals':
                    excluded.add('results')
                if Path(path).resolve() == ROOT / 'tests':
                    excluded.add('eval-runs')
                return excluded
            shutil.copytree(ROOT, package, ignore=ignore)
            report = validate_plugin.validate(package)
            self.assertEqual(report['errors'], [])
            self.assertEqual(report['skill_count'], 12)
            self.assertFalse((package/'ml-lifecycle').exists())
            self.assertFalse((package/'.env').exists())
            self.assertFalse((package/'tests/evals/results').exists())
            self.assertFalse((package/'tests/eval-runs').exists())
            self.assertFalse((package/'evals').exists())
            learner = Path(tmp)/'learner'
            learner.mkdir()
            def cli(tool, *args):
                result = subprocess.run([sys.executable, str(package/'tools'/tool), *map(str, args)],
                                        cwd=learner, capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stderr)
                return result
            cli('state.py', 'init', '--project', learner, '--goal', 'Package smoke test')
            (learner/'sample.csv').write_text('x,y\n1,0\n2,1\n3,0\n', encoding='utf-8')
            cli('data_profile.py', '--csv', learner/'sample.csv', '--max-rows', '2',
                '--out', learner/'1ml/artifacts/profile.json')
            facts = json.loads((learner/'1ml/artifacts/profile.json').read_text())
            self.assertEqual(facts['dataset']['n_rows'], 2)
            plan = learner/'plan.json'
            plan.write_text(json.dumps({'stage': 'evaluation', 'cells': [
                {'id': 'scope', 'type': 'markdown', 'source': 'Two-row head sample, not a population estimate.'}]}))
            cli('render.py', '--plan', plan, '--notebook', learner/'analysis.ipynb', '--project', learner)
            saved = json.loads((learner/'1ml/state.json').read_text())
            self.assertEqual(saved['stages']['evaluation']['cells'], ['scope'])
            self.assertEqual(saved['stages']['evaluation']['status'], 'pending')
            target = package/'skills/prepare/references/missingness.md'
            target.write_text(target.read_text(encoding='utf-8')+'\n[broken](not-shipped.md)\n', encoding='utf-8')
            self.assertTrue(any('not-shipped.md' in e for e in validate_plugin.validate(package)['errors']))

    def test_link_to_outside_package_is_rejected(self):
        import validate_plugin
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'skills/test').mkdir(parents=True)
            (root/'skills/test/SKILL.md').write_text(
                '---\nname: test\ndescription: A scoped task.\n---\n[escape](../../../outside.md)', encoding='utf-8')
            result = validate_plugin.validate(root)
            self.assertTrue(any('outside package' in e for e in result['errors']))
