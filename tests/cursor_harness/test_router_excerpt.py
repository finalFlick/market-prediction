"""Tests for ``_router_core.excerpt``."""

from __future__ import annotations

from pathlib import Path

import pytest


def test_head_excerpt_under_limit(project_dir: Path) -> None:
    from _router_core import excerpt

    target = project_dir / "doc.md"
    target.write_text("hello world\nline 2", encoding="utf-8")

    assert excerpt("doc.md", None, 100, project_dir) == "hello world\nline 2"


def test_head_excerpt_over_limit_truncates(project_dir: Path) -> None:
    from _router_core import excerpt

    body = "x" * 5000
    target = project_dir / "big.md"
    target.write_text(body, encoding="utf-8")

    out = excerpt("big.md", None, 200, project_dir)
    assert out is not None
    assert len(out) <= 200
    assert out.endswith("... [truncated]")


def test_anchor_excerpt_at_top(project_dir: Path) -> None:
    from _router_core import excerpt

    text = "## Intro\nfoo\nbar\n## Limits\nL1\nL2\n## Other\noo"
    target = project_dir / "doc.md"
    target.write_text(text, encoding="utf-8")

    out = excerpt("doc.md", "## Limits", 200, project_dir)
    assert out is not None
    assert out.startswith("## Limits")
    assert "L1" in out
    assert "L2" in out
    assert "## Other" not in out


def test_anchor_excerpt_at_eof(project_dir: Path) -> None:
    from _router_core import excerpt

    text = "## Intro\nfoo\n## Tail\nlast\nlines"
    (project_dir / "doc.md").write_text(text, encoding="utf-8")

    out = excerpt("doc.md", "## Tail", 200, project_dir)
    assert out is not None
    assert "last" in out
    assert "lines" in out


def test_anchor_missing_returns_none(project_dir: Path) -> None:
    from _router_core import excerpt

    (project_dir / "doc.md").write_text("# Just one\nbody", encoding="utf-8")
    assert excerpt("doc.md", "## NotThere", 200, project_dir) is None


def test_missing_file_returns_none(project_dir: Path) -> None:
    from _router_core import excerpt

    assert excerpt("nope.md", None, 100, project_dir) is None


def test_traversal_path_returns_none(
    project_dir: Path,
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    """A ``..`` path escaping the project root must be rejected."""
    from _router_core import excerpt

    sibling = tmp_path_factory.mktemp("sibling")
    (sibling / "secret.md").write_text("secret", encoding="utf-8")
    rel = Path("..") / sibling.name / "secret.md"
    assert excerpt(str(rel), None, 100, project_dir) is None
