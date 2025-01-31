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
RECIPIENTS = ["yaseenashraf@protonmail.com", "theyaseenashraf@gmail.com"]
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

def generate_html(data, first_run=False):
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
    """

    if first_run:
        html_content += """
        <p style="font-size:18px; color:#0ff;">✅ The server is now active and will notify you of new results.</p>
        """
    else:
        html_content += """
        <p style="font-size:18px; color:#0ff;">🚀 A new result has been published!</p>
        """

    html_content += """
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

    html_content += """
        </table>
    </body>
    </html>
    """
    return html_content

def send_email(html_content, subject):
    """Send email with HTML content."""
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = ", ".join(RECIPIENTS)
        msg['Subject'] = subject

        msg.attach(MIMEText(html_content, 'html'))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECIPIENTS, msg.as_string())
        
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Error sending email: {e}")

# Fetch initial data
print("🔍 Fetching initial data...")
initial_data = fetch_data()

if initial_data:
    last_response = initial_data  # Store first response
    print("📢 Sending initial activation email...")
    initial_html = generate_html(initial_data, first_run=True)
    send_email(initial_html, "🚀 Server Activated - Results Monitoring Started!")

# Main loop to check for updates
while True:
    print("🔍 Checking for updates...")
    new_response = fetch_data()

    if new_response and (last_response is not None):
        if (json.dumps(new_response) != json.dumps(last_response)):
            print("🔔 Data changed! Sending email notification...")
            last_response = new_response  # Update stored response
            html = generate_html(new_response)
            send_email(html, "🔔 New Results Announcement!")
    else:
        print("✅ No changes detected.")

    time.sleep(10)  # Wait for 10 seconds before checking again
