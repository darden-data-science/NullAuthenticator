# NullAuthenticator

A JupyterHub `Authenticator` that rejects every login attempt.

That sounds useless, and the point is easy to miss: it turns a hub into a **landing page**.
`authenticate()` always returns `None`, so nobody can sign in — but `custom_html` replaces the
login form, so the page can render whatever you like. Links to the real hubs behind the same
ingress, for example.

## Install

```bash
pip install git+https://github.com/darden-data-science/NullAuthenticator.git
```

## Use

```python
c.JupyterHub.authenticator_class = "null_authenticator"

c.NullAuthenticator.custom_html = """
<a role="button" class="btn btn-jupyter btn-lg" href="/msba26">MSBA 2026</a>
"""
```

The dotted path `"NullAuthenticator.NullAuthenticator"` works too, and is what
Zero-to-JupyterHub deployments generally use.

A complete example: [`examples/jupyterhub_config.example.py`](examples/jupyterhub_config.example.py).

## The one thing worth knowing

**`custom_html` is configurable only because this package redeclares it.**

JupyterHub's own `Authenticator.custom_html` is a `Unicode` trait that is *not* tagged
`config=True` (verified against JupyterHub 5.5). Setting it on a stock authenticator from config
silently does nothing. The five-line redeclaration in `NullAuthenticator.py` adds `config=True`,
and it is the only reason the landing page works.

It looks like redundant boilerplate. It is not. `tests/test_null_authenticator.py` guards both
halves of that — including a test that fails if JupyterHub ever adds `config=True` upstream, at
which point the redeclaration becomes safe to drop.

## Compatibility

Python 3.10+, JupyterHub 4.x and 5.x.

**No `allow_all` or `allowed_users` configuration is required.** JupyterHub 5 defaults
`Authenticator.allow_all` to `False`, which denies users who authenticate successfully — but that
gate is never reached here, because `get_authenticated_user()` returns as soon as `authenticate()`
yields `None`. There is a test for this.

`authenticate()` is a plain `def`, not `async def`. JupyterHub calls it through `maybe_future()`,
which accepts either. This is deliberate and asserted in the tests, so the difference from sibling
authenticators reads as a choice rather than an oversight.

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md).

```bash
pip install -e ".[dev]" && python -m unittest discover -s tests -v
```

## License

BSD 3-Clause. See [LICENSE](LICENSE).
