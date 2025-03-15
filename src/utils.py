import os
import csv
import time
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config import SLACK_USER_TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = WebClient(token=SLACK_USER_TOKEN)

TASK_CSV_FILE = "data/tasks.csv"
last_logged_task = {}

if not os.path.exists(TASK_CSV_FILE):
    with open(TASK_CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Sender", "Message", "Channel ID"])
    logger.info(f"Created new CSV file at {TASK_CSV_FILE}")

def get_user_name(user_id):
    try:
        response = client.users_info(user=user_id)
        return response["user"]["real_name"]
    except SlackApiError as e:
        logger.error(f"Error fetching user name for user_id {user_id}: {e.response['error']}")
        return user_id  

def log_task(sender_name, message_text, channel_id, message_time):
    if channel_id in last_logged_task and last_logged_task[channel_id] == message_time:
        logger.info(f"Skipping duplicate task logging for {sender_name} in {channel_id}")
        return  

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(TASK_CSV_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, sender_name, message_text, channel_id])
        last_logged_task[channel_id] = message_time
        logger.info(f"Task logged: {message_text} from {sender_name} in {channel_id}")
    except Exception as e:
        logger.error(f"Error writing task log: {e}")
