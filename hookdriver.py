from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os

# --- Load Environment Variables ---
load_dotenv()
DISCORD_EMAIL = os.getenv("DISCORD_EMAIL")
DISCORD_PASSWORD = os.getenv("DISCORD_PASSWORD")
CHANNEL_URL = os.getenv("DISCORD_CHANNEL_URL")

# --- Global Variables ---
# We will initialize these in a setup function before the app runs.
app = Flask(__name__)
driver = None
message_box = None

def setup_discord_session():
    """
    Initializes the Selenium WebDriver, logs into Discord, navigates to the
    specified channel, and finds the message box element.
    This function should be called ONCE before the Flask app starts.
    """
    global driver, message_box
    
    print("Starting Selenium setup...")
    options = webdriver.ChromeOptions()
    # Use the new headless mode for better compatibility
    options.add_argument("--headless=new") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)

    try:
        # --- 1. Login to Discord ---
        print("Navigating to Discord login...")
        driver.get("https://discord.com/login")
        
        # Wait for the email field to be present before trying to interact with it.
        wait = WebDriverWait(driver, 20) # Wait up to 20 seconds
        
        email_field = wait.until(EC.presence_of_element_located((By.NAME, "email")))
        email_field.send_keys(DISCORD_EMAIL)
        
        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys(DISCORD_PASSWORD)
        password_field.send_keys(Keys.ENTER)
        
        print("Login submitted. Waiting for dashboard...")

        # --- 2. Navigate to Channel ---
        # Wait for a known element on the dashboard to appear before navigating away.
        # This confirms the login was successful. The 'friends' tab is a good candidate.
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href='/channels/@me']")))
        
        print(f"Navigating to channel: {CHANNEL_URL}")
        driver.get(CHANNEL_URL)

        # --- 3. Cache the message box element ---
        # Wait for the message box to be ready.
        message_box_xpath = '//div[@role="textbox"]'
        message_box = wait.until(EC.presence_of_element_located((By.XPATH, message_box_xpath)))
        
        print("✅ Discord session is ready.")
        
    except Exception as e:
        print(f"❌ An error occurred during Selenium setup: {e}")
        # Quit the driver if setup fails
        if driver:
            driver.quit()
        # Exit the program since the app can't function without the driver
        exit()


@app.route('/message', methods=['POST'])
def send_message():
    """
    API endpoint to send a message to the pre-loaded Discord channel.
    """
    global message_box
    data = request.get_json()
    
    if not data or 'content' not in data:
        return jsonify({"error": "Missing 'content' field"}), 400

    content = data['content']

    try:
        # Send the message using the cached element
        message_box.send_keys(content)
        message_box.send_keys(Keys.ENTER)
        print(f"Sent message: {content}")
        return jsonify({"status": "Message sent"}), 200
    except Exception as e:
        # If the element is stale or another error occurs, you might want to re-initialize.
        # For now, we just report the error.
        print(f"❌ Failed to send message: {e}")
        return jsonify({"error": f"Failed to send message: {e}"}), 500

# --- Main execution block ---
if __name__ == '__main__':
    # Run the setup function BEFORE starting the Flask app.
    setup_discord_session()
    app.run(host='0.0.0.0', port=5005)