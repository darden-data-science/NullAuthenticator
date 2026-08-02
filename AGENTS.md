<!-- last-verified: 2026-08-02 against bdb2f07 (master) -->

# NullAuthenticator

**LIVE — do not delete.** 18 lines of code, last commit 2020-08-05, no tests, no CI, `setup.py`
only, `python_requires>=3.5`, `jupyterhub>=1.1.0`.

Easy to mistake for dead code. It is not: it powers the landing page, which is the front door to
every cohort hub.

## Where this fits

`authenticate()` always returns `None`, so nobody can ever log in. That is the point — the landing
hub exists only to render a class-picker page. The buttons live in its `custom_html` trait, which
is the thing you edit **every annual rollover**.

**My half of the contract:** none. I have no wire protocol. I expose one trait, `custom_html`, and
one behavior: reject every login attempt.

**Who consumes me:** pip-installed from this GitHub default branch, **unpinned**, by
`images/hub/Dockerfile:9` in `darden-data-science/jupyterhub-config-darden`. Set as
`authenticator_class: NullAuthenticator.NullAuthenticator` at
`config_files/integration/jupyterhub-landing/values.yaml:35`; the buttons are rendered from
`config_files/integration/jupyterhub-landing/values.yaml.gotmpl:15-39`.

**Full system map:** `/Users/Michael/Documents/Git Projects/Darden Jupyterhub/docs/SYSTEM-MAP.md`
(repo `darden-data-science/jupyterhub-config-darden`, private).

## Layout

```
NullAuthenticator/NullAuthenticator.py   18 lines: one class, one trait, one method
NullAuthenticator/_version.py            0.0.1dev
setup.py                                 entry point: null_authenticator
```

The deployment uses the dotted path, not the entry point name.

## Known issues

- **JupyterHub 5 `allow_all`.** The landing hub sets `custom_html` but neither `allow_all` nor
  `allowed_users`. Since `authenticate()` always returns `None` the practical behavior is
  unchanged, but this is the one authenticator in the system where the JupyterHub 5 default was
  never audited. Verify during the version sweep.
- No `pyproject.toml`. If it gets modernized, copy `../ExternalAuthenticator` — PEP 621 with a
  dynamic version from `_version.py`, a 7-line `setup.py` shim, and the `sys.modules`-stubbed
  unittest pattern, which suits an 18-line package well.
- The hub image installs from this branch unpinned, so any merge here changes the next hub build —
  and `ENV cacheBuster` in `images/hub/Dockerfile` must be bumped or Docker serves the cached
  layer.
