import threading
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from speech.text_to_speech import synthesize_and_stream_text_to_speech
from speech.speech_to_text import stream_audio_data_to_google, stop_stream
import asyncio

class AudioManager:
    
    def __init__(self):
        self.pause_event = threading.Event()

    def listenForCommand(self):
        # Start the audio processing loop
        try:
            for transcription in stream_audio_data_to_google(self.pause_event):
                if not transcription or transcription.strip() == "":
                    continue
                    
                print(f"\nUser said: {transcription}")
                print("Pausing audio recording...")
                self.pause_event.set()
                stop_stream()
                return transcription
        except KeyboardInterrupt:
            print("\n🛑 Process interrupted by user. Exiting...")
            self.pause_event.clear()
            stop_stream()
            raise
        
    async def speakResponse(self,responseText):
        try:
            if responseText:
                print("converting response to speech...")
                # synthesize_and_stream_text_to_speech(responseText)
                await asyncio.to_thread(synthesize_and_stream_text_to_speech, responseText)
                import time
                # time.sleep(1.5)
        except KeyboardInterrupt:
            print("\n🛑 Process interrupted by user. Exiting...")
            self.pause_event.clear()
            stop_stream()
            raise
    
    def resumeListening(self):
        print("Resuming audio recording...")
        self.pause_event.clear()

    def cleanup(self):
        print("Cleaning up audio resources...")
        self.pause_event.clear()
        stop_stream()