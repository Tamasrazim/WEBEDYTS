#!/usr/bin/env python3
"""Launch WEBEDYTS and verify that its packaged editor page loads."""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import tempfile
from pathlib import Path


def stop_process_tree(process: subprocess.Popen[str]) -> None:
    """Stop the app and any CEF child processes if the smoke test hangs."""
    if process.poll() is not None:
        return

    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        return

    try:
        os.killpg(process.pid, signal.SIGTERM)
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    except ProcessLookupError:
        pass


def startup_diagnostics(marker: Path) -> str:
    """Collect the startup marker and CEF log when a native launch fails."""
    sections: list[str] = []

    if marker.is_file():
        try:
            sections.append(
                "Startup marker:\n" + marker.read_text(encoding="utf-8", errors="replace")
            )
        except OSError as error:
            sections.append(f"Could not read startup marker: {error}")
    else:
        sections.append("Startup marker: not created")

    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        runtime_root = Path(local_app_data) / "WEBEDYTS"
        if runtime_root.is_dir():
            for log_path in sorted(runtime_root.rglob("webedyts.log")):
                try:
                    log_text = log_path.read_text(encoding="utf-8", errors="replace")
                except OSError as error:
                    sections.append(f"Could not read {log_path}: {error}")
                    continue
                sections.append(
                    f"CEF log ({log_path}):\n{log_text[-12000:]}"
                )

    return "\n\n".join(sections)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--working-directory", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=45)
    args = parser.parse_args()

    executable = args.executable.resolve()
    working_directory = args.working_directory.resolve()
    if not executable.is_file():
        print(f"Native application was not found: {executable}", file=sys.stderr)
        return 2
    if not working_directory.is_dir():
        print(f"Runtime directory was not found: {working_directory}", file=sys.stderr)
        return 2
    if args.timeout_seconds < 5:
        print("Timeout must be at least five seconds.", file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory(prefix="webedyts-startup-") as temp:
        marker = Path(temp) / "startup-result.txt"
        command = [
            str(executable),
            "--webedyts-smoke-test",
            f"--webedyts-smoke-test-marker={marker}",
            "--disable-gpu",
        ]
        process = subprocess.Popen(
            command,
            cwd=working_directory,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            start_new_session=(os.name != "nt"),
        )
        try:
            output, _ = process.communicate(timeout=args.timeout_seconds)
        except subprocess.TimeoutExpired:
            stop_process_tree(process)
            output, _ = process.communicate()
            print(output[-12000:], file=sys.stderr)
            print(
                f"WEBEDYTS did not close after loading the editor within "
                f"{args.timeout_seconds} seconds.",
                file=sys.stderr,
            )
            return 1

        if output:
            print(output[-12000:])
        if process.returncode != 0:
            print(
                f"WEBEDYTS exited with code {process.returncode}.",
                file=sys.stderr,
            )
            print(startup_diagnostics(marker), file=sys.stderr)
            return 1
        if not marker.is_file():
            print(
                "WEBEDYTS exited without reporting that the editor page loaded.",
                file=sys.stderr,
            )
            print(startup_diagnostics(marker), file=sys.stderr)
            return 1

        result = {}
        for line in marker.read_text(encoding="utf-8").splitlines():
            key, separator, value = line.partition("=")
            if separator:
                result[key] = value

        if result.get("status") != "loaded":
            print(
                f"WEBEDYTS did not load the expected bundled editor page: {result}",
                file=sys.stderr,
            )
            return 1
        if not result.get("url", "").startswith("file://"):
            print(
                f"WEBEDYTS loaded an unexpected URL: {result.get('url', '')}",
                file=sys.stderr,
            )
            return 1

    print("WEBEDYTS native startup smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
