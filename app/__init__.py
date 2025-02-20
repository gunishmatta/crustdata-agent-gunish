import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    NOTION_API_TOKEN = os.getenv("NOTION_API_TOKEN")
    SLACK_TOKEN = os.getenv("SLACK_TOKEN")
    SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
    SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")
    NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID")
    QDRANT_URL = os.getenv("QDRANT_URL")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Expose Config class for import
__all__ = ["Config"]
