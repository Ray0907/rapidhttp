# ⚡ RapidHTTP

**A blazing-fast Python HTTP client with 100% requests API compatibility, powered by Rust.**

```python
# Just change your import - that's it!
- import requests
+ import rapidhttp as requests

# All your existing code works immediately
r = requests.get('https://api.github.com/repos/python/cpython')
print(r.json()['stargazers_count'])
```

## 🚀 Why RapidHTTP?

- **3-5x faster** than requests for typical HTTP workloads
- **2-3x faster JSON parsing** with integrated orjson
- **100% API compatible** with requests - true drop-in replacement
- **Zero configuration** required for optimal performance
- **Built on Rust** - memory safe and production ready

## 📦 Installation

```bash
pip install rapidhttp
```

No Rust toolchain needed - pre-built wheels are provided for all major platforms.

## 🎓 Quick Start

RapidHTTP is a **drop-in replacement** for requests. If you know requests, you already know RapidHTTP.

```python
import rapidhttp as requests

# GET request
r = requests.get('https://api.github.com/events')
print(r.status_code)  # 200
print(r.json()[0]['type'])

# POST with JSON
r = requests.post('https://httpbin.org/post', json={'key': 'value'})

# POST with form data
r = requests.post('https://httpbin.org/post', data={'key': 'value'})

# Custom headers
r = requests.get('https://api.github.com/user',
                 headers={'Authorization': 'token YOUR_TOKEN'})

# Query parameters
r = requests.get('https://httpbin.org/get',
                 params={'key1': 'value1', 'key2': 'value2'})

# Timeouts
r = requests.get('https://api.github.com/events', timeout=5)
```

### Sessions for Connection Pooling

```python
import rapidhttp as requests

# Session automatically pools connections
session = requests.Session()
session.headers.update({'User-Agent': 'my-app/1.0'})

# Connections are reused across requests
for i in range(100):
    r = session.get(f'https://api.example.com/items/{i}')
    print(r.json())
```

### Error Handling

```python
import rapidhttp as requests
from rapidhttp import HTTPError, Timeout, ConnectionError

try:
    r = requests.get('https://api.github.com/invalid', timeout=5)
    r.raise_for_status()
except HTTPError as e:
    print(f'HTTP error: {e}')
except Timeout as e:
    print(f'Request timed out: {e}')
except ConnectionError as e:
    print(f'Connection error: {e}')
```

## 📊 Performance

Based on local benchmark tests (500 GET requests to localhost):

```
Library      Requests/sec    Latency (median)    Relative Speed
-----------------------------------------------------------------
RapidHTTP    9,717          0.09ms              1.0x (baseline)
requests     3,040          0.32ms              3.2x slower
```

JSON POST performance (300 requests with 3.8KB payload):

```
Library      Requests/sec    Parse Time    Relative Speed
---------------------------------------------------------
RapidHTTP    6,922          6.75μs        1.0x (baseline)
requests     2,634          14.92μs       2.6x slower
```

_Benchmarks run on MacBook Pro M1, Python 3.11. Results may vary based on system and network conditions._

**Performance Features:**

- Automatic connection pooling and reuse
- Fast JSON parsing via orjson integration
- Efficient memory usage with Rust's zero-copy operations
- HTTP/2 support via reqwest/hyper

## ✨ Supported Features

### Core Functions

- ✅ `requests.get()`, `post()`, `put()`, `patch()`, `delete()`, `head()`, `options()`
- ✅ `requests.request()` - universal method
- ✅ Sessions with connection pooling
- ✅ JSON encoding/decoding
- ✅ Form data submission
- ✅ Custom headers
- ✅ Query parameters
- ✅ Timeouts
- ✅ Authentication (Basic, Bearer)
- ✅ Error handling with proper exceptions

### Response Object

- ✅ `Response.status_code`, `headers`, `url`
- ✅ `Response.text`, `content`, `json()`
- ✅ `Response.raise_for_status()`
- ✅ `Response.ok`, `is_redirect`
- ✅ `Response.iter_content()`, `iter_lines()` for streaming

### Exceptions

- ✅ `HTTPError`, `ConnectionError`, `Timeout`
- ✅ `ConnectTimeout`, `ReadTimeout`, `TooManyRedirects`
- ✅ `RequestException`, `URLRequired`, `JSONDecodeError`

## 🛠 Building from Source

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Clone and build
git clone https://github.com/Ray0907/rapidhttp.git
cd rapidhttp

# Install dependencies
pip install maturin orjson

# Build in release mode
maturin develop --release

# Run benchmarks
python test_server.py  # Terminal 1
python simple_benchmark.py  # Terminal 2
```

## 📝 Requirements

- **Python**: 3.8 or higher
- **Platforms**: Linux, macOS, Windows
- **Architectures**: x86_64, aarch64 (ARM64)

## 🔧 Technical Details

RapidHTTP combines Python's simplicity with Rust's performance:

- **Rust core** powered by [reqwest](https://github.com/seanmonstar/reqwest) + [hyper](https://github.com/hyperium/hyper)
- **PyO3** for seamless Python-Rust interop
- **orjson** integration for fast JSON parsing
- **Memory safe** - no segfaults or undefined behavior
- **Production-ready** HTTP stack used by millions

## 🤝 Migration from requests

Migration is effortless - just change your import:

```python
# Before
import requests
r = requests.get('https://api.github.com/events')

# After
import rapidhttp as requests
r = requests.get('https://api.github.com/events')
```

That's it! All your existing code continues to work.

## 📄 License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

RapidHTTP stands on the shoulders of giants:

- [requests](https://github.com/psf/requests) - The elegant HTTP library that inspired our API
- [reqwest](https://github.com/seanmonstar/reqwest) - The powerful Rust HTTP client at our core
- [hyper](https://github.com/hyperium/hyper) - The fast, safe HTTP implementation
- [PyO3](https://github.com/PyO3/pyo3) - Rust bindings for Python
- [orjson](https://github.com/ijl/orjson) - Fast JSON parsing

---

**Made with ⚡ and 🦀**
