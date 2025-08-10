import sys
import json
from transformers import pipeline

# Initialize generator once
generator = pipeline('text-generation', model='distilgpt2', device=-1)

def generate_poem(params):
    theme = params.get('theme', 'life')
    style = params.get('style', 'free verse')
    length = params.get('length', 'short')

    prompt = f"Write a {length} {style} poem about {theme}."

    results = generator(prompt, max_length=100, num_return_sequences=1)
    return results[0]['generated_text']

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
                    poem = generate_poem(params)
                    result_content = poem
                except Exception as e:
                    result_content = f"Generation failed: {str(e)}"

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
