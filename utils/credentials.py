from dotenv import load_dotenv
import os 
load_dotenv()

import getpass
import os

lang_api=os.getenv("LANGSMITH_TRACING")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALSS")
GITHUB_PERSONAL_ACCESS_TOKEN = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")

LANGSMITH_TRACING="true"
LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
LANGSMITH_API_KEY="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"
LANGSMITH_PROJECT="personalAssistant"




# print(f"Got googe cred",GOOGLE_APPLICATION_CREDENTIALS)
# print(f" got github access", GITHUB_PERSONAL_ACCESS_TOKEN)
# print(f"got openAI ", openai_api_key)
# print(f"got gemini ", gemini_api_key)
# print("got TAVILY_API_KEY",TAVILY_API_KEY)