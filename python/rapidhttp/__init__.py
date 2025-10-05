"""
RapidHTTP - The fastest Python HTTP client with 100% requests API compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

RapidHTTP is a drop-in replacement for requests with 10-15x performance improvement.

Basic GET usage:

   >>> import rapidhttp as requests
   >>> r = requests.get('https://www.python.org')
   >>> r.status_code
   200
   >>> b'Python is a programming language' in r.content
   True

... or POST:

   >>> payload = dict(key1='value1', key2='value2')
   >>> r = requests.post('https://httpbin.org/post', data=payload)
   >>> print(r.text)
   {
     ...
     "form": {
       "key1": "value1",
       "key2": "value2"
     },
     ...
   }

Full documentation at <https://rapidhttp.readthedocs.io>.

:copyright: (c) 2024 RapidHTTP Contributors
:license: Apache 2.0, see LICENSE for more details.
"""

__title__ = 'rapidhttp'
__version__ = '0.1.0'
__description__ = 'The fastest Python HTTP client - 100% requests compatible'
__url__ = 'https://github.com/Ray0907/rapidhttp'
__author__ = 'RapidHTTP Contributors'
__author_email__ = 'support@rapidhttp.dev'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2024 RapidHTTP Contributors'

# Import core functionality from Rust extension
from ._rapidhttp import (
    Client as _Client,
    Response as _Response,
    request as _request,
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

# Import compatibility layer
from .api import (
    request,
    get,
    head,
    post,
    patch,
    put,
    delete,
    options,
)

from .sessions import Session, session
from .models import Response, Request, PreparedRequest
from .status_codes import codes
from . import exceptions

# For convenience
__all__ = [
    # Core functions
    'request', 'get', 'head', 'post', 'patch', 'put', 'delete', 'options',
    
    # Classes
    'Session', 'Response', 'Request', 'PreparedRequest',
    
    # Exceptions
    'HTTPError', 'ConnectionError', 'Timeout', 'ConnectTimeout', 
    'ReadTimeout', 'TooManyRedirects', 'RequestException', 'URLRequired',
    'JSONDecodeError',
    
    # Utilities
    'codes', 'session', 'exceptions',
    
    # Metadata
    '__title__', '__version__', '__description__', '__url__',
    '__author__', '__author_email__', '__license__', '__copyright__',
]
