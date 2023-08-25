from flask import Flask, request, abort
from dotenv import load_dotenv
import os
import json
import requests

load_dotenv()
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")
IMAGE_SAVE_DIR = os.getenv("IMAGE_SAVE_DIR")
refresh_token = os.getenv("refresh_token")
client_id = os.getenv("client_id")
client_secret = os.getenv("client_secret")
image_folder = os.getenv("image_folder")
video_folder = os.getenv("video_folder")


def refresh_access_token(refresh_token, client_id, client_secret):
    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
    }
    print(payload)
    response = requests.post(token_url, data=payload)
    if response.status_code == 200:
        token_data = response.json()
        return token_data.get("access_token")
    else:
        return None


print(refresh_access_token(refresh_token, client_id, client_secret))
