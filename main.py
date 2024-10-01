import asyncio
import re
import os
from flask import Flask, render_template_string, request

from edge_tts import Communicate

app = Flask(__name__)

# List of available voices
voices = {
    '1': 'en-US-AriaNeural',
    '2': 'en-US-GuyNeural',
    '3': 'ml-IN-MidhunNeural',
    '4': 'ml-IN-SobhanaNeural',
    '5': 'en-ZA-LeahNeural',
    '6': 'en-ZA-LukeNeural',
    '7': 'en-TZ-ElimuNeural',
    '8': 'en-TZ-ImaniNeural',
    '9': 'en-GB-LibbyNeural',
    '10': 'en-IN-NeerjaNeural',
    '11': 'en-IN-PrabhatNeural',
    '12': 'en-US-AnaNeural',
    '13': 'en-US-ChristopherNeural',
    '14': 'en-US-EricNeural',
    '15': 'en-US-JennyNeural',
    '16': 'en-US-MichelleNeural',
    '17': 'en-US-RogerNeural',
    '18': 'en-US-SteffanNeural',
}

# Function to preprocess text (removes unnecessary symbols and spaces)
def preprocess_text(text):
    text = re.sub(r'[^\w\s.,!?]', '', text)  # Remove special characters except punctuation
    text = re.sub(r'\s+', ' ', text).strip()  # Remove multiple spaces and trim
    return text

# Function to save text to speech
async def save_tts(text, selected_voice_code, rate, pitch):
    output_directory = "/storage/emulated/0/Download"  # Change this path as needed
    os.makedirs(output_directory, exist_ok=True)  # Create the directory if it doesn't exist
    output_path = f"{output_directory}/{selected_voice_code}.mp3"  # Change path as needed

    communicate = Communicate(
        text,
        voice=selected_voice_code,
        rate=rate,
        pitch=pitch
    )
    try:
        await communicate.save(output_path)
        return f"Audio saved to {output_path}"
    except Exception as e:
        return f"Error: {e}"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        selected_voice_code = voices.get(request.form['voice'])
        rate_choice = request.form['rate']
        pitch_choice = request.form['pitch']
        text = request.form['text']

        rate = convert_rate_to_percentage(rate_choice)
        pitch = convert_pitch_to_hz(pitch_choice)

        # Run TTS in a separate asyncio event loop
        result = asyncio.run(save_tts(preprocess_text(text), selected_voice_code, rate, pitch))
        return render_template_string(html_template, result=result, voices=voices)

    return render_template_string(html_template, result=None, voices=voices)

# Function to convert pitch selection to Hz
def convert_pitch_to_hz(pitch_choice):
    if pitch_choice == '1':  # -50%
        return '-50Hz'
    elif pitch_choice == '2':  # -25%
        return '-25Hz'
    elif pitch_choice == '3':  # Normal (0%)
        return '+0Hz'  # Ensure correct format
    elif pitch_choice == '4':  # +25%
        return '+25Hz'
    elif pitch_choice == '5':  # +50%
        return '+50Hz'
    return '+0Hz'  # Default to normal

# Function to convert the manually entered speaking rate to percentage
def convert_rate_to_percentage(rate_choice):
    try:
        rate = int(rate_choice)
        if -100 <= rate <= 100:  # Ensure the value is between -100 and 100
            return f"{'+' if rate >= 0 else ''}{rate}%"
    except ValueError:
        return '+0%'  # Default to normal if the input is invalid
    return '+0%'  # Default to normal

html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Text to Speech Converter</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; }
        .container { max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        h1 { text-align: center; }
        label { display: block; margin: 10px 0 5px; }
        select, input[type="number"], textarea { width: 100%; padding: 10px; margin-bottom: 10px; border-radius: 4px; border: 1px solid #ccc; }
        button { width: 100%; padding: 10px; background: #007BFF; border: none; border-radius: 4px; color: white; font-size: 16px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .result { margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Text to Speech Converter</h1>
        <form method="POST">
            <label for="voice">Select Voice:</label>
            <select name="voice" id="voice" required>
                {% for key, value in voices.items() %}
                    <option value="{{ key }}">{{ value }}</option>
                {% endfor %}
            </select>

            <label for="rate">Speaking Rate (-100 to 100):</label>
            <input type="number" name="rate" id="rate" placeholder="Enter rate" required>

            <label for="pitch">Select Pitch:</label>
            <select name="pitch" id="pitch" required>
                <option value="1">-50%</option>
                <option value="2">-25%</option>
                <option value="3">Normal (0%)</option>
                <option value="4">+25%</option>
                <option value="5">+50%</option>
            </select>

            <label for="text">Enter Text:</label>
            <textarea name="text" id="text" rows="5" required></textarea>

            <button type="submit">Convert to Speech</button>
        </form>

        {% if result %}
        <div class="result">
            <h2>Result</h2>
            <p>{{ result }}</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)  # Expose the app to the local network
