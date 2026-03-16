# v0.1.0 Release Checklist

Use this checklist before tagging and publishing `forkit-core` v0.1.0.

---

## 1. Code quality

- [ ] All 39 assertions in `tests/test_use_cases.py` pass: `pytest -v tests/`
- [ ] `python3 examples/use_cases.py` runs without errors and prints all 10 use cases
- [ ] `ruff check forkit/` — zero linting errors
- [ ] `mypy forkit/ --ignore-missing-imports` — no type errors on public API
- [ ] No `TODO`, `FIXME`, or `HACK` comments left in source (or all intentionally deferred ones are in `docs/`)

## 2. Identity contract regression check

Run `python3 examples/use_cases.py` and confirm these IDs appear unchanged:

```
base_model.id  = 1bdfbcb0d6a96a6b1cada3acc9db7773791833caf9e6ee2d20cfb5eccd774343
fine_tuned.id  = e919ef1354ef2cb1cebf9a3c65f3be0c739c9601508457f5c9c3152a7fd81ad9
agent.id       = 3e13ce3909ea49de2ac66f7fc727c19f667f1c4a4dd4ab22583e0316d148ad38
```

Any difference is a **breaking change** — do not release until investigated.

## 3. Dual-backend parity

- [ ] Run tests with `pydantic>=2` installed: same 39 assertions pass
- [ ] Run tests without pydantic (uninstall or use a clean venv): same 39 assertions pass
- [ ] Confirm `forkit.schemas._PYDANTIC_AVAILABLE` reflects the environment correctly

## 4. Package metadata

- [ ] `pyproject.toml` version is `0.1.0`
- [ ] `pyproject.toml` `authors` email is correct (`sa.hamza@forkit.dev`)
- [ ] `LICENSE` file is present (Apache 2.0)
- [ ] `README.md` quickstart examples are accurate and runnable
- [ ] `CHANGELOG.md` is up to date

## 5. Build and install

```bash
# Clean build
rm -rf dist/ build/ *.egg-info
pip install build
python -m build

# Verify wheel contents
unzip -l dist/forkit_core-0.1.0-py3-none-any.whl | grep -E "(forkit|forkit_core)" | head -40

# Test install in a clean venv
python -m venv /tmp/test_forkit
/tmp/test_forkit/bin/pip install dist/forkit_core-0.1.0-py3-none-any.whl
/tmp/test_forkit/bin/python -c "from forkit.schemas import ModelPassport; print('OK')"

# Test install with extras
/tmp/test_forkit/bin/pip install "dist/forkit_core-0.1.0-py3-none-any.whl[pydantic,cli]"
/tmp/test_forkit/bin/forkit --help
```

- [ ] Wheel builds cleanly
- [ ] Both `forkit` and `forkit_core` packages are included in the wheel
- [ ] `forkit` CLI entry point works after install
- [ ] Core imports work without optional dependencies

## 6. Documentation

- [ ] `docs/identity-spec.md` exists and matches implementation
- [ ] README quickstart is tested against the released wheel
- [ ] Regression anchors in `docs/identity-spec.md` §9 match `examples/use_cases.py` output

## 7. GitHub

- [ ] `main` branch is clean (`git status` shows nothing uncommitted)
- [ ] All CI checks pass (if GitHub Actions is configured)
- [ ] `CHANGELOG.md` `[Unreleased]` section is renamed to `[0.1.0] — YYYY-MM-DD`
- [ ] Tag and release:
  ```bash
  git tag -s v0.1.0 -m "v0.1.0 — Initial public release"
  git push origin v0.1.0
  ```

## 8. PyPI publish

```bash
pip install twine
twine check dist/*
twine upload dist/*
```

- [ ] `twine check` passes with no warnings
- [ ] Package visible at `https://pypi.org/project/forkit-core/`
- [ ] `pip install forkit-core` installs cleanly from PyPI

## 9. Post-release

- [ ] Add `[Unreleased]` section to `CHANGELOG.md`
- [ ] Bump `pyproject.toml` version to `0.2.0-dev` (or next planned version)
- [ ] Announce release (GitHub release notes, blog, X/LinkedIn as appropriate)

---

## Known deferred items (post-v0.1.0)

These are intentionally out of scope for the initial release:

- **Remote registry** — cloud-backed `RemoteRegistry` with API authentication
- **Schema validation CLI** — `forkit validate <passport.json>` against JSON Schema
- **JSON Schema export** — `ModelPassport.model_json_schema()` (Pydantic backend only for now)
- **Async SDK** — `AsyncForkitClient` for async-native frameworks
- **`forkit_core` shim deprecation** — remove legacy package in v0.2.0 after announcing migration path
- **Python 3.9 support** — requires replacing `kw_only=True` and `str | None` syntax
- **mypy strict mode** — full strict typing is a v0.2.0 goal
