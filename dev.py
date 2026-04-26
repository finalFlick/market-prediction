"""Developer helper for the trading-lab dockerized workflow."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

BASE_COMPOSE: tuple[str, ...] = ("-f", "docker-compose.yml", "-f", "docker-compose.dev.yml")
REPO_ROOT = Path(__file__).resolve().parent


def _compose(args: list[str], *, check: bool = True) -> int:
    full = ["docker", "compose", *BASE_COMPOSE, *args]
    return subprocess.run(full, cwd=REPO_ROOT, check=check).returncode


def _up(_args: argparse.Namespace) -> None:
    """Start backend, engine, research, and frontend in dev mode."""
    _compose(["up", "-d"])


def _down(_args: argparse.Namespace) -> None:
    """Stop and remove the compose stack."""
    _compose(["down"])


def _logs(args: argparse.Namespace) -> None:
    """Stream logs for a service, or all services."""
    compose_args = ["logs", "-f"]
    if args.service:
        compose_args.append(args.service)
    _compose(compose_args)


def _exec(args: argparse.Namespace) -> None:
    """Run a command inside a service."""
    if not args.command:
        raise SystemExit(
            "No command supplied. Try: python dev.py exec <service> -- <cmd>"
        )
    _compose(["exec", args.service, *args.command])


def _shell(args: argparse.Namespace) -> None:
    """Open an interactive shell inside a service."""
    _compose(["exec", "-it", args.service, "bash"])


def _install(_args: argparse.Namespace) -> None:
    """Re-run editable install in backend for dependency additions."""
    _compose(["exec", "backend", "pip", "install", "-e", "."])


def _jupyter(_args: argparse.Namespace) -> None:
    """Show the local Jupyter URL and stream research logs."""
    print("Open: http://localhost:8888")
    _compose(["logs", "-f", "research"])


def _reset_deps(_args: argparse.Namespace) -> None:
    """Clear dependency-related Docker volumes and relaunch the stack."""
    subprocess.run(
        [
            "docker",
            "volume",
            "rm",
            "-f",
            "trading-py-venv",
            "trading-pip-cache",
            "trading-node-modules",
        ],
        cwd=REPO_ROOT,
        check=False,
    )
    _compose(["up", "-d"])


def _rebuild(args: argparse.Namespace) -> None:
    """Build one service (or all services) with --no-cache."""
    compose_args = ["build", "--no-cache"]
    if args.service:
        compose_args.append(args.service)
    _compose(compose_args)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Orchestrate the local docker dev stack.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("up", help="Start the dev stack.").set_defaults(func=_up)
    sub.add_parser("down", help="Stop the dev stack.").set_defaults(func=_down)

    logs = sub.add_parser("logs", help="Stream compose logs.")
    logs.add_argument("service", nargs="?")
    logs.set_defaults(func=_logs)

    exec_parser = sub.add_parser("exec", help="Run a command inside a service.")
    exec_parser.add_argument("service")
    exec_parser.add_argument("command", nargs=argparse.REMAINDER)
    exec_parser.set_defaults(func=_exec)

    shell = sub.add_parser("shell", help="Open bash inside a service.")
    shell.add_argument("service")
    shell.set_defaults(func=_shell)

    sub.add_parser("install", help="Run pip install -e . in backend.").set_defaults(
        func=_install
    )
    sub.add_parser("jupyter", help="Show Jupyter URL and stream logs.").set_defaults(
        func=_jupyter
    )
    sub.add_parser("reset-deps", help="Clear dependency volumes and restart.").set_defaults(
        func=_reset_deps
    )

    rebuild = sub.add_parser("rebuild", help="Build all services, or one service, with no cache.")
    rebuild.add_argument("service", nargs="?")
    rebuild.set_defaults(func=_rebuild)
    return parser


def main() -> None:
    args = _parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
