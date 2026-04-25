"""Placeholder so `pytest -m det` is a valid CI gate before determinism tests land."""

import pytest


@pytest.mark.det
def test_det_marker_registered() -> None:
    assert True
