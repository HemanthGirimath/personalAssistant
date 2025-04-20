from dotenv import load_dotenv
import os 
load_dotenv()

GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
GITHUB_PERSONAL_ACCESS_TOKEN = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
openai_api_key = os.getenv("OPENAI_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

print(f"Got googe cred",GOOGLE_APPLICATION_CREDENTIALS)
print(f" got github access", GITHUB_PERSONAL_ACCESS_TOKEN)
print(f"got openAI ", openai_api_key)
print(f"got gemini ", gemini_api_key)
