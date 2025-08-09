import sys
import json
import os
import requests

RAILWAY_API_URL = os.environ.get(
    "RAILWAY_API_URL",
    "http://localhost:8000"  # Default to local for testing
)

def main():
    while True:
        line = sys.stdin.readline()
        if not line:
            break

        try:
            msg = json.loads(line)
            method = msg.get("method")
            id_ = msg.get("id")

            if method == "listTools":
                sys.stdout.write(json.dumps({
                    "id": id_,
                    "result": {
                        "tools": [{
                            "name": "poemgen",
                            "description": "Generate a poem by theme, style, and length",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "theme": {"type": "string"},
                                    "style": {"type": "string"},
                                    "length": {"type": "string"}
                                },
                                "required": ["theme", "style", "length"]
                            }
                        }]
                    }
                }) + "\n")
                sys.stdout.flush()

            elif method == "callTool":
                params = msg.get("params", {}).get("arguments", {})
                try:
                    response = requests.post(
                        f"{RAILWAY_API_URL}/generate_poem",
                        json=params,
                        timeout=10
                    )
                    data = response.json()
                    content = data.get("poem", "No poem generated.")
                except Exception as e:
                    content = f"Request failed: {str(e)}"

                sys.stdout.write(json.dumps({
                    "id": id_,
                    "result": {"content": content}
                }) + "\n")
                sys.stdout.flush()

        except Exception as e:
            sys.stdout.write(json.dumps({"error": str(e)}) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
