"""Dyson Python library exceptions."""


class DysonException(Exception):
    """Base class for exceptions."""


class DysonNetworkError(DysonException):
    """Represents network error."""


class DysonServerError(DysonException):
    """Represents Dyson server error."""


class DysonLoginFailure(DysonException):
    """Represents failure during logging in."""


class DysonAuthRequired(DysonException):
    """Represents not logged into could."""


class DysonInvalidAuth(DysonException):
    """Represents invalid authentication."""


class DysonConnectTimeout(DysonException):
    """Represents mqtt connection timeout."""


class DysonNotConnected(DysonException):
    """Represents mqtt not connected."""


class DysonInvalidCredential(DysonException):
    """Requesents invalid mqtt credential."""


class DysonConnectionRefused(DysonException):
    """Represents mqtt connection refused by the server."""
