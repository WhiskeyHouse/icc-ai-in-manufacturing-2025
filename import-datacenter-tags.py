#!/usr/bin/env python3
"""
Script to import DataCenterDemo tags into Ignition Gateway
"""

import json
import requests
import base64
from pathlib import Path

# Configuration
GATEWAY_URL = "http://localhost:9088"
USERNAME = "admin"
PASSWORD = "password"  # Update with actual password
TAG_PROVIDER = "DataCenterDemo"
TAGS_FILE = Path("ignition-projects/DataCenterDemo/DataCenterDemoTags.json")


def import_tags():
    """Import tags from JSON file to Ignition tag provider"""

    # Read the tags JSON file
    print(f"Reading tags from {TAGS_FILE}...")
    with open(TAGS_FILE, "r") as f:
        tags_data = json.load(f)

    print(f"Found {len(tags_data.get('tags', []))} tags to import")

    # Prepare the import payload
    # The tags need to be imported to the root of the tag provider
    import_payload = {
        "tagProvider": TAG_PROVIDER,
        "basePath": "",  # Import to root
        "collisionPolicy": "o",  # Overwrite existing
        "importData": tags_data,
    }

    # Prepare authentication
    auth = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
    headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}

    # Try using the system/tag-config endpoint
    import_url = f"{GATEWAY_URL}/system/tag-config/import"

    # Alternative: Try to create tags directly
    # We'll iterate through tags and create them one by one
    print(f"Importing tags to {TAG_PROVIDER} provider...")

    # First, let's try to see what structure we have
    if "tags" in tags_data:
        tags_to_import = tags_data["tags"]
    else:
        # The file might be the tag structure directly
        tags_to_import = [tags_data] if isinstance(tags_data, dict) else tags_data

    print(f"Processing {len(tags_to_import)} tag items...")

    # Try the webdev API endpoint for tag import
    webdev_url = f"{GATEWAY_URL}/system/webdev/DataCenterDemo/tags/import"

    try:
        # First attempt: Try webdev endpoint
        response = requests.post(webdev_url, json=tags_data, headers=headers)

        if response.status_code == 200:
            print("✅ Tags imported successfully via webdev!")
            result = response.json()
            if "results" in result:
                print(f"Import results: {result['results']}")
        else:
            print(f"WebDev endpoint failed with status: {response.status_code}")

            # Second attempt: Try system endpoint
            response = requests.post(import_url, json=import_payload, headers=headers)

            if response.status_code == 200:
                print("✅ Tags imported successfully via system endpoint!")
                result = response.json()
                if "results" in result:
                    print(f"Import results: {result['results']}")
            else:
                print(f"❌ Failed to import tags. Status: {response.status_code}")
                print(f"Response: {response.text[:500]}...")

    except Exception as e:
        print(f"❌ Error importing tags: {e}")


if __name__ == "__main__":
    import_tags()
