import os
import threading
from openai import OpenAI
from utils.credentials import openai_api_key
from speech.audioModule import AudioManager


client = OpenAI(api_key=openai_api_key)
pause_event = threading.Event()
audiManager = AudioManager()

while True:
    try:
        transcription = audiManager.listenForCommand()    
        try:
            if not transcription:
                print("No transcription received. Continuing...")
                continue
            print("Sending to GPT...")
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": transcription
                    },
                ],
                stream=True,
            )
            buffer = ""
            print("GPT response:")
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    buffer += chunk.choices[0].delta.content
                    print(chunk.choices[0].delta.content, end='', flush=True)
            print("\n") 

            if buffer:
                print("Converting response to speech...")
                audiManager.speakResponse(buffer)
                
        except Exception as e:
            print(f"Error during processing: {e}")

                
        finally:
            audiManager.resumeListening()
            
        print("\nListening for next input...")

    except KeyboardInterrupt:
        print("\n🛑 Process interrupted by user. Exiting...")
        audiManager.cleanup()
        break
    except Exception as e:
        print(f"Unexpected error: {e}")

    finally:
        audiManager.cleanup()

