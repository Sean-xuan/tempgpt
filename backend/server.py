from flask import Flask, request, jsonify, render_template
import os
import whisper
import numpy as np
import openai
import requests
import io
from pydub import AudioSegment
from pydub.playback import play
import json
from flask import send_file

# Initialize Flask app
app = Flask(__name__, static_folder="../frontend/static", static_url_path="")


# Global buffer for storing audio data
buffer = np.array([])

# Load the Whisper model for speech to text
whisper_model = whisper.load_model("base")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe_and_respond', methods=['POST'])
def transcribe_and_respond():
    # Receive audio data from frontend
    transcription = "how are you?"
    
    # Save audio data to a file
    #audio_filename = "received_audio.wav"
    #audio_file.save(audio_filename)
    #print("Received audio file size:", os.path.getsize(audio_filename), "bytes")

    # Convert audio to text
    #transcription = transcribe_with_whisper(audio_filename)

    # Get a response from GPT
    response_text = get_response_from_gpt(transcription)
    print(response_text)

    # Convert text response to audio and save it
    response_audio_filename = os.path.join(app.static_folder, "response_audio.mp3")

    EL_TTS(response_text,response_audio_filename)

    response_data = {
        'transcription': transcription,
        'response': response_text,
        'audio_url': '/static/response_audio.mp3',

        #'audio_url': '/'+response_audio_filename  # This URL can be used by the frontend to play the audio
    }
    return jsonify(response_data)

@app.route('/audio_response')
def audio_response():
    response_audio_filename = os.path.join(app.static_folder, "response_audio.mp3")
    return send_file(response_audio_filename, mimetype='audio/mpeg')


def transcribe_with_whisper(audio_file):
    # Load the audio
    audio = whisper.load_audio(audio_file)

    # Trim or pad the audio to fit
    audio = whisper.pad_or_trim(audio)

    # Convert audio to log-Mel spectrogram
    mel = whisper.log_mel_spectrogram(audio).to(whisper_model.device)

    # Decode the audio
    options = whisper.DecodingOptions(fp16=False)
    result = whisper.decode(whisper_model, mel, options)

    return result.text

@app.errorhandler(500)
def internal_error(error):
    response = {
        'status': 'error',
        'message': 'Internal server error'
    }
    return jsonify(response), 500
# You can uncomment the line below to run the server
# app.run(port=5000, debug=True)


def get_api_key_from_config():
    # Load the OpenAI API Key from config.json
    #with open("config.json", "r") as json_file:
        #data = json.load(json_file)
    key=""
    return key

def get_response_from_gpt(prompt):
    #api_key = get_api_key_from_config()
    openai.api_key = api_key
    OAI={
          "model": "gpt-3.5-turbo",
          "prompt": "This is how a toxic entitled evil female streamer responded in a conversation. She would respond in a toxic and rude manner. She would talk about the message and would elaborate on it as well as share some of her experiences if possible. She would also go on a tangent if possible.",
          "temperature": 0.9,
            "max_tokens": 20,
            "top_p": 1,
            "frequency_penalty": 1,
            "presence_penalty": 1
        }
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
            {"role": "system", "content": OAI["prompt"]},
            {"role": "user", "content": prompt},
        ],
      temperature=OAI["temperature"],
      max_tokens=OAI["max_tokens"],
      top_p=OAI["top_p"],
      frequency_penalty=OAI["frequency_penalty"],
      presence_penalty=OAI["presence_penalty"]
    )

    json_object = json.loads(str(response))
    return(json_object['choices'][0]['message']['content'])

def EL_TTS(message,response_audio_filename):
    url = f'https://api.elevenlabs.io/v1/text-to-speech/{"MF3mGyEYCl7XYWbV9V6O"}'
    headers = {
        'accept': 'audio/mpeg',
        'xi-api-key': '6d0ed246659b5953e0535f011b8d8ff5',
        'Content-Type': 'application/json'
    }
    data = {
        'text': message,
        'voice_settings': {
            'stability': 0.75,
            'similarity_boost': 0.75
        }
    }

    response = requests.post(url, headers=headers, json=data, stream=True)

    print("========================================")
    print("ElevenLabs TTS API Response:")
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {response.headers}")
    print("========================================")

    
    # Check if the response was successful
    if response.status_code != 200:
        print("Erroßr from ElevenLabs TTS:", response.text)
        return None
    print("Length of audio content from TTS API:", len(response.content))

    audio_content = AudioSegment.from_file(io.BytesIO(response.content), format="mp3")
    # Save the audio content to a specified file
    # play(audio_content)
    print("Audio file saved at:", response_audio_filename)

    with open(response_audio_filename, 'wb') as f:
        f.write(audio_content.raw_data)

    return audio_content.duration_seconds

if __name__ == '__main__':
    app.run(port=5002)
