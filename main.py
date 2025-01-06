import multiprocessing
from slack_bolt.adapter.socket_mode import SocketModeHandler

from app import Config


def start_flask():
    from flask_app import app
    app.run(host='0.0.0.0', port=8002)

def start_slack_bot():
    from slack_bot import slack_app
    SocketModeHandler(slack_app, Config.SLACK_APP_TOKEN).start()

if __name__ == "__main__":
    flask_process = multiprocessing.Process(target=start_flask)
    slack_bot_process = multiprocessing.Process(target=start_slack_bot)
    flask_process.start()
    slack_bot_process.start()
    flask_process.join()
    slack_bot_process.join()
