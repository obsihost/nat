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
    <html lang="en" dir="rtl" style="margin: 0; padding: 0;">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Results Announcement</title>
    </head>
    <body style="background-color: #121212; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #e0e0e0; text-align: center; margin: 0; padding: 8px;">
      <h1 style="margin-bottom: 10px; text-shadow: 0 0 5px #00ffff; font-size: 1.2rem; color: #00ffff;">🔔 رابعة حاسبات ظهرت</h1>
      
      <h2 style="margin: 10px 0; font-size: 1.1rem; color: #00ffff;">نتائج الأقسام</h2>
      <div style="width: 100%; margin-bottom: 15px;">
        <table style="width: 100%; border-collapse: collapse; background: #1e1e1e; font-size: 0.8rem;">
          <tr>
            <th style="padding: 6px 4px; border: 1px solid #333; text-align: right; background-color: #1e1e1e; color: #00ffff; font-weight: normal; border-bottom: 2px solid #333; width: 40%; font-size: 0.75rem;">القسم</th>
    """
    
    years = ['الفرقة الاولي', 'الفرقة الثانية', 'الفرقة الثالثة', 'الفرقة الرابعة']
    departments = {
        'الهندسة الصناعية': 'الهندسة الصناعية',
        'هندسة الإلكترونيات والاتصالات': 'هندسة الإلكترونيات والاتصالات',
        'هندسة القوى والآلات الكهربية': 'هندسة القوى والآلات الكهربية',
        'الهندسة الحيوية الطبية': 'الهندسة الحيوية الطبية',
        'هندسة الميكاترونيات': 'هندسة الميكاترونيات',
        'هندسة الإنتاج': 'هندسة الإنتاج',
        'هندسة الحاسبات و النظم': 'هندسة الحاسبات و النظم',
        'إعدادى': 'إعدادى'
    }

    # Add year headers
    for year in years:
        html_content += f'<th style="padding: 6px 4px; border: 1px solid #333; text-align: center; background-color: #1e1e1e; color: #00ffff; font-weight: normal; border-bottom: 2px solid #333; width: 15%; font-size: 0.75rem;">{year}</th>'
    html_content += "</tr>"

    def has_result(dept, year):
        for item in data:
            scope_name = item['ScopeName']
            if dept == 'إعدادى':
                if 'إعدادى' in scope_name:
                    return True
                continue
            if dept not in scope_name:
                continue
            year_match = ('إعدادى' in scope_name) if year == 'الفرقة الاولي' else year in scope_name
            if year_match:
                return True
        return False

    # Add rows for each department
    for dept_display, dept_value in departments.items():
        html_content += f'<tr><td style="padding: 6px 4px; border: 1px solid #333; text-align: right; font-size: 0.75rem;">{dept_display}</td>'
        for year in years:
            cell_style = 'padding: 6px 4px; border: 1px solid #333; text-align: center; font-size: 0.75rem;'
            if has_result(dept_value, year):
                cell_style += ' background-color: #FFA500;'
            checkmark = "✓" if has_result(dept_value, year) else ""
            html_content += f'<td style="{cell_style}">{checkmark}</td>'
        html_content += "</tr>"
    
    html_content += """
        </table>
      </div>
      
      <h2 style="margin: 10px 0; font-size: 1.1rem; color: #00ffff;">البيانات الأصلية</h2>
      <div style="width: 100%; margin-bottom: 15px;">
        <table style="width: 100%; border-collapse: collapse; background: #1e1e1e; font-size: 0.8rem;">
          <tr>
            <th style="padding: 6px 4px; border: 1px solid #333; text-align: center; background-color: #1e1e1e; color: #00ffff; font-weight: normal; border-bottom: 2px solid #333; width: 35%; font-size: 0.75rem;">التاريخ</th>
            <th style="padding: 6px 4px; border: 1px solid #333; text-align: center; background-color: #1e1e1e; color: #00ffff; font-weight: normal; border-bottom: 2px solid #333; width: 65%; font-size: 0.75rem;">النتيجة</th>
          </tr>
    """
    
    for entry in data:
        date = entry["Date"]
        scope_name = entry["ScopeName"]
        html_content += f"""
          <tr>
            <td style="padding: 6px 4px; border: 1px solid #333; text-align: center; font-size: 0.75rem;">{date}</td>
            <td style="padding: 6px 4px; border: 1px solid #333; text-align: right; font-size: 0.75rem;">{scope_name}</td>
          </tr>
        """
    
    html_content += """
        </table>
      </div>
    </body>
    </html>
    """
    return html_content

def send_email(html_content):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = ", ".join(RECIPIENTS)
        msg['Subject'] = "🔔 نتيجتنا ظهرت"
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
        # Specific check for الفرقة الرابعة هندسة الحاسبات و النظم
        target_result_exists = any(
            'الفرقة الرابعة' in item['ScopeName'] and 
            'الحاسبات' in item['ScopeName'] 
            for item in new_response
        )

        # Check for changes and the specific result condition
        if target_result_exists and json.dumps(new_response, sort_keys=True) != json.dumps(last_response, sort_keys=True):
            print("🔔 Desired result found! Sending email notification...")
            last_response = new_response
            html = generate_html(new_response)
            send_email(html)
        else:
            print("✅ No changes or desired result detected.")
    else:
        print("⚠️ Error fetching data, skipping this check.")

    time.sleep(6)