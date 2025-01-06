import re
import uuid
from abc import ABC, abstractmethod
from typing import List

from haystack import Document
from notion_haystack.notion_exporter import NotionExporter
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class DataLoader(ABC):
    """Abstract base class for loading data from different sources."""

    @abstractmethod
    def load_data(self) -> List[Document]:
        """Loads data from the specified source."""
        pass


class NotionDataLoader(DataLoader):
    """Loads data from Notion."""

    def __init__(self, api_token, page_ids):
        self.exporter = NotionExporter(api_token=api_token)
        self.page_ids = page_ids

    def load_data(self) -> List[Document]:
        exported_pages = self.exporter.run(page_ids=self.page_ids)

        print("Exported Pages:", exported_pages)

        documents = []

        # Iterate over each page
        for page in exported_pages.get('documents', []):
            self.process_text(page.content, documents)

        return documents

    def process_text(self, text, documents):
        """Splits the page content into individual documents based on newlines, headers (#), or fixed length."""
        max_length = 300
        if len(text) > max_length:
            chunks = [text[i:i + max_length] for i in range(0, len(text), max_length)]
            for chunk in chunks:
                document = Document(
                    id=str(uuid.uuid4()),
                    content=chunk.strip(),
                    meta={'type': 'chunk'}
                )
                documents.append(document)

        print(f"Created {len(documents)} documents from the text.")


class SlackDataLoader(DataLoader):
    """Loads data from Slack."""

    def __init__(self, token, channel_id):
        self.token = token
        self.channel_id = channel_id
        self.client = WebClient(token=self.token)

    def load_data(self) -> List[Document]:
        """Loads conversations from a Slack channel and creates Document objects."""
        conversations = []
        try:
            result = self.client.conversations_history(channel=self.channel_id)
            messages = result['messages']
            while result['has_more']:
                result = self.client.conversations_history(
                    channel=self.channel_id,
                    oldest=messages[-1]['ts']
                )
                messages.extend(result['messages'])

            for i in range(len(messages) - 1):
                if messages[i]['type'] == 'message' and messages[i+1]['type'] == 'message':
                    question = messages[i]['text']
                    answer = messages[i+1]['text']
                    conversation = f"**Question:** {question}\n**Answer:** {answer}"
                    conversations.append(Document(content=conversation, meta={'source': 'slack'}))

        except SlackApiError as e:
            print(f"Error fetching conversations from Slack: {e}")
            return []

        return conversations
