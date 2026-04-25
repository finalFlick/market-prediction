"""CLI: run a backtest from a YAML config and write artifacts."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any, cast

import click
import yaml

from backtests.engine import BacktestConfig, BacktestEngine, CostModel
from backtests.manifest import make_run_dir, write_manifest
from data.store import OHLCVStore
from data.types import Exchange, Timeframe
from monitoring.canonical_json import write_canonical_json
from monitoring.logger import get_logger
from risk.limits import RiskLimits
from strategies.base import Strategy

log = get_logger(__name__)


def _import_strategy(dotted: str) -> type[Strategy]:
    module_path, _, attr = dotted.rpartition(".")
    if not module_path:
        raise click.BadParameter(f"strategy must be 'module.ClassName', got '{dotted}'")
    mod = importlib.import_module(module_path)
    obj = getattr(mod, attr, None)
    if obj is None:
        # Allow `strategies.examples.momentum_xover` -> `MomentumXover` by convention.
        candidates = [
            value
            for value in vars(mod).values()
            if isinstance(value, type) and issubclass(value, Strategy) and value is not Strategy
        ]
        if not candidates:
            raise click.BadParameter(f"no Strategy subclass found in {module_path}")
        return candidates[0]
    if not (isinstance(obj, type) and issubclass(obj, Strategy)):
        raise click.BadParameter(f"{dotted} is not a Strategy subclass")
    return obj


def _load_yaml(path: Path) -> dict[str, Any]:
    raw = yaml.safe_load(path.read_text())
    return cast(dict[str, Any], raw)


@click.command()
@click.option(
    "--strategy",
    "strategy_dotted",
    required=True,
    help="e.g. strategies.examples.momentum_xover",
)
@click.option(
    "--config",
    "config_path",
    type=click.Path(exists=True, path_type=Path),
    required=True,
)
@click.option("--results-root", type=click.Path(path_type=Path), default="backtests/results")
def main(strategy_dotted: str, config_path: Path, results_root: Path) -> None:
    cfg = _load_yaml(config_path)

    strategy_cls = _import_strategy(strategy_dotted)
    strategy = strategy_cls(**cfg.get("strategy_params", {}))

    cost_cfg = cfg.get("costs", {})
    risk_cfg = cfg.get("risk", {})
    bt_cfg = BacktestConfig(
        starting_cash=float(cfg["capital"]),
        cost_model=CostModel(**cost_cfg),
        risk_limits=RiskLimits(**risk_cfg),
        vol_window=int(cfg.get("vol_window", 24)),
        seed=int(cfg.get("seed", 42)),
    )

    universe: list[str] = cfg["data"]["symbols"]
    exchange = Exchange(cfg["data"]["exchange"])
    timeframe = Timeframe(cfg["data"]["timeframe"])
    with OHLCVStore() as store:
        bars = {sym: store.read(exchange, sym, timeframe) for sym in universe}
    if any(df.empty for df in bars.values()):
        raise click.ClickException("one or more symbols have no bars in the store")

    engine = BacktestEngine(bt_cfg)
    result = engine.run(strategy, bars)

    run_dir = make_run_dir(results_root, name=strategy.name, config=cfg)
    result.equity.to_frame().to_parquet(run_dir / "equity.parquet")
    result.trades.to_parquet(run_dir / "trades.parquet")
    write_canonical_json(run_dir / "metrics.json", result.metrics)
    write_manifest(
        run_dir,
        config=cfg,
        extra={"metrics": result.metrics, "n_trades": len(result.trades)},
    )

    log.info("backtest.done", run_dir=str(run_dir), **result.metrics)


if __name__ == "__main__":
    main()
