"""Focused checks for the audit boundary and reusable native case inputs."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from tests.evals.eval_paths import run_directory
from tests.evals.summarize_native import summarize
from tests.evals.run_fcc import native_transport_failure

ROOT = Path(__file__).resolve().parents[1]
READER = ROOT / "tests/evals/read_resource.py"


class EvalHarnessTests(unittest.TestCase):
    def test_transport_block_is_distinct_from_scientific_failure(self):
        def report(trial):
            return {"cases": [{"arms": {"with": [trial]}}]}
        self.assertEqual(native_transport_failure(report({
            "error": "exit 1: API Error: Request rejected (429)"})), "provider_rate_limit")
        self.assertIsNone(native_transport_failure(report({"score": 0, "error": None})))
        self.assertIsNone(native_transport_failure(report({"answer": "Retry on HTTP 429", "score": 1})))
        self.assertIsNone(native_transport_failure(report({"error": "Permission to read denied"})))

    def test_native_summary_retains_failed_calls_and_tolerates_status_messages(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            trace = root / "trace.jsonl"
            events = [
                {"type": "system", "message": "waiting for server"},
                {"type": "assistant", "message": {"content": [
                    {"type": "tool_use", "id": "call1", "name": "Skill",
                     "input": {"skill": "nonexistent"}}]}},
                {"type": "user", "message": {"content": [
                    {"type": "tool_result", "tool_use_id": "call1", "is_error": True,
                     "content": "Unknown skill"}]}},
                {"type": "result", "result": "Answer"}]
            trace.write_text("\n".join(json.dumps(e) for e in events), encoding="utf-8")
            report = root / "report.json"
            report.write_text(json.dumps({"cases": [{"name": "test", "arms": {"with": [
                {"tracePath": str(trace), "score": 1, "graders": []}]}}]}))
            result = summarize(report)[0]
            self.assertTrue(result["calls"][0]["result"]["is_error"])
            self.assertEqual(result["answer"], "Answer")

    def test_run_directory_excludes_cases_and_unsafe_patterns(self):
        target = run_directory(ROOT, "native-test")
        self.assertTrue(target.is_relative_to(ROOT))
        self.assertFalse(target.is_relative_to(ROOT / "tests/evals"))
        with self.assertRaises(ValueError):
            run_directory(ROOT, "../escape")
        with self.assertRaisesRegex(ValueError, "metacharacters"):
            run_directory(ROOT / "sandbox.{example}", "native-test")

    def test_reader_records_exact_loaded_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            (run / "plugin").mkdir()
            content = "# Test\nA decision with a → branch.\n".encode("utf-8")
            (run / "plugin/resource.md").write_bytes(content)
            result = subprocess.run([sys.executable, "-X", "utf8", str(READER),
                                     str(run), "resource.md"], capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(content, result.stdout.replace(b"\r\n", b"\n"))
            record = json.loads((run / "reads.jsonl").read_text())
            self.assertEqual(record["sha256"], hashlib.sha256(content).hexdigest())
            self.assertEqual(record["bytes"], len(content))
            self.assertEqual(record["path"], "resource.md")

    def test_reader_rejects_paths_outside_plugin(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            (run / "plugin").mkdir()
            (run / "answer-key.txt").write_text("DO NOT EXPOSE")
            result = subprocess.run([sys.executable, "-X", "utf8", str(READER),
                                     str(run), "../answer-key.txt"], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn(b"DO NOT EXPOSE", result.stdout + result.stderr)
            self.assertFalse((run / "reads.jsonl").exists())

    def test_cases_have_separate_prompts_and_graders(self):
        paths = sorted((ROOT / "tests/evals").glob("*/case.yaml"))
        self.assertEqual(len(paths), 12)
        for path in paths:
            with self.subTest(case=path.parent.name):
                case = json.loads(path.read_text())  # JSON is valid YAML.
                self.assertEqual(case["schema_version"], "1.1")
                self.assertEqual(case["name"], path.parent.name)
                self.assertEqual((path.parent / case["plugins"][0]).resolve(), ROOT)
                self.assertTrue(case["execution"]["prompt"])
                self.assertTrue(case["graders"])
                self.assertNotIn("append_system_prompt", case["execution"])
                self.assertTrue(set(case["execution"]["allowed_tools"]) <=
                                {"Read", "Glob", "Grep", "Skill"})

    def test_probe_rejects_escaping_run_name_before_writing(self):
        result = subprocess.run([sys.executable, str(ROOT / "tests/evals/prepare_probe.py"),
                                 "unseen-sites", "../escape"], capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn(b"lowercase slugs", result.stderr)


if __name__ == "__main__":
    unittest.main()
