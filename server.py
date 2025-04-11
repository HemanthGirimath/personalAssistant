from fastapi import FastAPI, Request
import uvicorn
import json
from typing import Dict, Any
from features.github.githubAccess import get_repo, get_content_of_repo, create_newRepo

app = FastAPI()

functionRegistry = {
    "get_repo": get_repo,
    "get_content_of_repo": get_content_of_repo,
    "create_newRepo": create_newRepo
}


@app.post("/execute")
async def execute_function(request: Request):
    "Execute a function based on the request data."
    data = await request.json()
    function_name = data.get("function_name")
    parameters = data.get("parameters", {})

    if function_name not in functionRegistry:
        return {"error": f"Function {function_name} not found"}
    try:
        result = functionRegistry[function_name](**parameters)
        return {"result": result}
    except Exception as e:
            return {"error": str(e)}
    
#Endpoint that lists all functions with their specifications
@app.get("/functions")
async def listFunctions():
    specs = {}
    for name, func in functionRegistry.items():
        specs[name] = {
            "description": func.__doc__,
            "parameters": getattr(func, "pax    rameters", {})
        }
    return specs

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)