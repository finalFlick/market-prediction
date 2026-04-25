# Strategy Playbook

Defines the canonical strategy template, target metrics for promotion, and
the baseline strategy that ships with the repo.

## 1. Strategy template

A `Strategy` is a class implementing:

```python
class Strategy(Protocol):
    name: str
    universe: list[str]
    timeframe: str

    def target_positions(self, state: MarketState) -> dict[str, float]:
        """Return target weight in [-1, 1] per symbol. Sum |w| ≤ 1."""
```

Strategies do not place orders; they emit *target weights*. The risk engine
converts weights to orders.

## 2. Target metrics for promotion

A strategy may be promoted only if it passes **all** of:

| Metric                          | Threshold                          |
|---------------------------------|------------------------------------|
| In-sample net Sharpe            | > 1.0                              |
| Walk-forward net Sharpe         | > 0.7 on most recent 12 months     |
| Max drawdown                    | < 25%                              |
| Hit rate (closed trades)        | > 50%                              |
| Turnover                        | < 50× per year (cost-aware)        |
| Live-vs-backtest Sharpe drift   | < 30% over first 30 paper days     |
| `RiskAgent` review              | logged in `DECISIONS.md`           |

Numbers are net of fees, slippage, and (for perps) funding.

## 3. Baseline: `momentum_xover`

Reference implementation that exercises every part of the pipeline.

- **Universe**: BTCUSDT (Binance perps).
- **Timeframe**: 1h.
- **Signal**: LightGBM regressor predicting forward 4-bar log-return from
  classic price/volume features.
- **Entry**: long when predicted return > +threshold; short when < -threshold.
- **Exit**: when predicted return crosses zero or stop-loss / take-profit
  triggers via `risk.sizing`.
- **Sizing**: volatility-targeted (annualized 15% vol) capped at 1× equity.
- **Risk**: max gross 1.0, max per-symbol 1.0, daily loss stop -3%.

Runbook:

```bash
python -m research.features.build --symbol BTCUSDT --timeframe 1h
python -m research.models.train  --config configs/strategies/momentum_xover.yaml
python -m backtests.run          --strategy strategies.examples.momentum_xover \
                                 --config   configs/backtest.yaml
python -m execution.runner       --broker paper \
                                 --strategy strategies.examples.momentum_xover
```

## 4. Composing multiple signals

When more than one signal is in `live`, `strategies/composer.py` blends them.
Default policy: equal-volatility-contribution weighting, recomputed daily.
Document any deviation in `DECISIONS.md`.

## 5. Lifecycle and retirement

- A strategy whose live-vs-backtest drift exceeds the threshold for 5
  consecutive days is **automatically demoted** to paper by `MonitoringAgent`.
- A strategy that breaches its risk limits **twice** is **retired**; revival
  requires a fresh hypothesis row in `SIGNALS.md`.
