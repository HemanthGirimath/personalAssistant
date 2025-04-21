from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from models.baseModule import ModelSelector
from features.agents.tools.liveSearch import webSearchTool
from langchain_core.messages import AIMessage



class AgentHandler:
    def __init__(self,model):
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
            final_response = ""
            for step in self.agent_executor.stream(
                {"messages": [HumanMessage(content=text)]},
                stream_mode="values",
            ):
                # Get only AI messages and their content
                if isinstance(step["messages"][-1], AIMessage) and step["messages"][-1].content:
                    final_response = step["messages"][-1].content
                    print(f"AI Response: {final_response}")
            
                # print(step["messages"][-1].pretty_print())
            
            # Return just the string content
            return str(final_response)
        except Exception as e:
            print(f"Error in process_query: {e}")
            return str(e)
    
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

