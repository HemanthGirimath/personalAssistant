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

app = FastAPI()
model = ModelSelector()
voice_interaction = VoiceInteractionBase(model.current_model)

@app.get("/try")
async def hello(request:Request):
    use_voice = True
    if use_voice:
        result = await voice_interaction.process_agent_voice_interaction()
        return(f"result : ${result}")

# @app.post("/execute")
# async def execute_function(request: Request):
#     "Execute a function based on the request data."
#     data = await request.json()
#     function_name = data.get("function_name")
#     parameters = data.get("parameters", {})

#     if function_name not in functionRegistry:
#         return {"error": f"Function {function_name} not found"}
#     try:
#         result = functionRegistry[function_name](**parameters)
#         return {"result": result}
#     except Exception as e:
#             return {"error": str(e)}
    
# #Endpoint that lists all functions with their specifications
# @app.get("/functions")
# async def listFunctions():
    specs = {}
    for name, func in functionRegistry.items():
        specs[name] = {
            "description": func.__doc__,
            "parameters": getattr(func, "pax    rameters", {})
        }
    return specs

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