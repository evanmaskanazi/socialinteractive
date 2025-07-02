import smtplib
import json
import os

# Load config
with open('therapy_data/email_config.json', 'r') as f:
    config = json.load(f)

print(f"Testing email: {config['sender_email']}")
print(f"Password length: {len(config['sender_password'])}")

try:
    # Test connection
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.set_debuglevel(1)  # Show debug info
    server.starttls()
    server.login(config['sender_email'], config['sender_password'])
    print("SUCCESS! Login worked!")
    server.quit()
except Exception as e:
    print(f"ERROR: {e}")