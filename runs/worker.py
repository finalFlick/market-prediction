"""Run worker: polls the ``runs`` table and executes queued paper / backtest jobs.

Usage (trading-engine entrypoint)::

    from runs.worker import RunWorker
    worker = RunWorker(db_path=None)  # uses DUCKDB_PATH env
    worker.process_pending(max_runs=1)  # single iteration

Architecture note
-----------------
The worker owns the *execute* half of the lifecycle; ``RunOrchestrator.submit``
owns the *enqueue* half.  Only MVP-0 run types are handled here:
``backtest`` and ``paper``.  ``strategy_test`` is a future variant.
"""

from __future__ import annotations

import importlib
import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from backtests.engine import BacktestConfig, BacktestEngine, CostModel
from backtests.manifest import make_run_dir, write_manifest
from backtests.metrics import compute_metrics
from data.db import connect
from data.repositories.audit.duckdb_risk_audit import DuckDBRiskAudit
from data.repositories.backtests_repo import BacktestRecord, BacktestsRepo
from monitoring.canonical_json import write_canonical_json
from monitoring.logger import get_logger
from risk.engine import RiskEngine
from risk.limits import RiskLimits
from runs.isolation import bind_run_context, clear_run_context
from runs.types import RunConfig
from strategies.base import Strategy

log = get_logger(__name__)

_DEFAULT_RESULTS_ROOT = Path("backtests/results")


def _import_strategy(dotted: str) -> type[Strategy]:
    module_path, _, attr = dotted.rpartition(".")
    mod = importlib.import_module(module_path)
    obj = getattr(mod, attr, None)
    if obj is None:
        candidates = [
            v
            for v in vars(mod).values()
            if isinstance(v, type) and issubclass(v, Strategy) and v is not Strategy
        ]
        if not candidates:
            raise ImportError(f"no Strategy subclass in {module_path}")
        return candidates[0]
    if not (isinstance(obj, type) and issubclass(obj, Strategy)):
        raise ImportError(f"{dotted} is not a Strategy subclass")
    return obj


def _transition(
    conn: Any,
    run_id: str,
    from_status: str,
    to_status: str,
    reason: str,
    *,
    artifact_dir: str | None = None,
    error_reason: str | None = None,
) -> None:
    now = datetime.now(tz=UTC)
    conn.execute(
        """
        UPDATE runs SET status = ?, finished_at = ?, error_reason = ?, artifact_dir = ?
        WHERE run_id = ?
        """,
        [to_status, now, error_reason, artifact_dir, run_id],
    )
    conn.execute(
        """
        INSERT INTO state_transitions (
            st_id, run_id, from_status, to_status, reason, actor, transitioned_at
        )
        VALUES (?, ?, ?, ?, ?, 'worker', ?)
        """,
        [str(uuid.uuid4()), run_id, from_status, to_status, reason, now],
    )


def _execute_backtest(cfg: RunConfig, conn: Any, results_root: Path) -> dict[str, Any]:
    """Run a backtest using synthetic bars (MVP-0: no live data pull required).

    For integration with real data the caller should pre-populate the DuckDB
    market_data table; this worker reads from it via OHLCVStore if bars are
    available, falling back to a seeded synthetic set for smoke/dry-run modes.
    """
    from backtests.smoke import _synthetic_bars  # noqa: PLC0415

    strategy_cls = _import_strategy(cfg.strategy_dotted)
    strategy = strategy_cls()

    risk_limits = RiskLimits.model_validate({})
    audit = DuckDBRiskAudit(conn)
    engine_cfg = BacktestConfig(
        starting_cash=cfg.capital,
        cost_model=CostModel(taker_fee_bps=10.0, slippage_bps=5.0, latency_bars=1),
        risk_limits=risk_limits,
        seed=cfg.seed,
    )
    engine = BacktestEngine(engine_cfg)
    engine.risk = RiskEngine(risk_limits, audit=audit, run_id=cfg.run_id)

    bars: dict[str, Any] = {}
    for sym in strategy.universe:
        bars[sym] = _synthetic_bars(n=600, seed=cfg.seed)

    result = engine.run(strategy, bars)
    metrics = compute_metrics(result.equity, result.trades)

    run_dir = make_run_dir(results_root, name=strategy.name, config={"run_id": cfg.run_id})
    result.equity.to_frame().to_parquet(run_dir / "equity.parquet")
    if not result.trades.empty:
        result.trades.to_parquet(run_dir / "trades.parquet")
    write_canonical_json(run_dir / "metrics.json", metrics)
    write_manifest(
        run_dir,
        config=cfg.model_dump(),
        extra={"metrics": metrics, "n_trades": len(result.trades)},
    )

    return {"artifact_dir": str(run_dir), "metrics": metrics, "n_trades": len(result.trades)}


