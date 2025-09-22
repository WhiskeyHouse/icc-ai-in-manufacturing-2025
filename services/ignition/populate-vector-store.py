#!/usr/bin/env python3
"""
Populate Vector Store with Demo Patterns
Indexes our demo patterns into the RAG system
"""

import json
import requests
import time

RAG_BASE_URL = "http://localhost:8086"

def read_json_file(filepath):
    """Read JSON file and return content"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

def read_text_file(filepath):
    """Read text file and return content"""
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

def add_to_vector_store(text, metadata):
    """Add document to vector store"""
    try:
        response = requests.post(
            f"{RAG_BASE_URL}/api/v1/test_vector_store",
            json={
                "text": text,
                "metadata": metadata
            },
            timeout=30
        )
        return response.json() if response.status_code == 200 else {"success": False, "error": response.text}
    except Exception as e:
        return {"success": False, "error": str(e)}

def query_vector_store(query_text):
    """Query the vector store"""
    try:
        response = requests.post(
            f"{RAG_BASE_URL}/api/v1/query",
            json={"query": query_text},
            timeout=30
        )
        return response.json() if response.status_code == 200 else {"error": response.text}
    except Exception as e:
        return {"error": str(e)}

def main():
    print("🔄 Populating Vector Store with Demo Patterns")
    print("=" * 60)
    
    # Pattern files to index
    patterns = [
        {
            "file": "demo-patterns/fermentation-tank-component.json",
            "type": "json",
            "metadata": {
                "source": "whk_demo_patterns",
                "type": "perspective_component",
                "category": "fermentation",
                "component_type": "ia.display.tank",
                "whk_standard": "fermentation_v2",
                "compliance": "FDA"
            }
        },
        {
            "file": "demo-patterns/pump-control-script.py",
            "type": "text",
            "metadata": {
                "source": "whk_demo_patterns", 
                "type": "jython_script",
                "category": "pump_control",
                "script_type": "gateway_timer",
                "whk_standard": "pump_v1",
                "compliance": "FDA"
            }
        },
        {
            "file": "demo-patterns/batch-recipe-selector.json",
            "type": "json",
            "metadata": {
                "source": "whk_demo_patterns",
                "type": "perspective_component", 
                "category": "batch_management",
                "component_type": "ia.display.dropdown",
                "whk_standard": "batch_v3",
                "compliance": "FDA"
            }
        }
    ]
    
    # Index each pattern
    successful = 0
    total = len(patterns)
    
    for i, pattern in enumerate(patterns, 1):
        print(f"\n📄 [{i}/{total}] Processing: {pattern['file']}")
        
        # Read file content
        if pattern['type'] == 'json':
            content = read_json_file(pattern['file'])
            if content:
                text = json.dumps(content, indent=2)
            else:
                continue
        else:
            text = read_text_file(pattern['file'])
            if not text:
                continue
        
        # Add to vector store
        result = add_to_vector_store(text, pattern['metadata'])
        
        if result.get('success'):
            print(f"✅ Indexed successfully")
            successful += 1
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
        
        # Small delay between requests
        time.sleep(0.5)
    
    print(f"\n📊 Indexing Summary:")
    print(f"   ✅ Successfully indexed: {successful}/{total}")
    
    if successful > 0:
        print(f"\n🔍 Testing Vector Store Queries:")
        
        # Test queries
        test_queries = [
            "Create a fermentation tank control panel",
            "Generate pump control script with safety",
            "Design batch recipe selector with FDA compliance"
        ]
        
        for query in test_queries:
            print(f"\n📝 Query: {query}")
            result = query_vector_store(query)
            
            if 'error' not in result:
                print(f"✅ Found {len(result.get('results', []))} relevant documents")
                if result.get('results'):
                    top_result = result['results'][0]
                    print(f"   🎯 Top match: {top_result.get('metadata', {}).get('category', 'unknown')} (score: {top_result.get('score', 0):.3f})")
            else:
                print(f"❌ Query failed: {result['error']}")
    
    print(f"\n🎉 Vector store population complete!")
    return successful == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)