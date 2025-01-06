import os
import uuid

from dotenv import load_dotenv

from app.ai.data_loaders import NotionDataLoader, SlackDataLoader

load_dotenv()

NOTION_API_TOKEN = os.getenv("NOTION_API_TOKEN")
SLACK_TOKEN = os.getenv("SLACK_TOKEN")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")
LLAMA2_HOST = os.getenv("LLAMA2_HOST")
NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID")


def load_all_data():
    """Loads data from all sources."""
    notion_loader = NotionDataLoader(api_token=NOTION_API_TOKEN,
                                     page_ids=[NOTION_PAGE_ID])
    slack_loader = SlackDataLoader(token=SLACK_TOKEN, channel_id=SLACK_CHANNEL_ID)
    notion_data = notion_loader.load_data()
    slack_data = slack_loader.load_data()
    all_documents = []
    for doc in notion_data:
        doc.id = str(uuid.uuid4())
        all_documents.append(doc)
    for doc in slack_data:
        doc.id = str(uuid.uuid4())
        all_documents.append(doc)
    return all_documents