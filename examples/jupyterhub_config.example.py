"""Example JupyterHub config for a landing-page hub.

A hub configured this way can never be logged into. Its only job is to render
`custom_html` — typically a set of links to the real hubs behind the same
ingress.

Run with:  jupyterhub --config jupyterhub_config.example.py
"""

c = get_config()  # noqa: F821  (injected by traitlets)

# Either form works. The entry point is the tidier one; the dotted path is what
# Zero-to-JupyterHub deployments tend to use, since it needs no entry-point
# resolution inside the hub image.
c.JupyterHub.authenticator_class = "null_authenticator"
# c.JupyterHub.authenticator_class = "NullAuthenticator.NullAuthenticator"

# The whole point. This replaces the username/password form on the login page.
#
# NOTE: this trait is configurable ONLY because NullAuthenticator redeclares it
# with config=True. JupyterHub's own Authenticator.custom_html is not tagged
# configurable, so the same assignment against a stock Authenticator silently
# does nothing.
c.NullAuthenticator.custom_html = """
<div class="text-center">
  <p>Choose your course:</p>
  <a role="button" class="btn btn-jupyter btn-lg" href="/msba26">MSBA 2026</a>
  <a role="button" class="btn btn-jupyter btn-lg" href="/exec-ed">Executive Education</a>
</div>
"""

# No allow_all or allowed_users needed. JupyterHub 5 defaults
# Authenticator.allow_all to False, but that gate is never reached:
# get_authenticated_user() returns as soon as authenticate() yields None.

# Landing hubs usually sit at a path prefix behind a shared ingress.
# c.JupyterHub.base_url = "/"
