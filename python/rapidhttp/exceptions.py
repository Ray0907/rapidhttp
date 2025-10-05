"""
rapidhttp.exceptions
~~~~~~~~~~~~~~~~~~~~

This module contains the set of requests-compatible exceptions.
"""

# Re-export exceptions from Rust extension
from ._rapidhttp import (
    HTTPError,
    ConnectionError,
    Timeout,
    ConnectTimeout,
    ReadTimeout,
    TooManyRedirects,
    RequestException,
    URLRequired,
    JSONDecodeError,
)

# Additional compatibility exceptions
class FileModeWarning(Warning):
    """A file was opened in text mode, but Requests determined its binary length."""
    pass


class RequestsDependencyWarning(Warning):
    """An imported dependency doesn't match the expected version range."""
    pass


__all__ = [
    'HTTPError',
    'ConnectionError', 
    'Timeout',
    'ConnectTimeout',
    'ReadTimeout',
    'TooManyRedirects',
    'RequestException',
    'URLRequired',
    'JSONDecodeError',
    'FileModeWarning',
    'RequestsDependencyWarning',
]
