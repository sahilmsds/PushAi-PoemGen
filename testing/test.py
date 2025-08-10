import requests

API_URL = "https://puchai-poem-generator.onrender.com/generate_poem"

def test_generate_poem():
    payload = {
        "theme": "love",
        "style": "free verse",
        "length": "short"
    }
    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        poem = data.get("poem", "")
        print("Generated Poem:\n")
        print(poem)
    except Exception as e:
        print(f"Error during request: {e}")

if __name__ == "__main__":
    test_generate_poem()

