#!/usr/bin/env python3
"""
Simple Local Performance Test
==============================

Benchmark RapidHTTP vs requests using a local test server
Tests both regular requests and JSON optimization
"""

import time
import statistics
import json
import requests as test_requests


def check_server_ready(url, max_retries=10):
    """Check if server is ready"""
    for i in range(max_retries):
        try:
            r = test_requests.get(url, timeout=2)
            if r.status_code == 200:
                return True
        except:
            time.sleep(0.5)
    return False


def benchmark_library(lib, lib_name, url, num_requests=500):
    """Test performance of a single library"""
    print(f"\nTesting {lib_name}...")
    
    # Warmup
    for _ in range(10):
        try:
            lib.get(url, timeout=5)
        except Exception as e:
            print(f"  Warmup error: {e}")
            return None
    
    # Test
    times = []
    errors = 0
    
    for i in range(num_requests):
        start = time.perf_counter()
        try:
            r = lib.get(url, timeout=5)
            if r.status_code == 200:
                times.append(time.perf_counter() - start)
            else:
                errors += 1
        except:
            errors += 1
    
    if not times:
        print("  All requests failed")
        return None
    
    times_sorted = sorted(times)
    
    return {
        'library': lib_name,
        'count': len(times),
        'errors': errors,
        'mean': statistics.mean(times),
        'median': statistics.median(times),
        'p95': times_sorted[int(len(times_sorted) * 0.95)],
        'req_per_sec': len(times) / sum(times)
    }


def benchmark_json_parser(lib, lib_name, json_data, url, iterations=1000):
    """Test pure JSON parsing performance with real HTTP requests"""
    print(f"\nTesting {lib_name} JSON parser...")

    # Warmup
    for _ in range(5):
        try:
            lib.post(url, json=json_data, timeout=5)
        except:
            pass

    # Test parsing only (excluding network time)
    parse_times = []

    for _ in range(iterations):
        try:
            r = lib.post(url, json=json_data, timeout=5)
            if r.status_code == 200:
                # Measure only JSON parsing time
                start = time.perf_counter()
                r.json()
                parse_time = time.perf_counter() - start
                parse_times.append(parse_time)
        except:
            pass

    if not parse_times:
        print("  Parsing failed")
        return None

    return {
        'library': lib_name,
        'iterations': len(parse_times),
        'parse_median': statistics.median(parse_times),
        'parse_mean': statistics.mean(parse_times),
        'ops_per_sec': len(parse_times) / sum(parse_times)
    }


def benchmark_json(lib, lib_name, url, payload, num_requests=200):
    """Test JSON POST and parsing performance"""
    print(f"\nTesting {lib_name} JSON...")
    
    # Warmup
    for _ in range(5):
        try:
            lib.post(url, json=payload, timeout=5)
        except Exception as e:
            print(f"  Warmup error: {e}")
            return None
    
    # Test
    request_times = []
    parse_times = []
    errors = 0
    
    for i in range(num_requests):
        try:
            start = time.perf_counter()
            r = lib.post(url, json=payload, timeout=5)
            request_time = time.perf_counter() - start
            
            if r.status_code == 200:
                parse_start = time.perf_counter()
                r.json()
                parse_time = time.perf_counter() - parse_start
                
                request_times.append(request_time)
                parse_times.append(parse_time)
            else:
                errors += 1
        except:
            errors += 1
    
    if not request_times:
        print("  All requests failed")
        return None
    
    return {
        'library': lib_name,
        'count': len(request_times),
        'errors': errors,
        'request_median': statistics.median(request_times),
        'parse_median': statistics.median(parse_times),
        'req_per_sec': len(request_times) / sum(request_times)
    }


