from dotenv import load_dotenv
import os 
load_dotenv()

GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
GITHUB_PERSONAL_ACCESS_TOKEN = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
openai_api_key = os.getenv("OPENAI_API_KEY")

print(f"Got googe cred",GOOGLE_APPLICATION_CREDENTIALS)
