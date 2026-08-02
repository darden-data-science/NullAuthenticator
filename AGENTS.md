<!-- last-verified: 2026-08-02 against f7c5674 (master) -->

# NullAuthenticator

**LIVE — do not delete.** Modernized 2026-08-02 to v1.0.0: PEP 621 packaging, dynamic version,
GitHub Actions CI (py3.10–3.13), 11 tests, `jupyterhub>=4`, Python 3.10+.

Easy to mistake for dead code — it rejects every login, and the module is 18 lines. It is not
dead: it powers the landing page, which is the front door to every cohort hub.

## Where this fits

`authenticate()` always returns `None`, so nobody can log in. That is the point — the landing hub
exists only to render a class-picker page. The buttons live in its `custom_html` trait, which is
the thing you edit **every annual rollover**.

**My half of the contract:** none. No wire protocol. One trait, `custom_html`, and one behavior:
reject every login.

**Who consumes me:** pip-installed from this GitHub default branch, **unpinned**, by
`images/hub/Dockerfile:9` in `darden-data-science/jupyterhub-config-darden`. Set as
`authenticator_class: NullAuthenticator.NullAuthenticator` at
`config_files/integration/jupyterhub-landing/values.yaml:35`; the buttons are rendered from
`config_files/integration/jupyterhub-landing/values.yaml.gotmpl:15-39`.

**Full system map:** `/Users/Michael/Documents/Git Projects/Darden Jupyterhub/docs/SYSTEM-MAP.md`
(repo `darden-data-science/jupyterhub-config-darden`, private).

## The fact that makes this package non-trivial

**`custom_html` is configurable ONLY because this package redeclares it.**

JupyterHub's own `Authenticator.custom_html` is a `Unicode` trait with **no** `config=True`
(verified against JupyterHub 5.5.0 — `jupyterhub/auth.py:396`). Assigning it from config on a
stock authenticator silently does nothing. The redeclaration in `NullAuthenticator.py:10-15` adds
`.tag(config=True)`, and that is the only reason the landing page renders anything.

Those five lines look like redundant boilerplate copied from the base class. Deleting them takes
down the front door for every cohort, silently, with no error. Two tests guard it — including one
that fails if JupyterHub ever adds `config=True` upstream, at which point the redeclaration
becomes safe to drop.

## Layout

```
NullAuthenticator/NullAuthenticator.py   18 lines: one class, one trait, one method
NullAuthenticator/_version.py            the single source of truth for the version
pyproject.toml                           PEP 621, authoritative
setup.py                                 shim, kept for editable installs
tests/test_null_authenticator.py         11 tests
examples/jupyterhub_config.example.py    a working landing-page config
.github/workflows/ci.yml                 py3.10-3.13
```

Both `authenticator_class` forms resolve — the entry point `null_authenticator` and the dotted
path `NullAuthenticator.NullAuthenticator`. The deployment uses the dotted path.

## Commands

```bash
uv venv && uv pip install -e ".[dev]"
```

```bash
uv run python -m unittest discover -s tests -v
```

## Testing convention — deliberately different from ExternalAuthenticator

These tests run against a **real JupyterHub**, not the `sys.modules`-stubbed pattern used in
`../ExternalAuthenticator`. The defining behavior here — that `custom_html` is settable from
config — is a property of real traitlets, so a stubbed traitlets would report success against a
broken package. `jupyterhub` is a declared dependency, so it is always present in CI.

Copy ExternalAuthenticator's stubbing pattern when a package's logic is genuinely independent of
its dependencies. Do not copy it here.

## Settled questions

- **JupyterHub 5's `allow_all` does not affect this authenticator.** The default is `False`, which
  denies users who authenticate successfully — but `get_authenticated_user()` returns as soon as
  `authenticate()` yields `None` (`jupyterhub/auth.py:716-717`), so the gate is never reached. The
  landing hub needs no `allow_all` or `allowed_users`. Asserted in the tests.
- **`authenticate()` is a plain `def`, not `async def`.** JupyterHub calls it through
  `maybe_future()`, which accepts either. Left synchronous deliberately — changing deployed auth
  code for stylistic consistency is not worth the risk. A test asserts it, so the difference from
  `../DictionaryAuthenticator` (which is `async`) reads as a choice.

## Cross-repo impact

The hub image installs from this branch unpinned, so anything merged to `master` lands in the next
hub image build — merging is a deploy decision. Docker layer-caches that `RUN pip install`, so
`ENV cacheBuster` in `images/hub/Dockerfile` must be bumped or the rebuild silently keeps the old
version.

## Known issues

None outstanding. `requirements.txt` was removed during modernization — it duplicated the
dependency already declared in `pyproject.toml` and was pure drift risk.
