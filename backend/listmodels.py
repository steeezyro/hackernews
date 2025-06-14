import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()  # Load the .env file if needed
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

for model in genai.list_models():
    print(model.name)