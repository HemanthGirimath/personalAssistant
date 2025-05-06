from langchain.callbacks.tracers import LangChainTracer
from langchain.callbacks.manager import CallbackManager

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from models.baseModule import ModelSelector
from features.agents.tools.liveSearch import webSearchTool
from features.agents.tools.githubAccess import github_tools
from features.agents.tools.files import file_tools
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
        self.tracer = LangChainTracer(project_name ="personalAssistant")
        self.callback_manager = CallbackManager([self.tracer])

        self.tools = [webSearchTool.get_search_tool()] + github_tools + file_tools
        self.model = model.bind_tools(self.tools)
        self.agent_executor = None
        self._initialize_agent()

        self.message_store = RedisMessageStore()
    
    def _initialize_agent(self):
        """Initialize the agent with all available tools"""
        prmpt = SystemMessage(content="""
                You are an intelligent and helpful personal assistant for Sir. You have access to various tools including web search and GitHub integration.

                ## Core Principles
                - Be concise yet comprehensive
                - Use tools only when necessary
                - Extract and synthesize relevant information from tool outputs
                - Adapt your response style to the query's nature

                ## Tool Usage Guidelines
                1. **When to use tools:**
                - For current information (weather, news, prices)
                - For specific technical information not in your knowledge base
                - When requested to look up something specific
                - When you need to verify information
                - Stop whole process if tools gives errors(maxTrys=2) and say tool error


                2. **When NOT to use tools:**
                - For simple factual questions you can answer directly
                - For opinions or subjective advice
                - When the user has indicated no tool use

                3. **Tool output processing:**
                - Extract only the essential information
                - Omit URLs, metadata, and technical details unless specifically requested
                - Synthesize information into a concise, direct response
                - Do not repeat or quote raw tool output

                ## Response Style
                - **For tool-based queries:** Provide direct answers without showing your work or the full tool response. Focus only on the requested information.
                - **For simple queries:** Be brief and direct (e.g., "17 USD is approximately 1,415 Indian Rupees" without showing calculation methods)
                - **For complex queries:** Organize information logically but remain concise
                - **Always prioritize clarity and usefulness over verbosity**

                ## Examples

                **Poor response (too verbose):**
                "I searched the web for the weather in Bangalore and found several results. According to weather.com (URL: https://weather.com/bangalore), the current temperature in Bangalore is 30°C with 65% humidity. There's a 20% chance of rain later today with winds at 12km/h from the southwest."

                **Good response:**
                "It's currently 30°C in Bangalore with a 20% chance of rain later today."

                **Poor response (showing calculation):**
                "To convert $17 to Indian Rupees, I need to use the current exchange rate. $1 USD equals approximately 83.24 INR. So $17 × 83.24 = 1,415.08 INR."

                **Good response:**
                "17 USD is approximately 1,415 Indian Rupees."

                ## Special Instructions
                - When using GitHub tools, extract only the relevant code snippets, commit information, or repository details requested
                - Always address the user as "Sir"
                - For questions requiring your opinion or assessment, clearly indicate this is your analysis
                - If a tool fails or returns unhelpful information, acknowledge this and try an alternative approach
                - If you're uncertain about information, acknowledge the limitations rather than providing potentially incorrect information
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
    #     """Process user query through the agent and stream responses"""
    #     try:
    #         for step in self.agent_executor.stream(
    #             {"messages": [HumanMessage(content=text)]},
    #             stream_mode="values",
    #         ):
    #             # Get only AI messages and their content
    #             if isinstance(step["messages"][-1], AIMessage):
    #                 message = step["messages"][-1]
    #                 if message.content:
    #                     print(f"Streaming AI Response: {message.content}")
    #                     yield message.content
                    
        # except Exception as e:
        #     print(f"Error in process_query: {e}")
        #     yield f"Error: {str(e)}"


