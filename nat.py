import os
import requests
import smtplib
import time
import json
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECIPIENTS = os.getenv("RECIPIENTS").split(",")
URL = os.getenv("URL")

last_response = None

def fetch_data():
    try:
        response = requests.get(URL, verify=False)
        return response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def generate_html(data):
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Results Announcement</title>
    </head>
    <body style="background-color:#0e0e0e; font-family:Arial, sans-serif; color:#fff; text-align:center; padding:20px;">
        <h1 style="font-size:24px; text-transform:uppercase; text-shadow:0px 0px 10px rgba(0, 255, 255, 0.8);">
            🔔 Results Announcements
        </h1>
        <table style="width: 80%; margin: auto; border-collapse: collapse; background: rgba(255, 255, 255, 0.1); border-radius: 10px; overflow: hidden;">
            <tr style="background-color: rgba(255, 255, 255, 0.2);">
                <th style="padding: 15px; border-bottom: 1px solid rgba(255, 255, 255, 0.3); color:#ffffff;">Date</th>
                <th style="padding: 15px; border-bottom: 1px solid rgba(255, 255, 255, 0.3); color:#ffffff;">Natega</th>
            </tr>
    """
    for entry in data:
        date = entry["Date"]
        scope_name = entry["ScopeName"]
        html_content += f"""
        <tr style="background-color: rgba(255, 255, 255, 0.1);">
            <td style="padding: 15px; border-bottom: 1px solid rgba(255, 255, 255, 0.3); color:#ffffff;">{date}</td>
            <td style="padding: 15px; border-bottom: 1px solid rgba(255, 255, 255, 0.3); color:#ffffff;">{scope_name}</td>
        </tr>
        """
    html_content += "</table></body></html>"
    return html_content

def send_email(html_content):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = ", ".join(RECIPIENTS)
        msg['Subject'] = "🔔 New Results Announcement"

        msg.attach(MIMEText(html_content, 'html'))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECIPIENTS, msg.as_string())
        
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Error sending email: {e}")

while True:
    print("🔍 Checking for updates...")
    new_response = fetch_data()

    if new_response:
        if last_response is None:
            last_response = new_response
        elif json.dumps(new_response, sort_keys=True) != json.dumps(last_response, sort_keys=True):  
            print("🔔 Data changed! Sending email notification...")
            last_response = new_response
            html = generate_html(new_response)
            send_email(html)
        else:
            print("✅ No changes detected.")
    else:
        print("⚠️ Error fetching data, skipping this check.")

    time.sleep(6)