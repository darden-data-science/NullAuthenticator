from jupyterhub.auth import Authenticator


from traitlets import Unicode


class NullAuthenticator(Authenticator):
    """Null Authenticator - Always returns None"""

    custom_html = Unicode(
        help="""
        HTML form to be overridden by authenticators if they want a custom authentication form.
        Defaults to an empty string, which shows the default username/password form.
        """
    ).tag(config=True)

    def authenticate(self, handler, data):
        self.log.info("Attempted login. Rejecting.")
        return None