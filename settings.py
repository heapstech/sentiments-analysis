from dotenv import load_dotenv
from pathlib import Path
import os

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

CONSUMER_KEY = os.getenv("consumer_key")
CONSUMER_SECRET = os.getenv("consumer_secret")
ACCESS_TOKEN_KEY = os.getenv("access_token_key")
ACCESS_TOKEN_SECRET = os.getenv("access_token_secret")
