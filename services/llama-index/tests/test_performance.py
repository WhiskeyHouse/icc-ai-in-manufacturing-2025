"""
Performance benchmarking tests for the llama-index service.
These tests measure the response time and throughput of the API.
"""

import pytest
import time
import statistics
import concurrent.futures
from fastapi import status


@pytest.mark.slow
@pytest.mark.integration
def test_api_response_time(test_client):
    """Test the response time of the API endpoints."""
    # Define test endpoints and payload
    endpoints = [
        {"name": "Health Check", "url": "/health", "method": "get", "payload": None},
        {
            "name": "Query API",
            "url": "/api/v1/query",
            "method": "post",
            "payload": {"query": "What is bourbon whiskey?", "model": "gpt-4o-mini"},
        },
        {
            "name": "Table Query API",
            "url": "/api/v1/query/Recipe",
            "method": "post",
            "payload": {"query": "Tell me about rye whiskey", "model": "gpt-4o-mini"},
        },
    ]

    # Number of requests per endpoint
    num_requests = 5

    results = {}

    # Test each endpoint
    for endpoint in endpoints:
        name = endpoint["name"]
        url = endpoint["url"]
        method = endpoint["method"]
        payload = endpoint["payload"]

        response_times = []

        for _ in range(num_requests):
            start_time = time.time()

            if method == "get":
                response = test_client.get(url)
            elif method == "post":
                response = test_client.post(url, json=payload)
            else:
                raise ValueError(f"Unsupported method: {method}")

            end_time = time.time()
            response_time = end_time - start_time

            # Check that the response is valid
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_202_ACCEPTED,
            ]

            response_times.append(response_time)

            # Small delay to avoid overwhelming the server
            time.sleep(0.1)

        # Calculate statistics
        avg_response_time = statistics.mean(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        median_response_time = statistics.median(response_times)

        results[name] = {
            "avg": avg_response_time,
            "min": min_response_time,
            "max": max_response_time,
            "median": median_response_time,
        }

    # Log results
    for name, stats in results.items():
        print(f"\n{name} response times (seconds):")
        print(f"  Average: {stats['avg']:.4f}")
        print(f"  Minimum: {stats['min']:.4f}")
        print(f"  Maximum: {stats['max']:.4f}")
        print(f"  Median:  {stats['median']:.4f}")

    # Basic assertions to ensure response times are reasonable
    # These thresholds might need adjustment based on your environment
    assert results["Health Check"]["avg"] < 0.1, "Health check is too slow"

    # Since the query endpoints currently return a disabled message,
    # they should also be relatively fast
    assert results["Query API"]["avg"] < 0.5, "Query API is too slow"
    assert results["Table Query API"]["avg"] < 0.5, "Table Query API is too slow"


@pytest.mark.slow
@pytest.mark.integration
def test_concurrent_throughput(test_client):
    """Test the throughput of the API with concurrent requests."""

    # Define a simple query function
    def query_api(query_text):
        return test_client.post(
            "/api/v1/query", json={"query": query_text, "model": "gpt-4o-mini"}
        )

    # List of queries to send
    queries = [
        "What is bourbon whiskey?",
        "Tell me about rye whiskey.",
        "What are the ingredients in single malt?",
        "How long is bourbon aged?",
        "What barrels are used for rye whiskey?",
        "How to make whiskey?",
        "What is the difference between bourbon and scotch?",
        "How is whiskey distilled?",
        "What is the mash bill for bourbon?",
        "How to taste whiskey properly?",
    ]

    # Number of concurrent workers
    num_workers = 4

    # Start timer
    start_time = time.time()

    # Send requests concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        future_to_query = {
            executor.submit(query_api, query): query for query in queries
        }
        responses = []

        for future in concurrent.futures.as_completed(future_to_query):
            query = future_to_query[future]
            try:
                response = future.result()
                assert response.status_code in [
                    status.HTTP_200_OK,
                    status.HTTP_202_ACCEPTED,
                ]
                responses.append(response)
            except Exception as e:
                print(f"Query '{query}' generated an exception: {e}")

    # End timer
    end_time = time.time()
    total_time = end_time - start_time

    # Calculate throughput
    num_requests = len(queries)
    requests_per_second = num_requests / total_time

    print(f"\nThroughput test results:")
    print(f"  Total requests: {num_requests}")
    print(f"  Concurrent workers: {num_workers}")
    print(f"  Total time: {total_time:.4f} seconds")
    print(f"  Throughput: {requests_per_second:.2f} requests/second")

    # Assert that we meet a minimum throughput threshold
    # This threshold should be adjusted based on your requirements
    assert requests_per_second > 1.0, "Throughput is too low"
