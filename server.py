import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Your Render URL
base_url = "https://puchai-poem-generator.onrender.com"
mcp_url = f"{base_url}/mcp"

# Get your auth token
auth_token = os.getenv('AUTH_TOKEN')
print(f"🔐 Using auth token: {auth_token[:10]}..." if auth_token else "❌ No AUTH_TOKEN found!")

# Test 1: MCP endpoint without auth (should return 401)
print("\n🔍 Test 1: MCP without authentication")
try:
    payload = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
    response = requests.post(mcp_url, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: MCP endpoint with auth
print("\n🔍 Test 2: MCP with Bearer token authentication")
if auth_token:
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_token}"
        }
        payload = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
        response = requests.post(mcp_url, json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

# Test 3: Test tools/list
print("\n🔍 Test 3: List available tools")
if auth_token:
    try:
        headers = {
            "Content-Type": "application/json", 
            "Authorization": f"Bearer {auth_token}"
        }
        payload = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        response = requests.post(mcp_url, json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            tools = data.get('result', {}).get('tools', [])
            print(f"Found {len(tools)} tools:")
            for tool in tools:
                print(f"  - {tool['name']}: {tool['description']}")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

# Test 4: Test poem generation
print("\n🔍 Test 4: Generate a quick poem")
if auth_token:
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_token}"
        }
        payload = {
            "jsonrpc": "2.0",
            "id": 3, 
            "method": "tools/call",
            "params": {
                "name": "quick_poem",
                "arguments": {"theme": "testing"}
            }
        }
        response = requests.post(mcp_url, json=payload, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Poem generated successfully!")
            data = response.json()
            content = data.get('result', {}).get('content', [])
            if content:
                print("📝 Generated poem:")
                print(content[0].get('text', 'No text found'))
        else:
            print(f"❌ Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "="*50)
print("🔧 DEBUG INFO:")
print(f"AUTH_TOKEN exists: {'Yes' if auth_token else 'No'}")
print(f"AUTH_TOKEN length: {len(auth_token) if auth_token else 0}")
print("Make sure AUTH_TOKEN is set in Render environment variables!")