import os
from dotenv import load_dotenv

load_dotenv()

SLACK_USER_TOKEN = os.getenv("SLACK_USER_TOKEN")  
SLACK_APP_LEVEL_TOKEN = os.getenv("SLACK_APP_LEVEL_TOKEN")  

if not SLACK_USER_TOKEN or not SLACK_APP_LEVEL_TOKEN:
    raise ValueError("Missing required environment variables!")
