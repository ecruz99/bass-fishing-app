"""Errors that mean something to the app, not to a particular layer.

Any layer can raise them, and routers turn them into HTTP responses. This keeps
database errors inside the repositories and HTTP details inside the routers.
"""


class EmailAlreadyRegisteredError(Exception):
    """Signup used an email that another account already has."""
