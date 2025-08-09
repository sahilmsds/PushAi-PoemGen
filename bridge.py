import sys
import json
import os
import requests

RAILWAY_API_URL = os.environ.get(
    "RAILWAY_API_URL",
    "https://pushai-poemgen-production-38f5.up.railway.app"
)  # Change this or set env var accordingly

def main():
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break

            msg = json.loads(line)
            method = msg.get("method")
            id_ = msg.get("id")

            if method == "listTools":
                sys.stdout.write(json.dumps({
                    "id": id_,
                    "result": {
                        "tools": [
                            {
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
                            }
                        ]
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
                    if "poem" in data:
                        result_content = data["poem"]
                    else:
                        result_content = f"Error: {data.get('error', 'Unknown error')}"
                except Exception as e:
                    result_content = f"Request failed: {str(e)}"

                sys.stdout.write(json.dumps({
                    "id": id_,
                    "result": {
                        "content": result_content
                    }
                }) + "\n")
                sys.stdout.flush()

        except Exception as e:
            sys.stdout.write(json.dumps({
                "error": str(e)
            }) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
