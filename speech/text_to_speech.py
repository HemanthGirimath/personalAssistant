from google.cloud import texttospeech
import os
from pydub import AudioSegment
from pydub.playback import play
import io
from utils.credentials import GOOGLE_APPLICATION_CREDENTIALS


google_cred = GOOGLE_APPLICATION_CREDENTIALS
if not google_cred or not os.path.exists(google_cred):
    raise FileNotFoundError(f"Credentials file not found: {google_cred}")

def get_client():
    """Initialize Text-to-Speech client with proper credentials"""
    try:
        # Try using default credentials first
        return texttospeech.TextToSpeechClient()
    except Exception as e:
        # If default credentials fail, try getting from environment variable
        credentials_path = google_cred
        if not credentials_path:
            raise Exception("GOOGLE_APPLICATION_CREDENTIALS environment variable not set")
        
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(f"Credentials file not found at: {credentials_path}")
        
        # credentials = service_account.Credentials.from_service_account_file(credentials_path)
        # return texttospeech.TextToSpeechClient(credentials=credentials)

# Initialize the client using the function
try:
    client = get_client()
except Exception as e:
    print(f"Error initializing Text-to-Speech client: {e}")
    raise

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
    # print("Text-to-Speech completed.")
    return True