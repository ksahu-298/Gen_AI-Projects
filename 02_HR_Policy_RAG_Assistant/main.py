import os
from dotenv import load_dotenv


load_dotenv()


# Load environment variables from .env file
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
JINA_API_KEY = os.getenv("JINA_API_KEY")