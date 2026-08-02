"""Tests for NullAuthenticator.

These run against a REAL JupyterHub install rather than the sys.modules-stubbed
pattern used in the sibling ExternalAuthenticator repo. That is deliberate: the
single most important property of this package — that `custom_html` is settable
from JupyterHub config — is a real-traitlets behaviour that a stubbed traitlets
would happily fake, so a stubbed test would pass even if the package were
broken. `jupyterhub` is a declared dependency, so it is always present.
"""

import inspect
import unittest

from traitlets.config import Config

from jupyterhub.auth import Authenticator

from NullAuthenticator import NullAuthenticator, __version__


class RejectsEveryLoginTest(unittest.IsolatedAsyncioTestCase):
    """The core behaviour: nobody can ever log in."""

    def test_authenticate_is_synchronous_by_design(self):
        """`authenticate` is a plain def, not `async def`.

        JupyterHub calls it through `maybe_future()`, which accepts either, so
        this is valid and is left alone deliberately — the sibling
        DictionaryAuthenticator uses `async def` and both work. Asserted here so
        the difference reads as a choice rather than an oversight, and so that
        anyone converting it to async updates these tests knowingly.
        """
        self.assertFalse(
            inspect.iscoroutinefunction(NullAuthenticator.authenticate),
            "authenticate became a coroutine; drop this test and await it below",
        )

    def test_authenticate_returns_none(self):
        authenticator = NullAuthenticator()
        self.assertIsNone(authenticator.authenticate(handler=None, data={}))

    def test_authenticate_returns_none_for_any_credentials(self):
        authenticator = NullAuthenticator()
        for data in (
            {},
            {"username": "alice"},
            {"username": "alice", "password": "hunter2"},
            {"username": "", "password": ""},
        ):
            with self.subTest(data=data):
                self.assertIsNone(authenticator.authenticate(handler=None, data=data))

    async def test_get_authenticated_user_rejects_before_the_allow_check(self):
        """JupyterHub 5 defaults Authenticator.allow_all to False, which denies
        every user that authenticates successfully. That gate is irrelevant here:
        get_authenticated_user() returns as soon as authenticate() yields None,
        so it is never reached.

        This is why the landing hub needs no allow_all / allowed_users config.
        If this ever starts failing, that assumption has changed.
        """
        authenticator = NullAuthenticator()
        self.assertFalse(authenticator.allow_all)
        result = await authenticator.get_authenticated_user(
            handler=None, data={"username": "alice", "password": "hunter2"}
        )
        self.assertIsNone(result)


class CustomHtmlTest(unittest.TestCase):
    """The reason this package exists.

    The landing hub renders its class-picker buttons entirely through this
    trait. Everything below guards a redeclaration in NullAuthenticator.py that
    looks like redundant boilerplate and is not.
    """

    def test_custom_html_is_not_configurable_on_base_jupyterhub(self):
        """Guards the assumption that makes the redeclaration necessary.

        JupyterHub declares `custom_html = Unicode(...)` WITHOUT config=True.
        If a future JupyterHub adds config=True upstream, this test fails and
        the redeclaration in this package becomes removable.
        """
        self.assertNotIn("custom_html", Authenticator.class_traits(config=True))

    def test_custom_html_is_configurable_here(self):
        self.assertIn("custom_html", NullAuthenticator.class_traits(config=True))

    def test_custom_html_is_applied_from_config(self):
        """The end-to-end property the landing page depends on."""
        html = '<a role="button" href="/msba26">MSBA 2026</a>'
        config = Config()
        config.NullAuthenticator.custom_html = html

        authenticator = NullAuthenticator(config=config)
        self.assertEqual(authenticator.custom_html, html)
        self.assertEqual(authenticator.get_custom_html("/"), html)

    def test_custom_html_defaults_to_empty(self):
        self.assertEqual(NullAuthenticator().custom_html, "")


class PackagingTest(unittest.TestCase):
    def test_version_is_a_release_string(self):
        self.assertRegex(__version__, r"^\d+\.\d+\.\d+")

    def test_importable_from_package_root(self):
        import NullAuthenticator as pkg

        self.assertIs(pkg.NullAuthenticator, NullAuthenticator)

    def test_subclasses_jupyterhub_authenticator(self):
        self.assertTrue(issubclass(NullAuthenticator, Authenticator))


if __name__ == "__main__":
    unittest.main()
