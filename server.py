import os
from flask import Flask, request, jsonify
from transformers import pipeline, set_seed

app = Flask(__name__, static_folder="static")

# Initialize the generator once globally for efficiency
generator = pipeline('text-generation', model='distilgpt2')
set_seed(42)  # for reproducibility

@app.route("/", methods=["GET"])
def index():
    return app.send_static_file("index.html")

@app.route("/generate_poem", methods=["POST"])
def generate_poem():
    data = request.get_json() or {}

    theme = data.get("theme", "life")
    style = data.get("style", "free verse")
    length = data.get("length", "short")

    # Customize max_length based on length parameter
    max_length_map = {"short": 50, "medium": 100, "long": 150}
    max_length = max_length_map.get(length, 50)

    prompt = f"Write a {length} {style} poem about {theme}:"

    # Generate text with truncation enabled and reasonable parameters
    results = generator(
        prompt,
        max_length=max_length,
        num_return_sequences=1,
        do_sample=True,
        temperature=0.8,
        top_p=0.9,
        truncation=True,
        pad_token_id=generator.tokenizer.eos_token_id
    )

    poem = results[0]['generated_text'].strip()

    # Remove prompt from output if repeated
    if poem.lower().startswith(prompt.lower()):
        poem = poem[len(prompt):].strip()

    return jsonify({
        "theme": theme,
        "style": style,
        "length": length,
        "poem": poem
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
