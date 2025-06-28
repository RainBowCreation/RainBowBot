from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
import os
import time
import threading


app = Flask(__name__)

load_dotenv()
DISCORD_EMAIL = os.getenv("DISCORD_EMAIL")
DISCORD_PASSWORD = os.getenv("DISCORD_PASSWORD")
CHANNEL_URL = os.getenv("DISCORD_CHANNEL_URL")

driver = None
message_box = None

def setup_discord_session():
    global driver, message_box
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")  # remove --headless for debug
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)

    # Login to Discord
    driver.get("https://discord.com/login")
    time.sleep(5)
    driver.find_element(By.NAME, "email").send_keys(DISCORD_EMAIL)
    driver.find_element(By.NAME, "password").send_keys(DISCORD_PASSWORD)
    driver.find_element(By.NAME, "password").send_keys(Keys.ENTER)

    time.sleep(10)  # Wait for dashboard load

    # Open the channel
    driver.get(CHANNEL_URL)
    time.sleep(10)

    # Cache the message box element
    message_box = driver.find_element(By.XPATH, '//div[@role="textbox"]')
    print("Discord session is ready.")

# Call this once at startup
appHasRunBefore:bool = False
@app.before_request
def init_driver():
    global appHasRunBefore
    if not appHasRunBefore:
        threading.Thread(target=setup_discord_session).start()
        appHasRunBefore = True

@app.route('/message', methods=['POST'])
def send_message():
    global message_box
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({"error": "Missing 'content' field"}), 400

    content = data['content']

    try:
        message_box.send_keys(content)
        message_box.send_keys(Keys.ENTER)
        return jsonify({"status": "Message sent"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to send message: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5005)