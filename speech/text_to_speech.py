from google.cloud import texttospeech
from dotenv import load_dotenv
import os
from pydub import AudioSegment
from pydub.playback import play
import io

# Load environment variables
load_dotenv()
google_cred = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not google_cred or not os.path.exists(google_cred):
    raise FileNotFoundError(f"Credentials file not found: {google_cred}")

# Initialize the Google Text-to-Speech client
client = texttospeech.TextToSpeechClient()

def synthesize_and_stream_text_to_speech(text):
    """
    Converts the given text to speech and streams the audio directly.
    :param text: The text to be converted to speech.
    """
    # Set the text input to be synthesized
    input_text = texttospeech.SynthesisInput(text=text)
    # Build the voice request
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",  # Specify the language and region
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,  # Voice gender
    )
    # Select the type of audio file you want
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3  # Output format
    )

    # Perform the text-to-speech request
    response = client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )

    # Stream the audio directly using pydub
    audio_stream = io.BytesIO(response.audio_content)
    audio = AudioSegment.from_file(audio_stream, format="mp3")
    play(audio)
    print("Text-to-Speech completed.")
    return True