import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config import SLACK_USER_TOKEN

client = WebClient(token=SLACK_USER_TOKEN)

COOLDOWN_PERIOD = 10  
last_replied = {}  
start_time = time.time()  

def get_user_name(user_id):
    """Convert Slack user ID to a readable username."""
    try:
        response = client.users_info(user=user_id)
        return response["user"]["real_name"]
    except SlackApiError:
        return user_id  

def get_dm_channels():
    """Fetch all direct message conversations."""
    try:
        response = client.conversations_list(types="im")
        return response["channels"]
    except SlackApiError as e:
        print(f"Error fetching DM channels: {e.response['error']}")
        return []

def check_new_dms():
    """Check for new DMs and reply only if sent after the bot started."""
    dm_channels = get_dm_channels()
    current_time = time.time()

    for dm in dm_channels:
        channel_id = dm["id"]
        try:
            messages = client.conversations_history(channel=channel_id, limit=1)["messages"]
            if not messages:
                continue

            message = messages[0]
            sender = message.get("user")
            message_time = float(message["ts"])
            message_text = message.get("text", "")

            print(f"DEBUG: New message in {channel_id} from {sender} at {message_time}: {message_text}")

            if message_time < start_time:
                print(f"DEBUG: Ignoring old message from {sender}")
                continue

            sender_name = get_user_name(sender)

            if sender == client.auth_test()["user_id"]:
                print(f"DEBUG: Skipping message from yourself in {channel_id}")
                continue

            if channel_id not in last_replied or (current_time - last_replied[channel_id]) > COOLDOWN_PERIOD:
                client.chat_postMessage(
                    channel=channel_id,
                    text=f"Hey {sender_name}, I'm currently away but will get back to you soon.",
                    as_user=True
                )
                last_replied[channel_id] = message_time
                print(f"✅ Auto-replied to {sender_name} in {channel_id}")

        except SlackApiError as e:
            if e.response["error"] == "restricted_action_read_only_channel":
                print(f"⚠️ Skipping restricted DM: {channel_id}")
            else:
                print(f"Error fetching messages: {e.response['error']}")

if __name__ == "__main__":
    while True:
        check_new_dms()
        time.sleep(5)  
