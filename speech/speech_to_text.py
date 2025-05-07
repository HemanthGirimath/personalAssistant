import sounddevice as sd
import queue
from google.cloud import speech
import time
import os

# Audio Recording Parameters
RATE = 16000
CHANNELS = 1
BLOCKSIZE = 1600

audio_queue = queue.Queue()
stream = None

def audio_callback(indata, frames, time, status):
    """Callback function for the audio stream."""
    if status:
        print(f"Status: {status}", flush=True)
    audio_queue.put(indata.copy())  # Add audio data to the queue

def stream_audio_data_to_google(pause_event):
    """Stream audio data to Google Speech-to-Text API."""
    global stream
    
    stt_client = speech.SpeechClient()
    
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code="en-US",
    )
    
    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True,
        # Add a timeout setting
        single_utterance=False  # Allow for multiple utterances in a stream
    )
    
    print("Starting audio stream. Speak into the microphone...")
    
    def generator():
        """Generates audio chunks from the queue when not paused."""
        while True:
            # Check if paused
            if pause_event.is_set():
                time.sleep(0.1)
                continue
                
            try:
                chunk = audio_queue.get(block=True, timeout=0.5)
                if chunk is None:
                    break
                yield speech.StreamingRecognizeRequest(audio_content=chunk.tobytes())
            except queue.Empty:
                continue
    
    try:
        # Create and start the audio input stream
        stream = sd.InputStream(
            samplerate=RATE,
            channels=CHANNELS,
            blocksize=BLOCKSIZE,
            callback=audio_callback,
            dtype="int16",
        )
        stream.start()
        
        requests = generator()
        responses = stt_client.streaming_recognize(config=streaming_config, requests=requests)
        
        for response in responses:
            if pause_event.is_set():
                continue
                
            for result in response.results:
                if result.is_final:
                    yield result.alternatives[0].transcript
    # except KeyboardInterrupt:
    #     print("Stream interrupted by user.")
                    
    except Exception as e:
        print(f"Error in audio streaming: {e}")
    finally:
        if stream and stream.active:
            stream.stop()
            stream.close()
        # print("Audio stream session closed.")

def stop_stream():
    """Function to properly stop the stream."""
    global stream
    if stream and stream.active:
        stream.stop()
        stream.close()
        # print("Audio stream stopped and closed. \n")