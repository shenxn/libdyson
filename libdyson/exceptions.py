"""Dyson Python library exceptions."""


class DysonException(Exception):
    """Base class for exceptions."""


class DysonNetworkError(DysonException):
    """Represents network error."""


class DysonLoginFailure(DysonException):
    """Represents failure during logging in."""


class DysonConnectTimeout(DysonException):
    """Represents mqtt connection timeout."""


class DysonNotConnected(DysonException):
    """Represents mqtt not connected."""


class DysonInvalidCredential(DysonException):
    """Requesents invalid mqtt credential."""


class DysonConnectionRefused(DysonException):
    """Represents mqtt connection refused by the server."""
