from fastapi import FastAPI, Request
import uvicorn
import json
import signal
import sys
import threading
import time
from typing import Dict, Any
from models.baseModule import ModelSelector
from features.Voice.voiceInteractionBase import VoiceInteractionBase
from features.agents.tools.githubAccess import GitHubTools
import uuid
from utils.promptLoader import loadPrompt


app = FastAPI()

# Remove global instantiations
# model = ModelSelector()
# github = GitHubTools()

# Create holder for lazy initialization
_model = None
_github = None

def get_model():
    global _model
    if _model is None:
        _model = ModelSelector()
    return _model

def get_github():
    global _github
    if _github is None:
        _github = GitHubTools()
    return _github

@app.get("/agent")
async def hello(request: Request, conversation_id: str = None, mode:str="general"):
    model = get_model()
    if mode == "general":
        generalPromot = loadPrompt("githubMode.txt")
        voice_interaction = VoiceInteractionBase(model.set_model("gpt-3.5-turbo"))
    else:
        githubPrompt = loadPrompt("githubMode.txt")
        voice_interaction = VoiceInteractionBase(model.set_model("gemini-2.0-flash"))

    use_voice = True
    if use_voice:
        # Generate new conversation_id if not provided
        if not conversation_id or conversation_id.strip() == "":
            conversation_id = str(uuid.uuid4())
            
        result = await voice_interaction.process_agent_voice_interaction(
            conversation_id=conversation_id
        )
        print("Agent Response : ", result["response"], end='\n\n')
        
        # Return both result and conversation_id
        return {
            "conversation_id": conversation_id,
            "result": result
        }
    
@app.get("/repo")
async def getAllRepo(request:Request):
    github = get_github()  # Lazy load GitHub when needed
    ressult = github.get_repo()
    return ressult
    

    
@app.get("/history/{conversation_id}")
async def get_history(conversation_id: str):
    """Get chat history for a specific conversation"""
    try:
        history = agent.get_conversation_history(conversation_id)
        return {"history": history}
    except Exception as e:
        return {"error": str(e)}



def signal_handler(sig, frame):
    print("\nShutting down server gracefully...")
    sys.exit(0)

def run_server():
    uvicorn.run(app, host="0.0.0.0", port=8000)

def main():
    try:
        # Register signal handler for graceful shutdown
        signal.signal(signal.SIGINT, signal_handler)
        
        # Create server thread as daemon
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Server shutdown complete")

if __name__ == "__main__":
    main()