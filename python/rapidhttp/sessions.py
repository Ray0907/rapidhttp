"""
rapidhttp.sessions
~~~~~~~~~~~~~~~~~~

This module provides a Session object to persist parameters across requests.
"""

from ._rapidhttp import request as _rust_request
from .models import Response


class Session:
    """A requests-compatible Session object.
    
    Provides cookie persistence, connection pooling, and configuration.
    
    Basic Usage::
    
      >>> import rapidhttp as requests
      >>> s = requests.Session()
      >>> s.get('https://httpbin.org/get')
      <Response [200]>
    """
    
    def __init__(self):
        self.headers = {}
        self.cookies = {}
        self.auth = None
        self.proxies = {}
        self.hooks = {}
        self.params = {}
        self.verify = True
        self.cert = None
        self.adapters = {}
        self.stream = False
        self.trust_env = True
        self.max_redirects = 30
    
    def request(self, method, url, 
                params=None,
                data=None, 
                headers=None,
                cookies=None,
                files=None,
                auth=None,
                timeout=None,
                allow_redirects=True,
                proxies=None,
                hooks=None,
                stream=None,
                verify=None,
                cert=None,
                json=None):
        """Constructs a :class:`Request <Request>`, prepares it and sends it.
        Returns :class:`Response <Response>` object.

        :param method: method for the new :class:`Request` object.
        :param url: URL for the new :class:`Request` object.
        :param params: (optional) Dictionary or bytes to be sent in the query string.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like object.
        :param json: (optional) json to send in the body of the :class:`Request`.
        :param headers: (optional) Dictionary of HTTP Headers.
        :param cookies: (optional) Dict or CookieJar object.
        :param files: (optional) Dictionary of ``'filename': file-like-objects``.
        :param auth: (optional) Auth tuple or callable.
        :param timeout: (optional) How long to wait for the server.
        :param allow_redirects: (optional) Set to True by default.
        :param proxies: (optional) Dictionary mapping protocol or protocol and
            hostname to the URL of the proxy.
        :param stream: (optional) whether to immediately download the response
            content. Defaults to ``False``.
        :param verify: (optional) Either a boolean or string. Defaults to True.
        :param cert: (optional) if String, path to ssl client cert file (.pem).
            If Tuple, ('cert', 'key') pair.
        :rtype: rapidhttp.Response
        """
        
        # Merge session headers with request headers
        merged_headers = {}
        merged_headers.update(self.headers)
        if headers:
            merged_headers.update(headers)
        
        # Merge session params with request params
        merged_params = {}
        merged_params.update(self.params)
        if params:
            merged_params.update(params)
        
        # Use session defaults if not overridden
        if verify is None:
            verify = self.verify
        if cert is None:
            cert = self.cert
        if stream is None:
            stream = self.stream
        if proxies is None:
            proxies = self.proxies
        if auth is None:
            auth = self.auth
            
        # Call the Rust implementation
        rust_response = _rust_request(
            method=method.upper(),
            url=url,
            params=merged_params if merged_params else None,
            headers=merged_headers if merged_headers else None,
            data=data,
            json=json,
            timeout=timeout,
            allow_redirects=allow_redirects,
            verify=verify,
        )
        
        # Wrap in our Response class
        return Response(rust_response)
    
    def get(self, url, **kwargs):
        """Sends a GET request. Returns :class:`Response` object.

        :param url: URL for the new :class:`Request` object.
        :param \\*\\*kwargs: Optional arguments that ``request`` takes.
        :rtype: rapidhttp.Response
        """
        kwargs.setdefault('allow_redirects', True)
        return self.request('GET', url, **kwargs)

    def options(self, url, **kwargs):
        """Sends a OPTIONS request. Returns :class:`Response` object.

        :param url: URL for the new :class:`Request` object.
        :param \\*\\*kwargs: Optional arguments that ``request`` takes.
        :rtype: rapidhttp.Response
        """
        kwargs.setdefault('allow_redirects', True)
        return self.request('OPTIONS', url, **kwargs)

    def head(self, url, **kwargs):
        """Sends a HEAD request. Returns :class:`Response` object.

        :param url: URL for the new :class:`Request` object.
        :param \\*\\*kwargs: Optional arguments that ``request`` takes.
        :rtype: rapidhttp.Response
        """
        kwargs.setdefault('allow_redirects', False)
        return self.request('HEAD', url, **kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        """Sends a POST request. Returns :class:`Response` object.

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like object.
        :param json: (optional) json to send in the body of the :class:`Request`.
        :param \\*\\*kwargs: Optional arguments that ``request`` takes.
        :rtype: rapidhttp.Response
        """
        kwargs.setdefault('allow_redirects', True)
        return self.request('POST', url, data=data, json=json, **kwargs)

    def put(self, url, data=None, **kwargs):
        """Sends a PUT request. Returns :class:`Response` object.

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like object.
        :param \\*\\*kwargs: Optional arguments that ``request`` takes.
        :rtype: rapidhttp.Response
        """
        kwargs.setdefault('allow_redirects', True)
        return self.request('PUT', url, data=data, **kwargs)

    def patch(self, url, data=None, **kwargs):
        """Sends a PATCH request. Returns :class:`Response` object.

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like object.
        :param \\*\\*kwargs: Optional arguments that ``request`` takes.
        :rtype: rapidhttp.Response
        """
        kwargs.setdefault('allow_redirects', True)
        return self.request('PATCH', url, data=data, **kwargs)

    def delete(self, url, **kwargs):
        """Sends a DELETE request. Returns :class:`Response` object.

        :param url: URL for the new :class:`Request` object.
        :param \\*\\*kwargs: Optional arguments that ``request`` takes.
        :rtype: rapidhttp.Response
        """
        kwargs.setdefault('allow_redirects', True)
        return self.request('DELETE', url, **kwargs)
    
    def close(self):
        """Closes all adapters and as such the session"""
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()


def session():
    """
    Returns a :class:`Session` for context-management.

    Usage::

      >>> import rapidhttp as requests
      >>> with requests.session() as s:
      ...     s.get('https://httpbin.org/get')
      <Response [200]>
    """
    return Session()
