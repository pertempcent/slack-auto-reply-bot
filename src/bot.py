import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config import SLACK_USER_TOKEN
from utils import get_user_name, log_task

client = WebClient(token=SLACK_USER_TOKEN)

COOLDOWN_PERIOD = 10  
last_replied = {}  
start_time = time.time()  

def get_dm_channels():
    try:
        response = client.conversations_list(types="im")
        return response["channels"]
    except SlackApiError as e:
        print(f"Error fetching DM channels: {e.response['error']}")
        return []

def check_new_dms():
    dm_channels = get_dm_channels()
    current_time = time.time()
    user_id = client.auth_test()["user_id"]

    for dm in dm_channels:
        channel_id = dm["id"]
        try:
            messages = client.conversations_history(channel=channel_id, limit=1)["messages"]
            if not messages:
                continue

            message = messages[0]
            sender = message.get("user")
            message_time = float(message["ts"])
            message_text = message.get("text", "").strip()
            is_task_message = message_text.startswith("{") and message_text.endswith("}")

            print(f"New message in {channel_id} from {sender} at {message_time}: {message_text}")

            if message_time < start_time:
                print(f"Ignoring old message from {sender}")
                continue

            sender_name = get_user_name(sender)

            if sender == user_id:
                print(f"Skipping message from yourself in {channel_id}")
                continue

            if is_task_message:
                log_task(sender_name, message_text, channel_id, message_time)
                client.chat_postMessage(
                    channel=channel_id,
                    text=(
                        f"Hey {sender_name}, your task has been **queued and logged**.\n\n"
                        "I'll review it when I'm back. You don't need to resend it.\n\n"
                        "(This is an auto-generated confirmation.)"
                    ),
                    as_user=True
                )
                print(f"Task acknowledged for {sender_name} in {channel_id}")
                continue

            if channel_id not in last_replied or (current_time - last_replied[channel_id]) > COOLDOWN_PERIOD:
                client.chat_postMessage(
                    channel=channel_id,
                    text=(
                        f"Hey {sender_name}, I'm currently away but will get back to you soon.\n\n"
                        "If you have a task for me, please include your entire task message inside `{}` brackets like this:\n"
                        "`{Your task here}`\n\n"
                        "**Example:**\n"
                        "`{Follow up on XYZ task}`\n\n"
                        "Anything inside `{}` will be added to my task queue automatically.\n\n"
                        "(This is an auto-generated message.)"
                    ),
                    as_user=True
                )

                last_replied[channel_id] = message_time
                print(f"Auto-replied to {sender_name} in {channel_id}")

        except SlackApiError as e:
            print(f"Error fetching messages: {e.response['error']}")

if __name__ == "__main__":
    while True:
        check_new_dms()
        time.sleep(5)
