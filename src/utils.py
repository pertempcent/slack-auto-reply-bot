import os
import csv
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config import SLACK_USER_TOKEN

client = WebClient(token=SLACK_USER_TOKEN)

TASK_CSV_FILE = "data/tasks.csv"
last_logged_task = {}

if not os.path.exists(TASK_CSV_FILE):
    with open(TASK_CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Sender", "Message", "Channel ID"])

def get_user_name(user_id):
    try:
        response = client.users_info(user=user_id)
        return response["user"]["real_name"]
    except SlackApiError:
        return user_id  

def log_task(sender_name, message_text, channel_id, message_time):
    if channel_id in last_logged_task and last_logged_task[channel_id] == message_time:
        return  

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(TASK_CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, sender_name, message_text, channel_id])
    
    last_logged_task[channel_id] = message_time
