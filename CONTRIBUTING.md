# Contributing to Forkit Dev Core

Forkit Dev Core is a contract-first repository. The highest-risk changes are:

- identity derivation
- schema semantics
- sync envelope shape
- verification behavior
- adapter behavior that changes persisted passport fields

For any large change in those areas, open an issue before implementation.

## Development basics

- Python: `3.10+`
- Node.js: `20+` for `web/`

Recommended checks before opening a pull request:

- `ruff check .`
- `pytest`
- `python -m build` if packaging or install-facing docs changed
- `cd web && npm run build && npm run lint` if the frontend changed

## Contract rules

- Do not change deterministic `passport_id` behavior casually.
- Keep application metadata outside the identity boundary.
- Do not present mock-backed UI behavior as a real hosted control plane.
- Keep self-hosted and generic sync wording precise.

## Pull requests

- Keep changes scoped.
- Include tests for behavior changes.
- Update docs when changing user-facing behavior or identity-related behavior.
- Prefer additive changes over silent contract rewrites.
