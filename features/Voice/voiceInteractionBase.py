from speech.audioModule import AudioManager

from features.agents.agentHandler import AgentHandler
import asyncio

class VoiceInteractionBase:
    def __init__(self, model_selector=None,prompt=None):
        """
        Initialize voice interaction with optional model selector
        """
        self.prompt = prompt
        self.audio_manager = AudioManager()
        self.model_selector = model_selector
        self.agent_selector = AgentHandler(model_selector,prompt)
 
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
                response = self.model_selector.process_query(
                    template=custom_prompt_template,
                    user_input=transcription
                )
            else:
                Response = self.model_selector.process_query(transcription)
                return Response
            # Convert response to speech
            if response:
                self.audio_manager.speakResponse(response)
                return response
            
        except Exception as e:
            print(f"Error during voice interaction: {e}")
            return None
            
        finally:
            self.audio_manager.resumeListening()

    async def process_agent_voice_interaction(self, conversation_id:str = None):
        try:
            # Get voice input and convert to text
            transcription = self.audio_manager.listenForCommand()
            
            if not transcription:
                print("No transcription received.")
                return None
            
            # Process with agent
            if transcription:
                response = await self.agent_selector.process_query(
                    text=transcription,
                    conversation_id=conversation_id
                )

                if response and isinstance(response, dict):
                    # Extract just the response text from the dictionary
                    response_text = response.get("response", "")
                    # Send only the text to TTS
                    # self.audio_manager.speakResponse(response_text)
                    asyncio.create_task(self.audio_manager.speakResponse(response_text))
                    return response  # Return full response object for API
            
            return None
        
        except Exception as e:
            print(f"Error during voice interaction: {e}")
            return None
            
        finally:
            self.audio_manager.resumeListening()

    def cleanup(self):
        """Cleanup voice interaction resources"""
        if self.audio_manager:
            self.audio_manager.cleanup()