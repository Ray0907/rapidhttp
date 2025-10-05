"""
rapidhttp.status_codes
~~~~~~~~~~~~~~~~~~~~~~

This module provides HTTP status code lookups.
"""


class _Codes(dict):
    """Provides dot-notation access to HTTP status codes."""
    
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"No status code: {name}")


# HTTP status codes
codes = _Codes({
    # Informational
    'continue': 100,
    'switching_protocols': 101,
    'processing': 102,
    'checkpoint': 103,
    'uri_too_long': 122,
    'ok': 200,
    'created': 201,
    'accepted': 202,
    'non_authoritative_info': 203,
    'non_authoritative_information': 203,
    'no_content': 204,
    'reset_content': 205,
    'reset': 205,
    'partial_content': 206,
    'partial': 206,
    'multi_status': 207,
    'already_reported': 208,
    'im_used': 226,
    
    # Redirection
    'multiple_choices': 300,
    'moved_permanently': 301,
    'moved': 301,
    'found': 302,
    'see_other': 303,
    'other': 303,
    'not_modified': 304,
    'use_proxy': 305,
    'switch_proxy': 306,
    'temporary_redirect': 307,
    'temporary_moved': 307,
    'temporary': 307,
    'permanent_redirect': 308,
    'resume_incomplete': 308,
    'resume': 308,
    
    # Client Error
    'bad_request': 400,
    'bad': 400,
    'unauthorized': 401,
    'payment_required': 402,
    'payment': 402,
    'forbidden': 403,
    'not_found': 404,
    'method_not_allowed': 405,
    'not_allowed': 405,
    'not_acceptable': 406,
    'proxy_authentication_required': 407,
    'proxy_auth': 407,
    'proxy_authentication': 407,
    'request_timeout': 408,
    'timeout': 408,
    'conflict': 409,
    'gone': 410,
    'length_required': 411,
    'precondition_failed': 412,
    'precondition': 412,
    'request_entity_too_large': 413,
    'request_uri_too_large': 414,
    'unsupported_media_type': 415,
    'unsupported_media': 415,
    'media_type': 415,
    'requested_range_not_satisfiable': 416,
    'requested_range': 416,
    'range_not_satisfiable': 416,
    'expectation_failed': 417,
    'im_a_teapot': 418,
    'teapot': 418,
    'misdirected_request': 421,
    'unprocessable_entity': 422,
    'unprocessable': 422,
    'locked': 423,
    'failed_dependency': 424,
    'dependency': 424,
    'unordered_collection': 425,
    'unordered': 425,
    'upgrade_required': 426,
    'upgrade': 426,
    'precondition_required': 428,
    'too_many_requests': 429,
    'too_many': 429,
    'header_fields_too_large': 431,
    'fields_too_large': 431,
    'no_response': 444,
    'none': 444,
    'retry_with': 449,
    'retry': 449,
    'blocked_by_windows_parental_controls': 450,
    'parental_controls': 450,
    'unavailable_for_legal_reasons': 451,
    'legal_reasons': 451,
    'client_closed_request': 499,
    
    # Server Error
    'internal_server_error': 500,
    'server_error': 500,
    'not_implemented': 501,
    'bad_gateway': 502,
    'service_unavailable': 503,
    'unavailable': 503,
    'gateway_timeout': 504,
    'http_version_not_supported': 505,
    'http_version': 505,
    'variant_also_negotiates': 506,
    'insufficient_storage': 507,
    'bandwidth_limit_exceeded': 509,
    'bandwidth': 509,
    'not_extended': 510,
    'network_authentication_required': 511,
    'network_auth': 511,
    'network_authentication': 511,
})

# Add reverse lookups (by code number)
for name, code in list(codes.items()):
    codes[code] = code

__all__ = ['codes']
