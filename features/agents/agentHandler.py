from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
# from models.baseModule import ModelSelector
from features.agents.tools.liveSearch import webSearchTool
from langchain_core.messages import AIMessage
from langchain.callbacks.tracers import LangChainTracer
from langchain.callbacks.manager import CallbackManager
import os

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "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"
os.environ["LANGCHAIN_PROJECT"] = "personalAssistant"

class AgentHandler:
    def __init__(self,model):
        self.tracer = LangChainTracer(project_name ="personalAssistant")
        self.tools = [webSearchTool.get_search_tool()]
        self.model = model.bind_tools(self.tools)
        self.agent_executor = None
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the agent with all available tools"""
        self.agent_executor = create_react_agent(self.model, self.tools)

    async def process_query(self, text: str, **kwargs):
        """Process user query through the agent"""
        try:
            response = ""
            for step in self.agent_executor.stream(
                {"messages": [HumanMessage(content=text)]},
                stream_mode="values",
                config={"callbacks": [self.tracer]}, 
            ):
                # Check if step contains messages
                if "messages" in step:
                    # Get the last message from the list
                    last_message = step["messages"][-1]
                    if isinstance(last_message, AIMessage) and last_message.content:
                        response = last_message.content
                        print(f"AI Response: {response}")

            return response
        except Exception as e:
            print(f"Error in process_query: {e}")
            return f"Error processing query: {str(e)}"
    
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


