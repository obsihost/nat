import requests
import smtplib
import time
import certifi
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Email configuration
SENDER_EMAIL = "njuuu30@gmail.com"
SENDER_PASSWORD = "ehrsqvshedezoeyy"
RECIPIENTS = ["yaseenashraf@protonmail.com", 
              "ahmedalifahmy837@gmail.com",
              "helalabdelrhman2@gmail.com",
              "ahmed.579.hamdy@gmail.com",
              "Amrhossam228@gmail.com",
              "abdullrhmanmohsen11@gmail.com",
              "mahmoud.soliman841@gmail.com",
              "rehabmohamed151220@gmail.com"]
URL = "https://sisg.helwan.edu.eg/External?fn=NewerResultsAnnounced&ScopeID=61baacb0-1bf2-11ee-977a-0050568b266a&AnnouncementType=1&Year=2024"

# Store last response
last_response = None

def fetch_data():
    """Fetch JSON data from the URL."""
    try:
        response = requests.get(URL, verify=False)
        return response.json()  # Convert response to JSON
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def generate_html(data):
    """Generate an HTML email with inline styles."""
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

    # Add rows dynamically
    for entry in data:
        date = entry["Date"]
        scope_name = entry["ScopeName"]
        html_content += f"""
        <tr style="background-color: rgba(255, 255, 255, 0.1);">
            <td style="padding: 15px; border-bottom: 1px solid rgba(255, 255, 255, 0.3); color:#ffffff;">{date}</td>
            <td style="padding: 15px; border-bottom: 1px solid rgba(255, 255, 255, 0.3); color:#ffffff;">{scope_name}</td>
        </tr>
        """

    # Close the HTML structure
    html_content += """
        </table>
    </body>
    </html>
    """
    return html_content


def send_email(html_content):
    """Send email with HTML content."""
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

# Main loop to check for updates
while True:
    print("🔍 Checking for updates...")
    new_response = fetch_data()

    if new_response:
        if last_response is None:  # Initialize last_response on the first run
            last_response = new_response
        elif json.dumps(new_response, sort_keys=True) != json.dumps(last_response, sort_keys=True):  
            print("🔔 Data changed! Sending email notification...")
            last_response = new_response  # Update stored response
            html = generate_html(new_response)
            send_email(html)
        else:
            print("✅ No changes detected.")
    else:
        print("⚠️ Error fetching data, skipping this check.")

    time.sleep(6)  # Wait for 6 seconds before checking again
