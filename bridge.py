import sys
import json
import os
import requests

RAILWAY_API_URL = os.environ.get(
    "RAILWAY_API_URL",
    "https://pushai-poemgen-production-38f5.up.railway.app"
)

def main():
    print(f"[bridge] Using RAILWAY_API_URL: {RAILWAY_API_URL}", file=sys.stderr)
    sys.stderr.flush()

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
                print(f"[bridge] Received callTool with params: {params}", file=sys.stderr)
                sys.stderr.flush()

                try:
                    response = requests.post(
                        f"{RAILWAY_API_URL}/generate_poem",
                        json=params,
                        timeout=10
                    )
                    data = response.json()
                    print(f"[bridge] Response from Flask API: {data}", file=sys.stderr)
                    sys.stderr.flush()

                    if "poem" in data:
                        result_content = data["poem"]
                    else:
                        result_content = f"Error: {data.get('error', 'Unknown error')}"

                except Exception as e:
                    result_content = f"Request failed: {str(e)}"
                    print(f"[bridge] Exception during request: {e}", file=sys.stderr)
                    sys.stderr.flush()

                sys.stdout.write(json.dumps({
                    "id": id_,
                    "result": {
                        "content": result_content
                    }
                }) + "\n")
                sys.stdout.flush()

        except Exception as e:
            print(f"[bridge] Exception in main loop: {e}", file=sys.stderr)
            sys.stderr.flush()
            sys.stdout.write(json.dumps({
                "error": str(e)
            }) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
