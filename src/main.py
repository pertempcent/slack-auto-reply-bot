from slack_bolt import App
from config import SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET
from bot import register_events

app = App(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)
app = register_events(app)

if __name__ == "__main__":
    app.start(port=3000)
