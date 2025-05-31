from dotenv import load_dotenv
import os
load_dotenv()


def get_api_key(env_name):
    API_KEY = os.getenv(env_name)
    return API_KEY
