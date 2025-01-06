import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    NOTION_API_TOKEN = os.getenv("NOTION_API_TOKEN")
    SLACK_TOKEN = os.getenv("SLACK_TOKEN")
    SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")
    LLAMA2_HOST = os.getenv("LLAMA2_HOST")
    NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID")
    QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")  # Default to localhost
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