def run_benchmark():
    """Run benchmark test"""
    print("=" * 70)
    print("  Local Server Performance Test")
    print("=" * 70)
    
    # Check libraries
    libs = {}
    
    try:
        import rapidhttp
        libs['RapidHTTP'] = rapidhttp
        print("\n✓ RapidHTTP loaded")
    except ImportError:
        print("\n✗ RapidHTTP not installed")
    
    try:
        import requests
        libs['requests'] = requests
        print("✓ requests loaded")
    except ImportError:
        print("✗ requests not installed")
    
    if not libs:
        print("\n❌ No HTTP libraries available!")
        return
    
    # Check server
    test_url = "http://127.0.0.1:8000/"
    print(f"\nChecking server {test_url} ...")
    
    if not check_server_ready(test_url):
        print("\n❌ Server not ready! Start with: python test_server.py")
        return
    
    print("✓ Server ready")
    
    # Test 1: Regular GET requests
    print(f"\n{'=' * 70}")
    print("  Test 1: GET Requests")
    print(f"{'=' * 70}")
    
    num_requests = 500
    print(f"Configuration: {num_requests} requests to {test_url}")
    
    results = []
    for lib_name, lib in libs.items():
        result = benchmark_library(lib, lib_name, test_url, num_requests)
        if result:
            results.append(result)
    
    # Print GET results
    if results:
        print(f"\n{'Library':<12} {'Success':<8} {'Mean':<12} {'Median':<12} {'P95':<12} {'Req/sec':<12}")
        print("-" * 75)
        
        results.sort(key=lambda x: x['median'])
        
        for r in results:
            print(f"{r['library']:<12} {r['count']:<8} "
                  f"{r['mean']*1000:>8.2f}ms  "
                  f"{r['median']*1000:>8.2f}ms  "
                  f"{r['p95']*1000:>8.2f}ms  "
                  f"{r['req_per_sec']:>8.1f}")
        
        if len(results) > 1:
            fastest = results[0]
            speedup = results[1]['median'] / fastest['median']
            time_saved = (results[1]['median'] - fastest['median']) * 1000
            
            print(f"\n🏆 Fastest: {fastest['library']}")
            print(f"  • {speedup:.2f}x faster than {results[1]['library']}")
            print(f"  • Saves {time_saved:.2f}ms per request")
    
    # Test 2: JSON POST requests
    print(f"\n{'=' * 70}")
    print("  Test 2: JSON POST Requests")
    print(f"{'=' * 70}")
    
    json_url = "http://127.0.0.1:8000/echo"
    payload = {
        'users': [
            {
                'id': i,
                'name': f'user{i}',
                'email': f'user{i}@example.com',
                'active': i % 2 == 0
            }
            for i in range(50)
        ]
    }
    payload_size = len(json.dumps(payload))
    num_json_requests = 300
    
    print(f"Configuration: {num_json_requests} requests, payload size: {payload_size} bytes")
    
    json_results = []
    for lib_name, lib in libs.items():
        result = benchmark_json(lib, lib_name, json_url, payload, num_json_requests)
        if result:
            json_results.append(result)
    
    # Print JSON results
    if json_results:
        print(f"\n{'Library':<12} {'Success':<8} {'Request':<12} {'Parse':<12} {'Req/sec':<12}")
        print("-" * 70)
        
        json_results.sort(key=lambda x: x['request_median'])
        
        for r in json_results:
            print(f"{r['library']:<12} {r['count']:<8} "
                  f"{r['request_median']*1000:>8.2f}ms  "
                  f"{r['parse_median']*1000000:>8.2f}μs  "
                  f"{r['req_per_sec']:>8.1f}")
        
        if len(json_results) > 1:
            fastest = json_results[0]
            req_speedup = json_results[1]['request_median'] / fastest['request_median']
            parse_speedup = json_results[1]['parse_median'] / fastest['parse_median']
            
            print(f"\n🏆 Fastest: {fastest['library']}")
            print(f"  • {req_speedup:.2f}x faster requests than {json_results[1]['library']}")
            print(f"  • {parse_speedup:.2f}x faster JSON parsing than {json_results[1]['library']}")
    
    # Test 3: JSON Parser Performance with Real Requests
    print(f"\n{'=' * 70}")
    print("  Test 3: JSON Parser Performance (Real HTTP Requests)")
    print(f"{'=' * 70}")

    # Test with different data sizes
    test_payloads = {
        'Small': {'status': 'ok', 'value': 42, 'message': 'Hello'},
        'Medium': {
            'users': [
                {'id': i, 'name': f'user{i}', 'email': f'user{i}@test.com'}
                for i in range(100)
            ]
        },
        'Large': {
            'records': [
                {
                    'id': i,
                    'data': {'field1': f'val{i}', 'field2': i * 1.5, 'list': list(range(5))}
                }
                for i in range(500)
            ]
        }
    }

    for size_name, test_payload in test_payloads.items():
        size_bytes = len(json.dumps(test_payload))
        iterations = 5000 if size_name == 'Small' else 1000 if size_name == 'Medium' else 500

        print(f"\n{size_name} JSON ({size_bytes} bytes, {iterations} iterations):")

        parser_results = []
        for lib_name, lib in libs.items():
            result = benchmark_json_parser(lib, lib_name, test_payload, json_url, iterations)
            if result:
                parser_results.append(result)
        
        if parser_results:
            print(f"\n{'Library':<12} {'Iterations':<12} {'Median':<12} {'Mean':<12} {'Ops/sec':<12}")
            print("-" * 70)
            
            parser_results.sort(key=lambda x: x['parse_median'])
            
            for r in parser_results:
                print(f"{r['library']:<12} {r['iterations']:<12} "
                      f"{r['parse_median']*1000000:>8.2f}μs  "
                      f"{r['parse_mean']*1000000:>8.2f}μs  "
                      f"{r['ops_per_sec']:>8.0f}")
            
            if len(parser_results) > 1:
                fastest = parser_results[0]
                speedup = parser_results[1]['parse_median'] / fastest['parse_median']
                print(f"  → {fastest['library']} is {speedup:.2f}x faster than {parser_results[1]['library']}")
    
    print(f"\n{'=' * 70}\n")


if __name__ == '__main__':
    try:
        run_benchmark()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
