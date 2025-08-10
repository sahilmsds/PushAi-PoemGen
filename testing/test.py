import requests

url = "http://localhost:8000/mcp"
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
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
print(response.status_code, response.text)
