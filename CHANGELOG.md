# Changelog

## Unreleased

### Added
- Added `execution.brokers.registry.LiveBrokerRegistry` with an MVP-0 default lock that refuses live broker registration unless `configs/runtime.yaml` explicitly unlocks it.
- Added `tests/security/test_live_registration_forbidden.py` covering locked live registration, paper registration, unlock override, and live alias parity.
- Added `configs/runtime.yaml` with `live_adapters_unlocked: false` as the default safety posture.

### Changed
- Updated `execution/runner.py` to route broker selection through `LiveBrokerRegistry` so locked live brokers are rejected with a clear CLI error.
- Added `BinanceLive` and `CoinbaseLive` aliases for design-vocabulary parity while keeping runtime registration locked.
- Bumped package version to `0.2.0`.
