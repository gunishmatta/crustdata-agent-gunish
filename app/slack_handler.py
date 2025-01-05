import os
import threading
from slack_sdk import WebClient
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.signature import SignatureVerifier
from flask import Flask, request, jsonify
import logging
from urllib import parse
SLACK_TOKEN = os.getenv("SLACK_TOKEN")

slack_client = WebClient(token=SLACK_TOKEN)

ALLOWED_CHANNELS = ["C0878Q5GAMB"]
ALLOWED_USERS = ["", "user2"]

def handle_slack_message(event,response):
    """Handles incoming Slack messages."""
    try:
        channel_id = event["channel"]
        user_id = event["user"]
        text = event["text"]
        api_validator_response = response.get("api_validator", {})
        response_text = api_validator_response.get("message", {}).get("text", "Unable to process your request.")
        slack_client.chat_postMessage(channel=channel_id, text=response_text)

    except SlackApiError as e:
        print(f"Error processing Slack message: {e}")


# sample_event = {
#     "type": "message",
#     "channel": "C0878Q5GAMB",
#     "user": "U1234567890",
#     "text": "GIve me some sample questions to ask from this documentation. with 1 ans, max 5",
#     "ts": "1694027890.000003",
#     "team": "T0123456789",
# }

# handle_slack_message(sample_event)
