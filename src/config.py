import os
from dotenv import load_dotenv

load_dotenv()

SLACK_USER_TOKEN = os.getenv("SLACK_USER_TOKEN")  

if not SLACK_USER_TOKEN:
    raise ValueError("Missing environment variable: SLACK_USER_TOKEN")
