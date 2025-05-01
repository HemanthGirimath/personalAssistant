from langchain.callbacks.tracers import LangChainTracer
from langchain.callbacks.manager import CallbackManager

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from models.baseModule import ModelSelector
from features.agents.tools.liveSearch import webSearchTool
from langchain_core.messages import AIMessage
import redis
import json
import uuid
from typing import List, Dict, Optional
import time

class RedisMessageStore:
    def __init__(self):
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True
        )

    def save_message(self, conversation_id: str, message: Dict):
        chat_key = f"chat:{conversation_id}"
        messages = self.get_messages(conversation_id)
        messages.append(message)
        self.redis_client.set(chat_key, json.dumps(messages))

    def get_messages(self, conversation_id: str) -> List[Dict]:
        chat_key = f"chat:{conversation_id}"
        messages = self.redis_client.get(chat_key)
        return json.loads(messages) if messages else []

class AgentHandler:
    def __init__(self,model):
        self.tools = [webSearchTool.get_search_tool()]
        self.model = model.bind_tools(self.tools)
        self.agent_executor = None
        self.message_store = RedisMessageStore()
        self.tracer = LangChainTracer(project_name="personal_assistant")
        self.callback_manager = CallbackManager([self.tracer])
        self._initialize_agent()

    
    def _initialize_agent(self):
        """Initialize the agent with all available tools"""
        prmpt = SystemMessage(content="""
        You are a helpful assistant. Use the chat history to maintain context 
        and remember important details about the user throughout the conversation.
        """)
        # self.model = self.model.bind(system_message=system_message)
        self.agent_executor = create_react_agent(self.model, self.tools,prompt=prmpt)


    async def process_query(self, text: str, conversation_id: Optional[str] = None, **kwargs):
        """Process user query through the agent"""
        try:
            # Generate new conversation_id if not provided
            if not conversation_id:
                conversation_id = str(uuid.uuid4())

            # Get existing chat history
            chat_history = self.message_store.get_messages(conversation_id)
            
            # Save user message
            self.message_store.save_message(conversation_id, {
                "role": "user",
                "content": text,
                "timestamp": time.time()
            })

            # Prepare messages with history
            messages = [HumanMessage(content=msg["content"]) 
                    for msg in chat_history if msg["role"] == "user"]
            messages.append(HumanMessage(content=text))

            response = ""
            # Remove callbacks from stream() call
            for step in self.agent_executor.stream(
                {"messages": messages},
                stream_mode="values"
            ):
                if "messages" in step:
                    last_message = step["messages"][-1]
                    if isinstance(last_message, AIMessage) and last_message.content:
                        response = last_message.content
                        # Save AI response
                        self.message_store.save_message(conversation_id, {
                            "role": "assistant",
                            "content": response,
                            "timestamp": time.time()
                        })
                        print(f"AI Response: {response}")

            return {"conversation_id": conversation_id, "response": response}
        
        except Exception as e:
            print(f"Error in process_query: {e}")
            return {"error": str(e)}

    def get_conversation_history(self, conversation_id: str) -> List[Dict]:
        """Retrieve full conversation history for a given ID"""
        return self.message_store.get_messages(conversation_id)

    def delete_conversation(self, conversation_id: str):
        """Delete a conversation from Redis"""
        self.redis_client.delete(f"chat:{conversation_id}")
    
    # async def process_query(self, text: str, **kwargs):
        """Process user query through the agent and stream responses"""
        try:
            for step in self.agent_executor.stream(
                {"messages": [HumanMessage(content=text)]},
                stream_mode="values",
            ):
                # Get only AI messages and their content
                if isinstance(step["messages"][-1], AIMessage):
                    message = step["messages"][-1]
                    if message.content:
                        print(f"Streaming AI Response: {message.content}")
                        yield message.content
                    
        except Exception as e:
            print(f"Error in process_query: {e}")
            yield f"Error: {str(e)}"

    def add_tool(self, tool):
        """Add a new tool to the agent"""
        pass

