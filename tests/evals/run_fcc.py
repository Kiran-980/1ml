"""Run installed FCC/Claude against a task-local, NVIDIA-only FCC HTTP adapter.

Requires the Python environment containing the user's installed free-claude-code.
Credentials stay in memory. No managed FCC settings, global server, or login is
changed. The installed API converters/provider runtime and Claude launcher are
used; admin, messaging and connected-account services are intentionally absent.
"""
import argparse
import asyncio
from contextlib import asynccontextmanager
from functools import partial
import json
import hashlib
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import threading
import time
try:
    from .eval_paths import run_directory
except ImportError:
    from eval_paths import run_directory

ROOT = Path(__file__).resolve().parents[2]
MODEL_REF = "nvidia_nim/nvidia/nemotron-3-ultra-550b-a55b"
MODEL_ID = "anthropic/" + MODEL_REF
ENTRYPOINTS = {
    "structural-missingness": "prepare", "unseen-sites": "evaluation",
    "fixed-origin-forecast": "lifecycle", "refit-after-calibration": "train",
    "production-unit-change": "operate", "deterministic-lookup": "frame",
    "clustered-mean": "statistics", "small-budget-tuning": "train",
    "underpowered-ab": "experiment", "capacity-overload": "validate",
    "immature-temporal-labels": "evaluation",
}


def native_transport_failure(report):
    """Classify transport evidence, never a low score or an answer mentioning 429."""
    for case in report.get("cases", []):
        for trials in case.get("arms", {}).values():
            for trial in trials:
                error = trial.get("error")
                if isinstance(error, str) and "API Error:" in error and re.search(r"\b429\b", error):
                    return "provider_rate_limit"
    return None


def local_settings(port):
    from free_claude_code.config.loader import get_settings
    from free_claude_code.config.settings import Settings
    original = get_settings()
    if not original.nvidia_nim_api_keys:
        raise RuntimeError("No NVIDIA key configured in FCC")
    return Settings(
        MODEL=MODEL_REF, NVIDIA_NIM_API_KEY=original.nvidia_nim_api_keys,
        ANTHROPIC_AUTH_TOKEN=original.proxy_auth_token,
        MODEL_FALLBACKS=[], HOST="127.0.0.1", PORT=port,
        PROXY_AUTH_ENABLED=True, MESSAGING_PLATFORM="none", FCC_OPEN_BROWSER=False,
        PROVIDER_RATE_LIMIT=1, PROVIDER_RATE_WINDOW=int(os.environ.get("FCC_EVAL_SPACING_SECONDS", "3")),
        PROVIDER_MAX_CONCURRENCY=1, PROVIDER_PROGRESS_TIMEOUT=120,
        LOG_RAW_API_PAYLOADS=False,
    )


