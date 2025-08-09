import os
from flask import Flask, request, jsonify
from transformers import pipeline

app = Flask(__name__, static_folder="static")

# Initialize text generation pipeline once
generator = pipeline('text-generation', model='distilgpt2')

@app.route("/", methods=["GET"])
def index():
    return app.send_static_file("index.html")

@app.route("/generate_poem", methods=["POST"])
def generate_poem():
    data = request.get_json()

    theme = data.get("theme", "life")
    style = data.get("style", "")  # optional
    length = data.get("length", "short")

    # Construct prompt based on input
    prompt = f"Write a {length} poem about {theme}."
    if style:
        prompt += f" The poem style should be {style}."

    # Generate poem with transformer pipeline
    result = generator(prompt, max_length=100, num_return_sequences=1)
    poem = result[0]['generated_text'].strip()

    return jsonify({
        "theme": theme,
        "style": style,
        "length": length,
        "poem": poem
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
