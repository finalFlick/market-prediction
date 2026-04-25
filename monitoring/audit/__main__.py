"""`python -m monitoring.audit verify --tables critical`."""

from __future__ import annotations

import argparse
import json

from monitoring.audit.verifier import verify_all


def main() -> int:
    p = argparse.ArgumentParser(prog="python -m monitoring.audit")
    p.add_argument("command", choices=["verify"], help="verify: run hash-chain verification")
    p.add_argument(
        "--tables",
        choices=["critical", "all"],
        default="critical",
        help="MVP-0: five critical hash tables (same for critical vs all)",
    )
    p.add_argument(
        "--db",
        type=str,
        default=None,
        help="DuckDB path (default: DUCKDB_PATH or data/market.duckdb)",
    )
    args = p.parse_args()
    if args.command == "verify":
        out = verify_all(db_path=args.db, tables=args.tables)
        print(json.dumps(out, indent=2, sort_keys=True, default=str))
        return 0 if out.get("all_ok") else 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
