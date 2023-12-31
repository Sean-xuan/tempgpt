from flask import Flask, request, jsonify, render_template
import os
import numpy as np
import openai
import requests
import io
from pydub import AudioSegment
from pydub.playback import play
import json


#AudioSegment.converter = "/app/vendor/ffmpeg/ffmpeg"
#AudioSegment.ffprobe = "/app/vendor/ffmpeg/ffprobe"



openai.api_key = os.environ.get("OPENAI_API_KEY")

# Initialize Flask app
app = Flask(__name__, static_folder="../frontend/static", static_url_path="/")


# Global buffer for storing audio data
buffer = np.array([])


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe_and_respond', methods=['POST'])
def transcribe_and_respond():
    # Receive audio data from frontend
    audio_file = request.files['audio']
    
    # Save audio data to a file
    audio_filename = "received_audio.wav"
    audio_file.save(audio_filename)
    print("Received audio file size:", os.path.getsize(audio_filename), "bytes")

    # Convert audio to text
    with open(audio_filename, "rb") as file:
        transcription = openai.Audio.translate("whisper-1", file)["text"]

    print(transcription)
    # Get a response from GPT
    response_text = get_response_from_gpt(transcription)
    print(response_text)

    # Convert text response to audio and save it
    #response_audio_filename = os.path.join(app.static_folder, "response_audio.mp3")
    response_audio_filename = os.path.abspath(os.path.join(app.static_folder, "response_audio.mp3"))
    audio_url = 'https://aiheartbeat-7515af4eaeeb.herokuapp.com/static/response_audio.mp3'



    EL_TTS(response_text,response_audio_filename)


    response_data = {
        'transcription': transcription,
        'response': response_text,
        'audio_url': audio_url # This URL can be used by the frontend to play the audio
    }
    print(response_data)
    return jsonify(response_data)


@app.errorhandler(500)
def internal_error(error):
    response = {
        'status': 'error',
        'message': 'Internal server error'
    }
    return jsonify(response), 500


def get_response_from_gpt(prompt):
    OAI={
          "model": "gpt-3.5-turbo",
          "prompt": "This is how a toxic entitled evil female streamer responded in a conversation. She would respond in a toxic and rude manner. She would talk about the message and would elaborate on it as well as share some of her experiences if possible. She would also go on a tangent if possible.",
          "temperature": 0.9,
            "max_tokens": 30,
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
    
    # Check if the response was successful
    if response.status_code != 200:
        print("Erroßr from ElevenLabs TTS:", response.text)
        return None
    print("Length of audio content from TTS API:", len(response.content))

    audio_content = AudioSegment.from_file(io.BytesIO(response.content), format="mp3")
    # Save the audio content to a specified file
    #play(audio_content)

    with open(response_audio_filename, 'wb') as f:
        f.write(audio_content.raw_data)

    return audio_content.duration_seconds

if __name__ == '__main__':
    #app.run(port=5002)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

