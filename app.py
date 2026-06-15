from flask import Flask, render_template, request, Response, jsonify
from openai import OpenAI
import json

app = Flask(__name__)

client = OpenAI(
    base_url='https://api.tokenrouter.com/v1',
    api_key='sk-WiRzYpo1Od1DK9g8S50m0oLsrqnJlEv8ACyjUrfcns02Scdf',
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    messages = data.get('messages', [])
    
    # Ensure system prompt is present
    if not messages or messages[0].get('role') != 'system':
        messages.insert(0, {"role": "system", "content": "شما یک دستیار هوشمند و مودب هستید. لطفاً پاسخ‌های خود را به زبان فارسی و خلاصه بیان کنید."})
        
    def generate():
        try:
            stream = client.chat.completions.create(
                model="MiniMax-M3",
                messages=messages,
                stream=True,
                stream_options={"include_usage": True},
            )
            
            for chunk in stream:
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        # Send SSE data
                        yield f"data: {json.dumps({'content': delta.content})}\n\n"
            
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            yield "data: [DONE]\n\n"

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
