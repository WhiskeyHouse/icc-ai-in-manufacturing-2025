#!/usr/bin/env python3
"""
Test script for the Llama Index RAG service.
"""
import os
import argparse
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


def test_health(base_url):
    """Test the health endpoint."""
    print("\n🔍 Testing health endpoint...")
    response = requests.get(f"{base_url}/api/v1/health")
    if response.status_code == 200:
        print("✅ Health check successful")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Health check failed with status code {response.status_code}")
        print(response.text)
    return response.status_code == 200


def test_tables(base_url):
    """Test the tables endpoint."""
    print("\n🔍 Testing tables endpoint...")
    response = requests.get(f"{base_url}/api/v1/tables")
    if response.status_code == 200:
        print("✅ Tables endpoint successful")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Tables endpoint failed with status code {response.status_code}")
        print(response.text)
    return response.status_code == 200


def test_query(base_url, query, model=None, table_name=None):
    """Test the query endpoint."""
    print(f"\n🔍 Testing query: '{query}'")

    payload = {"query": query, "similarity_top_k": 3}

    if model:
        payload["model"] = model

    if table_name:
        payload["table_name"] = table_name

    response = requests.post(f"{base_url}/api/v1/query", json=payload)

    if response.status_code == 200:
        print("✅ Query successful")
        result = response.json()
        print(f"📝 Response: {result['response']}")
        print("\n📊 Source Nodes:")
        for i, node in enumerate(result.get("source_nodes", []), 1):
            print(f"  {i}. Score: {node.get('score', 'N/A')}")
            metadata = node.get("metadata", {})
            if metadata:
                print(f"     Table: {metadata.get('table_name', 'Unknown')}")
                print(f"     Columns: {', '.join(metadata.get('column_names', []))}")
        print(f"\n⏱️ Processing time: {result.get('processing_time', 0):.2f} seconds")
    else:
        print(f"❌ Query failed with status code {response.status_code}")
        print(response.text)

    return response.status_code == 200


def main():
    parser = argparse.ArgumentParser(description="Test the Llama Index RAG API")
    parser.add_argument(
        "--url", default="http://localhost:8080", help="Base URL of the service"
    )
    parser.add_argument(
        "--query",
        default="What are the steps in the mashing process for rye bourbon?",
        help="Query to test",
    )
    parser.add_argument("--model", default=None, help="OpenAI model to use")
    parser.add_argument("--table", default=None, help="Specific table to query")
    args = parser.parse_args()

    # Check if OPENAI_API_KEY is set
    if not os.environ.get("OPENAI_API_KEY"):
        print("⚠️ Warning: OPENAI_API_KEY environment variable is not set.")

    # Test each endpoint
    health_ok = test_health(args.url)
    tables_ok = test_tables(args.url)

    # Only test query if health and tables endpoints are working
    if health_ok and tables_ok:
        test_query(args.url, args.query, args.model, args.table)


if __name__ == "__main__":
    main()
