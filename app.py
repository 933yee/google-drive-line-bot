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

app = Flask(__name__)


@app.route("/callback", methods=["POST"])
def webhook():
    # signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        events = json.loads(body)["events"]
    except:
        abort(400)
        # for debugging
    # with open("events.json", "w") as json_file:
    #     json.dump(events, json_file, indent=4)
    for event in events:
        if event["type"] == "message":
            message_id = event["message"]["id"]
            if event["message"]["type"] == "image":
                download(message_id, True)
            elif event["message"]["type"] == "video":
                download(message_id, False)

    return "OK"


def download(message_id, is_image):
    download_url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"
    headers = {"Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"}
    print(download_url)
    response = requests.get(download_url, headers=headers)
    if response.status_code == 200:
        data = response.content
        name = f"{message_id}.jpg" if is_image else f"{message_id}.mp4"
        new_access_token = refresh_access_token(refresh_token, client_id, client_secret)
        upload(data, name, new_access_token, is_image)
    else:
        print("Failed to download image")


def upload(data, name, access_token, is_image):
    try:
        header = {"authorization": f"Bearer {access_token}"}
        if is_image:
            folder = image_folder
            dataType = "image/jpeg"
        else:
            folder = video_folder
            dataType = "video/mp4"

        param = {"name": f"{name}", "parents": [folder]}

        files = {
            "data": ("metadata", json.dumps(param), "application/json;charset=UTF-8"),
            "file": (f"{name}", data, dataType),
        }

        response = requests.post(
            "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
            headers=header,
            files=files,
        )

        if response.status_code == 200:
            print("file uploaded successfully")
        else:
            print("fail to upload")
    except Exception as e:
        print("An error occurred:", e)


def refresh_access_token(refresh_token, client_id, client_secret):
    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
    }
    response = requests.post(token_url, data=payload)
    if response.status_code == 200:
        token_data = response.json()
        return token_data.get("access_token")
    else:
        return None


if __name__ == "__main__":
    app.run(port=5000)
