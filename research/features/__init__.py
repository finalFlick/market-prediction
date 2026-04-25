"""Point-in-time feature library.

Each submodule exposes pure functions that take a UTC-indexed OHLCV
DataFrame and return one or more named feature columns. Functions MUST be
shift-safe — feature at row `t` may only depend on rows `<= t`.
"""
