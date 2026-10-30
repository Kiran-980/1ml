"""Extract auditable outcomes from native eval reports without judging prose."""
import argparse
import json
from pathlib import Path


def summarize(report):
    data = json.loads(report.read_text(encoding="utf-8"))
    summaries = []
    for case in data["cases"]:
        for arm, trials in case["arms"].items():
            for trial in trials:
                raw_path = trial.get("tracePath", "")
                trace = Path(raw_path.replace("tests\\evals\\results", "tests\\eval-runs"))
                calls, results, final = {}, {}, ""
                if raw_path and trace.is_file():
                    for line in trace.read_text(encoding="utf-8").splitlines():
                        event = json.loads(line)
                        if event.get("type") == "result":
                            final = event.get("result", final)
                        message = event.get("message", {})
                        if not isinstance(message, dict):
                            continue
                        content = message.get("content", [])
                        if not isinstance(content, list):
                            continue
                        for block in content:
                            if block.get("type") == "tool_use":
                                calls[block["id"]] = {"tool": block["name"],
                                                      "input": block.get("input", {})}
                            elif block.get("type") == "tool_result":
                                results[block["tool_use_id"]] = {
                                    "is_error": bool(block.get("is_error")),
                                    "returned_chars": len(str(block.get("content", "")))}
                for key, call in calls.items():
                    call["result"] = results.get(key)
                summaries.append({"case": case["name"], "arm": arm,
                    "native_score": trial.get("score"), "error": trial.get("error"),
                    "duration_seconds": trial.get("durationSeconds"),
                    "failed_graders": [g["name"] for g in trial.get("graders", [])
                                       if not g.get("passed")],
                    "calls": list(calls.values()), "answer": final,
                    "report": str(report), "trace": str(trace) if raw_path else None})
    return summaries


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    reports = sorted(args.run.glob("*/report/aggregate-result.json"))
    direct = args.run / "report/aggregate-result.json"
    if direct.is_file():
        reports.append(direct)
    summaries = [r for p in reports for r in summarize(p)]
    (args.run / "review-input.json").write_text(json.dumps(summaries, indent=2), encoding="utf-8")
    for row in summaries:
        print(json.dumps({k: v for k, v in row.items() if k not in ["answer", "report", "trace"]}))


if __name__ == "__main__":
    main()
