
import uuid

from app import Config
from app.ai.data_loaders import NotionDataLoader, SlackDataLoader


def load_all_data():
    """Loads data from all sources."""
    notion_loader = NotionDataLoader(api_token=Config.NOTION_API_TOKEN,
                                     page_ids=[Config.NOTION_PAGE_ID])
    slack_loader = SlackDataLoader(token=Config.SLACK_TOKEN, channel_id=Config.SLACK_CHANNEL_ID)
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