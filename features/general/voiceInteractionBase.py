# import os
# import threading
# from openai import OpenAI
# from utils.credentials import openai_api_key
# from speech.audioModule import AudioManager


# client = OpenAI(api_key=openai_api_key)
# pause_event = threading.Event()
# audiManager = AudioManager()

# while True:
#     try:
#         transcription = audiManager.listenForCommand()    
#         try:
#             if not transcription:
#                 print("No transcription received. Continuing...")
#                 continue
#             print("Sending to GPT...")
#             response = client.chat.completions.create(
#                 model="gpt-3.5-turbo",
#                 messages=[
#                     {
#                         "role": "user",
#                         "content": transcription
#                     },
#                 ],
#                 stream=True,
#             )
#             buffer = ""
#             print("GPT response:")
#             for chunk in response:
#                 if chunk.choices[0].delta.content is not None:
#                     buffer += chunk.choices[0].delta.content
#                     print(chunk.choices[0].delta.content, end='', flush=True)
#             print("\n") 

#             if buffer:
#                 print("Converting response to speech...")
#                 audiManager.speakResponse(buffer)
                
#         except Exception as e:
#             print(f"Error during processing: {e}")

                
#         finally:
#             audiManager.resumeListening()
            
#         print("\nListening for next input...")

#     except KeyboardInterrupt:
#         print("\n🛑 Process interrupted by user. Exiting...")
#         audiManager.cleanup()
#         break
#     except Exception as e:
#         print(f"Unexpected error: {e}")

#     finally:
#         audiManager.cleanup()

from speech.audioModule import AudioManager
from langchain_core.output_parsers import StrOutputParser

class VoiceInteractionBase:
    def __init__(self, model_selector=None):
        """
        Initialize voice interaction with optional model selector
        """
        self.audio_manager = AudioManager()
        self.model_selector = model_selector
    
    async def process_voice_interaction(self, custom_prompt_template=None):
        """
        Process a complete voice interaction cycle:
        1. Listen for voice input
        2. Convert to text
        3. Process with model
        4. Convert response to speech
        """
        try:
            # Get voice input and convert to text
            transcription = self.audio_manager.listenForCommand()
            
            if not transcription:
                print("No transcription received.")
                return None
            
            # Process with model
            if custom_prompt_template:
                response = self.model_selector.structured_query(
                    template=custom_prompt_template,
                    user_input=transcription
                )
            else:
                response = self.model_selector.query(transcription)
            
            # Convert response to speech
            if response:
                self.audio_manager.speakResponse(response)
                
            return response
            
        except Exception as e:
            print(f"Error during voice interaction: {e}")
            return None
            
        finally:
            self.audio_manager.resumeListening()
    
    def cleanup(self):
        """Cleanup voice interaction resources"""
        if self.audio_manager:
            self.audio_manager.cleanup()