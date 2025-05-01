from fastapi import FastAPI, Request
import uvicorn
import json
from typing import Dict, Any
from models.baseModule import ModelSelector
from features.Voice.voiceInteractionBase import VoiceInteractionBase
import uuid

import uuid

app = FastAPI()
model = ModelSelector()
voice_interaction = VoiceInteractionBase(model.current_model)

@app.get("/try")
async def hello(request: Request, conversation_id: str = None):
    use_voice = True
    if use_voice:
        # Generate new conversation_id if not provided
        if not conversation_id or conversation_id.strip() == "":
            conversation_id = str(uuid.uuid4())
            
        result = await voice_interaction.process_agent_voice_interaction(
            conversation_id=conversation_id
        )
        print("server object : ", result)
        
        # Return both result and conversation_id
        return {
            "conversation_id": conversation_id,
            "result": result
        }

@app.get("/history/{conversation_id}")
async def get_history(conversation_id: str):
    """Get chat history for a specific conversation"""
    try:
        history = voice_interaction.agent_handler.get_conversation_history(conversation_id)
        return {"history": history}
    except Exception as e:
        return {"error": str(e)}

# @app.get("/try")
# async def hello(request: Request):
#     use_voice = True
#     if use_voice:
#         response_stream = []
#         async for chunk in voice_interaction.process_agent_voice_interaction():
#             response_stream.append(chunk)
#             # If using WebSocket, you can send each chunk to the client here
            
#         return {"stream": response_stream , "conversation_id": res }

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
    # specs = {}
    # for name, func in functionRegistry.items():
    #     specs[name] = {
    #         "description": func.__doc__,
    #         "parameters": getattr(func, "pax    rameters", {})
    #     }
    # return specs

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)