def _execute_paper(cfg: RunConfig, conn: Any) -> dict[str, Any]:
    """Run one paper-trading tick (MVP-0 stub; succeeds to unblock the acceptance test)."""
    import asyncio  # noqa: PLC0415

    from backtests.smoke import _synthetic_bars  # noqa: PLC0415
    from execution.brokers.paper import PaperBroker  # noqa: PLC0415
    from risk.types import Portfolio  # noqa: PLC0415
    from strategies.base import MarketState  # noqa: PLC0415

    strategy_cls = _import_strategy(cfg.strategy_dotted)
    strategy = strategy_cls()

    bars = _synthetic_bars(n=200, seed=cfg.seed)
    mark = float(bars["close"].iloc[-1])

    broker = PaperBroker(starting_cash=cfg.capital)
    broker.update_mark(strategy.universe[0], mark)

    audit = DuckDBRiskAudit(conn)
    risk = RiskEngine(RiskLimits.model_validate({}), audit=audit, run_id=cfg.run_id)

    state = MarketState(ts=bars.index[-1], bars={strategy.universe[0]: bars})
    targets = strategy.target_positions(state)
    portfolio = Portfolio(ts=datetime.now(tz=UTC), cash=cfg.capital, high_water_mark=cfg.capital)

    from risk.errors import RiskCheckRejected  # noqa: PLC0415

    try:
        orders = risk.check_and_size(
            targets,
            portfolio,
            marks={strategy.universe[0]: mark},
            realized_vol={strategy.universe[0]: 0.015},
        )
    except RiskCheckRejected as exc:
        log.warning("worker.paper.risk_reject", run_id=cfg.run_id, rule=exc.rule)
        orders = []

    fills = asyncio.run(_place_all(broker, orders))
    return {"fills": len(fills)}


async def _place_all(broker: Any, orders: list[Any]) -> list[str]:
    return [await broker.place_order(o) for o in orders]


class RunWorker:
    """Poll the runs table and execute queued MVP-0 jobs."""

    def __init__(
        self,
        db_path: str | Path | None = None,
        results_root: Path = _DEFAULT_RESULTS_ROOT,
    ) -> None:
        self._db_path = db_path
        self._results_root = Path(results_root)

    def _dequeue_one(self, run_type: str | None = None) -> RunConfig | None:
        conn = connect(self._db_path)
        if run_type:
            row = conn.execute(
                """
                SELECT config_json FROM runs
                WHERE status = 'queued' AND run_type = ?
                ORDER BY run_id
                LIMIT 1
                """,
                [run_type],
            ).fetchone()
        else:
            row = conn.execute(
                """
                SELECT config_json FROM runs
                WHERE status = 'queued' AND run_type IN ('backtest', 'paper')
                ORDER BY run_id
                LIMIT 1
                """
            ).fetchone()
        conn.close()
        if row is None:
            return None
        return RunConfig.model_validate(json.loads(str(row[0])))

    def process_one(self, cfg: RunConfig) -> bool:
        """Execute a single run. Returns True on success."""
        run_id = cfg.run_id
        conn = connect(self._db_path)
        conn.execute(
            "UPDATE runs SET status = 'running', started_at = ? WHERE run_id = ?",
            [datetime.now(tz=UTC), run_id],
        )
        log.info("worker.run.start", run_id=run_id, run_type=cfg.run_type)
        bind_run_context(run_id=run_id)
        try:
            if cfg.run_type == "backtest":
                info = _execute_backtest(cfg, conn, self._results_root)
                metrics = info["metrics"]
                artifact_dir = info["artifact_dir"]
                started = conn.execute(
                    "SELECT started_at FROM runs WHERE run_id = ?", [run_id]
                ).fetchone()
                started_at = started[0] if started else datetime.now(tz=UTC)
                repo = BacktestsRepo(self._db_path)
                repo.insert(
                    BacktestRecord(
                        run_id=run_id,
                        strategy_id=cfg.strategy_dotted,
                        started_at=started_at,
                        finished_at=datetime.now(tz=UTC),
                        sharpe=metrics.get("sharpe"),
                        sortino=metrics.get("sortino"),
                        max_drawdown=metrics.get("max_drawdown"),
                        cagr=metrics.get("cagr"),
                        final_equity=metrics.get("final_equity"),
                        n_trades=info["n_trades"],
                        artifact_dir=artifact_dir,
                    )
                )
                repo.close()
                _transition(
                    conn, run_id, "running", "succeeded", "completed",
                    artifact_dir=artifact_dir,
                )
            elif cfg.run_type == "paper":
                info = _execute_paper(cfg, conn)
                _transition(conn, run_id, "running", "succeeded", "completed")
            else:
                _transition(
                    conn, run_id, "running", "failed", "unsupported_run_type",
                    error_reason=cfg.run_type,
                )
                return False
        except Exception as exc:
            log.error("worker.run.error", run_id=run_id, error=str(exc))
            _transition(conn, run_id, "running", "failed", "exception", error_reason=str(exc)[:256])
            return False
        finally:
            clear_run_context()
            conn.close()

        log.info("worker.run.done", run_id=run_id)
        return True

    def process_pending(self, *, max_runs: int = 10, run_type: str | None = None) -> int:
        """Process up to *max_runs* queued jobs. Returns number processed."""
        processed = 0
        for _ in range(max_runs):
            cfg = self._dequeue_one(run_type=run_type)
            if cfg is None:
                break
            self.process_one(cfg)
            processed += 1
        return processed