def client(port, args):
    from free_claude_code.cli.launchers import runner
    from free_claude_code.cli.launchers.claude import launch
    settings = local_settings(port)
    runner.get_settings = lambda: settings  # Process-local launch context only.
    launch(args)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--client", type=int)
    parser.add_argument("--run", default="fcc-smoke")
    parser.add_argument("--timeout", type=int, default=360)
    parser.add_argument("--spacing-seconds", type=int, default=3)
    parser.add_argument("--output-dir", type=Path, help="New local evaluation log directory under evals/")
    parser.add_argument("--workdir", type=Path, help="Existing actor workspace under evals/")
    parser.add_argument("--prompt-file", type=Path, help="Append a UTF-8 task prompt to the Claude arguments")
    parser.add_argument("--isolated-config", action="store_true", help="Use a fresh Claude config directory for direct runs")
    parser.add_argument("--cases", nargs="+", help="Run these native cases sequentially")
    parser.add_argument("--explicit", action="store_true", help="Diagnostic invocation arm, separate from discovery")
    parser.add_argument("claude_args", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    cli_args = args.claude_args
    if cli_args and cli_args[0] == "--":
        cli_args = cli_args[1:]
    if args.client:
        client(args.client, cli_args)
        return
    if not 3 <= args.spacing_seconds <= 60:
        parser.error("spacing-seconds must be between 3 and 60")
    os.environ["FCC_EVAL_SPACING_SECONDS"] = str(args.spacing_seconds)
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", args.run):
        parser.error("run must be a lowercase slug")
    for case in args.cases or []:
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", case) or not (
                ROOT / "tests/evals" / case / "case.yaml").is_file():
            parser.error("unknown case or invalid case slug")
    run = run_directory(ROOT, args.run)
    if args.output_dir:
        run = args.output_dir.resolve()
        if not run.is_relative_to((ROOT / 'evals').resolve()):
            parser.error('output-dir must be inside this project evals directory')
        if any(c in str(run) for c in '()[]{}*?!#'):
            parser.error('output-dir contains permission-pattern metacharacters')
    run.mkdir(parents=True, exist_ok=False)
    tmp = run / "tmp"
    tmp.mkdir()
    if args.workdir:
        work = args.workdir.resolve()
        if not work.is_dir() or not work.is_relative_to((ROOT / 'evals').resolve()):
            parser.error('workdir must be an existing directory under evals/')
    else:
        work = run / "workspace"
        work.mkdir()
    if args.prompt_file:
        cli_args.append(args.prompt_file.read_text(encoding='utf-8'))
    eval_dir = "tests/evals"
    if args.explicit:
        generated = run / "cases"
        generated.mkdir()
        for case in args.cases or []:
            data = json.loads((ROOT / "tests/evals" / case / "case.yaml").read_text())
            if case in ENTRYPOINTS:
                data["execution"]["prompt"] = (f"Use the 1ml:{ENTRYPOINTS[case]} skill to answer this request.\n\n"
                                                  + data["execution"]["prompt"])
            data["plugins"] = ["../../../../.."]
            folder = generated / case
            folder.mkdir()
            (folder / "case.yaml").write_text(json.dumps(data, indent=2), encoding="utf-8")
        eval_dir = generated.relative_to(ROOT).as_posix()
    from loguru import logger
    logger.remove()
    logger.add(str(run / "fcc.log"), level="INFO", encoding="utf-8")
    from free_claude_code.api.app import create_app
    from free_claude_code.api.ports import ApiServices
    from free_claude_code.providers.runtime.runtime import ProviderRuntime, create_provider
    from free_claude_code.runtime.provider_manager import ProviderRuntimeManager
    from free_claude_code.runtime.web_tools.client import HTTPWebToolsClient
    import uvicorn
    from starlette.responses import JSONResponse

    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    port = listener.getsockname()[1]
    settings = local_settings(port)

    async def nvidia_only(provider_id, config, admission, api_key_number=1):
        if provider_id != "nvidia_nim":
            raise RuntimeError("Evaluation permits only NVIDIA")
        return await create_provider(provider_id, config, admission, api_key_number)

    manager = ProviderRuntimeManager(settings, runtime_factory=partial(
        ProviderRuntime, provider_constructor=nvidia_only))
    services = ApiServices(requests=manager, admin=None, tasks=None,
                           web_tools=HTTPWebToolsClient())
    app = create_app(services)

    @asynccontextmanager
    async def lifespan(_app):
        try:
            yield
        finally:
            await manager.close()
    app.router.lifespan_context = lifespan

    @app.middleware("http")
    async def bounded_api(request, call_next):
        allowed = {"/health", "/v1/models", "/v1/messages", "/v1/messages/count_tokens"}
        if request.url.path not in allowed:
            return JSONResponse({"error": "route excluded from evaluation"}, status_code=403)
        before = time.monotonic()
        requested_model = None
        if request.method == "POST":
            body = await request.json()
            requested_model = body.get("model")
        response = await call_next(request)
        with (run / "requests.jsonl").open("a", encoding="utf-8") as output:
            output.write(json.dumps({"path": request.url.path, "model": requested_model,
                "status": response.status_code, "headers_seconds": time.monotonic()-before,
                "at": time.time()}) + "\n")
        return response

    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port,
        log_level="error", access_log=False, timeout_graceful_shutdown=5))
    thread = threading.Thread(target=lambda: server.run(sockets=[listener]), daemon=True)
    thread.start()
    deadline = time.monotonic() + 15
    while not server.started and thread.is_alive() and time.monotonic() < deadline:
        time.sleep(.1)
    if not server.started:
        raise RuntimeError("Isolated FCC adapter did not start")
    env = dict(os.environ)
    env.update(TEMP=str(tmp), TMP=str(tmp), TMPDIR=str(tmp), PYTHONUTF8="1")
    if args.isolated_config:
        config_dir = run / 'claude-config'
        config_dir.mkdir()
        env['CLAUDE_CONFIG_DIR'] = str(config_dir)
    # Native plugin eval establishes its own child configuration isolation.
    command = [sys.executable, "-X", "utf8", str(Path(__file__).resolve()),
               "--client", str(port), "--", *cli_args]
    manifest = {"model": MODEL_ID, "fallbacks": [], "provider": "nvidia_nim",
                "request_spacing_seconds": args.spacing_seconds, "max_concurrency": 1,
                "temp": str(tmp), "claude_args": cli_args, "started_at": time.time()}
    manifest['workspace'] = str(work)
    manifest['isolated_config'] = args.isolated_config
    manifest["invocation_mode"] = "explicit" if args.explicit else "implicit"
    manifest["case_hashes"] = {case: hashlib.sha256(
        (ROOT / eval_dir / case / "case.yaml").read_bytes()).hexdigest() for case in args.cases or []}
    manifest["runner_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    manifest["source_hashes"] = {p.relative_to(ROOT).as_posix():
        hashlib.sha256(p.read_bytes()).hexdigest()
        for folder in ["skills", "references", "tools", "rules", ".claude-plugin"]
        for p in sorted((ROOT / folder).rglob("*"))
        if p.is_file() and "__pycache__" not in p.parts}
    (run / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"NVIDIA-only FCC adapter ready; run={args.run}", flush=True)
    process = None
    code = 1
    try:
        code = 0
        manifest["cases"] = []
        for case in args.cases or [None]:
            log_dir = run / case if case else run
            log_dir.mkdir(exist_ok=True)
            if case:
                case_args = ["plugin", "eval", str(ROOT), "--eval-dir", eval_dir,
                    "--case", case, "--runs", "1", "--ablation", "none", "--no-publish",
                    "--trust-plugin", "--keep-temp", "--model", MODEL_ID,
                    "--judge-model", MODEL_ID, "--output-dir", str(log_dir / "report")]
                command = [sys.executable, "-X", "utf8", str(Path(__file__).resolve()),
                           "--client", str(port), "--", *case_args]
                print(f"Starting {case}", flush=True)
            with (log_dir / "stdout.log").open("wb") as out, (log_dir / "stderr.log").open("wb") as err:
                process = subprocess.Popen(command, cwd=work, env=env, stdout=out, stderr=err,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                try:
                    result = process.wait(timeout=args.timeout)
                except subprocess.TimeoutExpired:
                    # Stop only this owned launcher and its descendants, never other FCC sessions.
                    subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    result = 124
            if result:
                code = result
            manifest["cases"].append({"case": case, "exit_code": result,
                                      "finished_at": time.time()})
            (run / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            print(f"Case {case or 'command'} finished exit={result}", flush=True)
            report = log_dir / "report" / "aggregate-result.json"
            if case and report.is_file():
                blocked = native_transport_failure(json.loads(report.read_text(encoding="utf-8")))
                if blocked:
                    manifest["blocked_by"] = blocked
                    manifest["not_run"] = (args.cases or [])[len(manifest["cases"]):]
                    code = code or 1
                    print(f"Stopping batch: {blocked}; remaining cases are not run, not failed scores.", flush=True)
                    break
    finally:
        server.should_exit = True
        thread.join(timeout=15)
        listener.close()
        manifest.update(exit_code=code, finished_at=time.time())
        (run / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Finished exit={code}; artifacts={run}", flush=True)
    raise SystemExit(code)


if __name__ == "__main__":
    main()
