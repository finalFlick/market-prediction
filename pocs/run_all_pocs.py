"""Run every POC under pocs/ and print one line per result."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

POCS: list[Path] = [
    Path("pocs/deterministic_backtest/run_poc.py"),
    Path("pocs/risk_engine_bypass/run_poc.py"),
    Path("pocs/risk_engine_bypass/run_poc_real.py"),
    Path("pocs/artifact_replay/run_poc.py"),
    Path("pocs/event_stream/run_poc.py"),
    Path("pocs/paperbroker_simulation/run_poc.py"),
    Path("pocs/llm_isolation/run_poc.py"),
    Path("pocs/config_mutation/run_poc.py"),
    Path("pocs/learning_feedback/run_poc.py"),
    Path("pocs/signal_validity_experiments/run_poc.py"),
    Path("pocs/bonus_latency_pipeline/run_poc.py"),
]


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    code = 0
    for rel in POCS:
        p = root / rel
        r = subprocess.run(  # noqa: S603
            [sys.executable, str(p)],
            cwd=str(root),
            capture_output=True,
            text=True,
        )
        name = str(rel)
        if r.returncode == 0:
            out = (r.stdout or "").strip().splitlines()[-1] if r.stdout else ""
            print(f"OK  {name}")
            for line in (r.stdout or "").strip().splitlines():
                print(f"    {line}")
        else:
            print(f"FAIL {name} rc={r.returncode}")
            print(r.stderr or r.stdout)
            code = 1
    return code


if __name__ == "__main__":
    raise SystemExit(main())
