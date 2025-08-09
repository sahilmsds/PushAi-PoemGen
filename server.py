import os
from flask import Flask, request, jsonify

app = Flask(__name__, static_folder="static")

@app.route("/", methods=["GET"])
def index():
    return app.send_static_file("index.html")

@app.route("/generate_poem", methods=["POST"])
def generate_poem():
    data = request.get_json()

    theme = data.get("theme", "life")
    style = data.get("style", "free verse")
    length = data.get("length", "short")

    base_lines = [
        f"In {theme}'s quiet corners I dwell,",
        f"A {style} whisper in the air's soft swell,",
        f"Moments drift like clouds in endless skies,",
        f"And hope is the sun that will always rise."
    ]

    medium_lines = [
        f"Through {theme}'s winding paths I roam,",
        f"Echoes of {style} songs call me home,",
        f"Stars above tell tales of old,",
        f"My heart beats stories yet untold.",
        f"Dreams like rivers flow and bend,",
        f"Seeking places where shadows end."
    ]

    long_lines = [
        f"In the vast expanse of {theme}, I find my peace,",
        f"Where {style} melodies never cease,",
        f"The moonlight dances on gentle streams,",
        f"And carries with it forgotten dreams.",
        f"Whispers of time in soft embrace,",
        f"Paint a smile upon my face.",
        f"Through trials and joys, I weave my way,",
        f"Hoping for a brighter day."
    ]

    if length == "short":
        chosen_lines = base_lines
    elif length == "medium":
        chosen_lines = medium_lines
    else:  # long
        chosen_lines = long_lines

    poem = "\n".join(chosen_lines)
    return jsonify({
        "theme": theme,
        "style": style,
        "length": length,
        "poem": poem
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
