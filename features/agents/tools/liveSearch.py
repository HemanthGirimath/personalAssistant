from langchain_community.tools.tavily_search import TavilySearchResults
from utils.credentials import TAVILY_API_KEY

class webSearchTool:
    @staticmethod
    def get_search_tool():
        """Returns an initialized TavilySearchResult"""
        return TavilySearchResults(
            max_results=2,
            api_key=TAVILY_API_KEY
        )
