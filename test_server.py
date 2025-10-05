#!/usr/bin/env python3
"""
Simple test server for benchmarking
Supports GET and POST /echo endpoints
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json


class TestHandler(BaseHTTPRequestHandler):
    """Simple request handler for testing"""

    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

    def do_GET(self):
        """Handle GET requests"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')

    def do_POST(self):
        """Handle POST requests - echo back JSON"""
        content_length = int(self.headers.get('Content-Length', 0))

        # Read body
        body = self.rfile.read(content_length)

        # Parse JSON if Content-Type is application/json
        content_type = self.headers.get('Content-Type', '')

        if 'application/json' in content_type:
            try:
                # Parse and echo back the JSON
                data = json.loads(body)
                response = json.dumps(data).encode('utf-8')

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(response)))
                self.end_headers()
                self.wfile.write(response)
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Invalid JSON')
        else:
            # Echo back non-JSON body
            self.send_response(200)
            self.send_header('Content-Type', content_type or 'text/plain')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)


def run_server(port=8000):
    """Start the test server"""
    server = HTTPServer(('127.0.0.1', port), TestHandler)
    print(f"Test server running on http://127.0.0.1:{port}/")
    print("Press Ctrl+C to stop")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
        server.shutdown()


if __name__ == '__main__':
    run_server()
