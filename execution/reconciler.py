"""Broker reconciliation on engine boot (Invariant 6)."""

from __future__ import annotations

from collections.abc import Sequence

from execution.brokers.base import Broker, ReconcileReport


async def reconcile_brokers(brokers: Sequence[Broker]) -> list[ReconcileReport]:
    return [await b.reconcile() for b in brokers]
