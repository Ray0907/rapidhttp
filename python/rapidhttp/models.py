"""
rapidhttp.models
~~~~~~~~~~~~~~~~

This module contains the primary objects for requests compatibility.
"""

from ._rapidhttp import Response as _RustResponse


class Response:
    """The :class:`Response <Response>` object, which contains a server's response to an HTTP request.
    
    This is a wrapper around the Rust response object that provides the requests-compatible API.
    """
    
    def __init__(self, rust_response):
        """Initialize with a Rust response object."""
        self._rust_response = rust_response
        self._content = None
        self._text = None
        self._json = None
    
    @property
    def status_code(self):
        """Integer Code of responded HTTP Status, e.g. 404 or 200."""
        return self._rust_response.status_code
    
    @property
    def url(self):
        """Final URL location of Response."""
        return self._rust_response.url
    
    @property
    def headers(self):
        """Case-insensitive Dictionary of Response Headers."""
        return self._rust_response.headers
    
    @property
    def content(self):
        """Content of the response, in bytes."""
        if self._content is None:
            self._content = self._rust_response.content()
        return self._content
    
    @property
    def text(self):
        """Content of the response, in unicode."""
        if self._text is None:
            self._text = self._rust_response.text()
        return self._text
    
    @property
    def encoding(self):
        """Encoding to decode with when accessing r.text."""
        # For now, default to utf-8
        return 'utf-8'
    
    @encoding.setter
    def encoding(self, value):
        """Set the encoding."""
        # This would need to be implemented in the Rust layer
        pass
    
    def json(self, **kwargs):
        """Returns the json-encoded content of a response, if any.

        :param \\*\\*kwargs: Optional arguments that ``json.loads`` takes.
        :raises ValueError: If the response body does not contain valid json.
        """
        if self._json is None:
            # Use orjson for 3-5x faster JSON decoding
            try:
                import orjson
                self._json = orjson.loads(self.content)
            except ImportError:
                # Fallback to standard library if orjson not available
                import json
                self._json = json.loads(self.text)
        return self._json
    
    def raise_for_status(self):
        """Raises :class:`HTTPError`, if one occurred."""
        self._rust_response.raise_for_status()
    
    @property
    def ok(self):
        """Returns True if :attr:`status_code` is less than 400, False otherwise."""
        return self.status_code < 400
    
    @property
    def is_redirect(self):
        """True if this Response is a well-formed HTTP redirect that could have
        been processed automatically (by :meth:`Session.resolve_redirects`).
        """
        return 'location' in self.headers and self.status_code in (301, 302, 303, 307, 308)
    
    @property
    def is_permanent_redirect(self):
        """True if this Response one of the permanent versions of redirect."""
        return 'location' in self.headers and self.status_code in (301, 308)
    
    @property
    def apparent_encoding(self):
        """The apparent encoding, provided by the charset_normalizer or chardet libraries."""
        # Simplified - would need proper implementation
        return 'utf-8'
    
    def iter_content(self, chunk_size=1, decode_unicode=False):
        """Iterates over the response data.  When stream=True is set on the
        request, this avoids reading the content at once into memory for
        large responses.

        :param chunk_size: Number of bytes it should read into memory.
        :param decode_unicode: If True, content will be decoded using the best
            available encoding based on the response.
        """
        # For now, yield the entire content
        # In a full implementation, this would stream from Rust
        content = self.content
        for i in range(0, len(content), chunk_size):
            yield content[i:i+chunk_size]
    
    def iter_lines(self, chunk_size=512, decode_unicode=False, delimiter=None):
        """Iterates over the response data, one line at a time.  When
        stream=True is set on the request, this avoids reading the content
        at once into memory for large responses.
        """
        # Simple implementation
        text = self.text
        for line in text.splitlines():
            yield line
    
    @property
    def cookies(self):
        """A CookieJar of Cookies the server sent back."""
        # Simplified - would need proper cookie handling
        return {}
    
    @property
    def elapsed(self):
        """The amount of time elapsed between sending the request
        and the arrival of the response (as a timedelta).
        """
        # Would need to be tracked in Rust layer
        from datetime import timedelta
        return timedelta(0)
    
    @property
    def request(self):
        """The :class:`PreparedRequest <PreparedRequest>` object to which this
        is a response.
        """
        # Would need to be implemented
        return None
    
    @property
    def history(self):
        """A list of :class:`Response <Response>` objects from the history of the Request.
        Any redirect responses will end up here. The list is sorted from the oldest to the most recent request.
        """
        return []
    
    @property
    def reason(self):
        """Textual reason of responded HTTP Status, e.g. "Not Found" or "OK"."""
        # Map common status codes
        status_reasons = {
            200: 'OK',
            201: 'Created',
            204: 'No Content',
            301: 'Moved Permanently',
            302: 'Found',
            304: 'Not Modified',
            400: 'Bad Request',
            401: 'Unauthorized',
            403: 'Forbidden',
            404: 'Not Found',
            500: 'Internal Server Error',
            502: 'Bad Gateway',
            503: 'Service Unavailable',
        }
        return status_reasons.get(self.status_code, '')
    
    def __repr__(self):
        return f'<Response [{self.status_code}]>'
    
    def __bool__(self):
        """Returns True if :attr:`status_code` is less than 400."""
        return self.ok
    
    def __nonzero__(self):
        """Returns True if :attr:`status_code` is less than 400."""
        return self.ok


class Request:
    """A user-created :class:`Request <Request>` object."""
    
    def __init__(self, method=None, url=None, headers=None, files=None,
                 data=None, params=None, auth=None, cookies=None, hooks=None, json=None):
        self.method = method
        self.url = url
        self.headers = headers or {}
        self.files = files
        self.data = data
        self.json = json
        self.params = params or {}
        self.auth = auth
        self.cookies = cookies or {}
        self.hooks = hooks or {}
    
    def __repr__(self):
        return f'<Request [{self.method}]>'


class PreparedRequest:
    """The fully prepared :class:`PreparedRequest <PreparedRequest>` object."""
    
    def __init__(self):
        self.method = None
        self.url = None
        self.headers = {}
        self.body = None
        self.hooks = {}
    
    def __repr__(self):
        return f'<PreparedRequest [{self.method}]>'
