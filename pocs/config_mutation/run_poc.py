"""POC 7: new runs use current config; past runs keep frozen config snapshot."""

from __future__ import annotations

import copy
import json
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ConfigStore:
    current: dict[str, Any] = field(
        default_factory=lambda: {"risk_per_trade": 0.01}
    )

    def set_risk(self, v: float) -> None:
        self.current["risk_per_trade"] = v


@dataclass
class Run:
    run_id: str
    config_snapshot: dict[str, Any]


def run_backtest(
    _data: int, store: ConfigStore, runlog: list[Run]
) -> None:
    snap = copy.deepcopy(store.current)
    rid = f"run-{len(runlog) + 1:03d}"
    runlog.append(Run(run_id=rid, config_snapshot=snap))


def main() -> None:
    store = ConfigStore()
    log: list[Run] = []
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        run_backtest(1, store, log)
        (base / f"{log[0].run_id}").mkdir()
        (base / f"{log[0].run_id}" / "config.json").write_text(
            json.dumps(log[0].config_snapshot, sort_keys=True, indent=2)
        )
        store.set_risk(0.05)
        run_backtest(1, store, log)
        (base / f"{log[1].run_id}").mkdir()
        (base / f"{log[1].run_id}" / "config.json").write_text(
            json.dumps(log[1].config_snapshot, sort_keys=True, indent=2)
        )
        on_disk_1 = json.loads(
            (base / f"{log[0].run_id}" / "config.json").read_text()
        )
        on_disk_2 = json.loads(
            (base / f"{log[1].run_id}" / "config.json").read_text()
        )
    assert on_disk_1["risk_per_trade"] == 0.01
    assert on_disk_2["risk_per_trade"] == 0.05
    assert store.current["risk_per_trade"] == 0.05
    print("POC7_OK: first run snapshot frozen; second run and global config at 5%")


if __name__ == "__main__":
    main()
