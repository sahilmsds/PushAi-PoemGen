from flask import Flask, request, jsonify
import random

app = Flask(__name__)

# Root route - just to check server health
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Poem MCP Server is running!"})

# New endpoint for poem generation
@app.route("/generate_poem", methods=["POST"])
def generate_poem():
    data = request.get_json()

    theme = data.get("theme", "life")
    style = data.get("style", "free verse")

    # Very basic poem generator
    lines = [
        f"In {theme}'s quiet corners I dwell,",
        f"A {style} whisper in the air's soft swell,",
        f"Moments drift like clouds in endless skies,",
        f"And hope is the sun that will always rise."
    ]

    # Shuffle for variation
    random.shuffle(lines)

    return jsonify({
        "theme": theme,
        "style": style,
        "poem": "\n".join(lines)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
