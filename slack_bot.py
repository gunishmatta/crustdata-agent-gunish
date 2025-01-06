import logging
import re

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from app import Config
from app.ai.pipeline import RagPipeSingleton

slack_app = App(token=Config.SLACK_TOKEN)
slack_client = WebClient(token=Config.SLACK_TOKEN)

ALLOWED_CHANNELS = ["C0878Q5GAMB"]

ERROR_INTERNAL_SERVER = "An internal error occurred."

@slack_app.event("app_mention")
def handle_mention(body, logger):
    try:
        event = body["event"]
        channel_id = event["channel"]
        user_id = event["user"]
        text = event["text"]

        cleaned_text = re.sub(r'<[^>]*>', '', text)
        logging.info(f"Incoming mention in channel {channel_id} from user {user_id}: {cleaned_text}")

        if channel_id not in ALLOWED_CHANNELS:
            logging.info(f"Channel {channel_id} is not allowed. Ignoring.")
            return

        response = RagPipeSingleton.get_instance().run({
            "embedder": {"text": cleaned_text},
            "prompt_builder": {"question": cleaned_text}
        })

        api_validator_response = response.get("api_validator", {})
        message = api_validator_response.get("message", {})
        response_text = message.get("text", "Unable to process your request.")
        logging.info(f"Agent response: {response_text}")

        slack_client.chat_postMessage(channel=channel_id, text=response_text)

    except SlackApiError as e:
        logging.error(f"Error posting message to Slack: {e.response['error']}")
    except Exception as e:
        logging.error(f"Unexpected error while processing Slack event: {e}")

