import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get auth token from environment
auth_token = os.getenv('AUTH_TOKEN')
if not auth_token:
    print("❌ Error: AUTH_TOKEN not found in environment variables!")
    print("Make sure you have AUTH_TOKEN set in your .env file")
    exit(1)

url = "http://localhost:8086/mcp"  # Updated to port 8086
payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "quick_poem",
        "arguments": {
            "theme": "Love"
        }
    }
}

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {auth_token}"  # Added Bearer token auth
}

print(f"🚀 Testing MCP server at {url}")
print(f"🔐 Using auth token: {auth_token[:10]}...")

try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"📊 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Success!")
        print("📝 Response:")
        print(response.text)
    else:
        print("❌ Error Response:")
        print(response.text)
        
except requests.exceptions.RequestException as e:
    print(f"❌ Connection Error: {e}")
    print("Make sure your server is running on localhost:8086")