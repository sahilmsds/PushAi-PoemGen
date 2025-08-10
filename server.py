from flask import Flask, request, jsonify
from transformers import pipeline

app = Flask(__name__)

generator = pipeline('text-generation', model='distilgpt2', device=-1)

@app.route('/')
def home():
    return 'Poem Generator API is running.'

@app.route('/generate_poem', methods=['POST'])
def generate_poem():
    data = request.json
    prompt = data.get('prompt', 'Write a short free verse poem about life.')
    try:
        results = generator(prompt, max_length=50, num_return_sequences=1, do_sample=True, temperature=0.8)
        poem = results[0]['generated_text']
        return jsonify({'poem': poem})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
