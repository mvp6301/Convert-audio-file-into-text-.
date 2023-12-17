from flask import Flask, render_template, request
import os
import speech_recognition as sr
from pydub import AudioSegment
from pydub.utils import mediainfo  # Add this line to import mediainfo
from googletrans import Translator


app = Flask(__name__)
AudioSegment.converter = "ffmpeg"
mediainfo.FFPROBE_PATH = "ffprobe"
LANGUAGE_MAPPING = {
    'telugu': 'te',
    'english': 'en',
    'assamese': 'as',
    'bengali': 'bn',
    'bodo': 'brx',
    'dogri': 'doi',
    'gujarati': 'gu',
    'hindi': 'hi',
    'kannada': 'kn',
    'kashmiri': 'ks',
    'konkani': 'kok',
    'maithili': 'mai',
    'malayalam': 'ml',
    'manipuri': 'mni',
    'marathi': 'mr',
    'nepali': 'ne',
    'odia':'or-IN',
    'punjabi': 'pa',
    'sanskrit': 'sa',
    'santali': 'sat',
    'sindhi': 'sd',
    'tamil': 'ta',
    'telugu': 'te',
    'urdu': 'ur',
}

def convert_audio_to_text(audio_file):
    recognizer = sr.Recognizer()

    try:
        # Load the audio file using pydub and convert to WAV
        audio = AudioSegment.from_file(audio_file)
        audio = audio.set_frame_rate(16000)  # Set the frame rate to 16 kHz (required for Google Speech Recognition)
        audio.export("temp.wav", format="wav")

        # Load the converted WAV file
        with sr.AudioFile("temp.wav") as source:
            audio_data = recognizer.record(source)

        # Use Google Web Speech API to convert audio to text
        text = recognizer.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand the audio.")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return None

def translate_text(text, target_language='en'):
    translator = Translator()

    # Handle empty text
    if not text:
        print("Error: Empty text provided for translation.")
        return ""

    try:
        translation = translator.translate(text, dest=target_language)
        translated_text = translation.text
        print(translated_text)
        return translated_text
    except Exception as e:
        print(f"Error during translation: {e}")
        return ""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        target_language = request.form.get('target_language')
        # Check if the 'audio_file' key is in the request.files dictionary
        if 'audio_file' not in request.files:
            return render_template('audio.html', extracted_text=None)

        audio_file = request.files['audio_file']

        # Check if the file is selected and has an allowed extension
        if audio_file.filename == '' or not allowed_file(audio_file.filename):
            return render_template('audio.html', extracted_text=None)

        # Process the audio file and get the extracted text
        extracted_text = convert_audio_to_text(audio_file)
        translated_text = translate_text(extracted_text, target_language)

        return render_template('audio.html', language_mapping=LANGUAGE_MAPPING, extracted_text=extracted_text, translated_text=translated_text)

    return render_template('audio.html', language_mapping=LANGUAGE_MAPPING, extracted_text=None, translated_text="")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'wav', 'mp3'}

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080)


