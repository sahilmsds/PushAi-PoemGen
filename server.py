# server.py
from flask import Flask, request, jsonify
import random

app = Flask(__name__)

def generate_poem(theme):
    # A very simple rule-based generator
    lines = [
        f"The {theme} whispers softly through the night,",
        f"In {theme}'s arms, the world feels right,",
        f"Under the {theme} sky, dreams take flight,",
        f"The {theme} sings in silver light."
    ]
    random.shuffle(lines)
    return "\n".join(lines)

@app.route("/generate_poem", methods=["POST"])
def poem_endpoint():
    data = request.get_json()
    theme = data.get("theme", "nature")
    poem = generate_poem(theme)
    return jsonify({"poem": poem})

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Poem MCP Server is running!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)