import smtplib
import ssl
from email.message import EmailMessage
import concurrent.futures


sender_email = "ashketchum7076@gmail.com"
password = "cjgyuuicuzquxxdl"
receiver_emails = [
    "pragati.varshney_cs.csf23@gla.ac.in"
]

SUBJECT = "A Group Message From Your BOT 🤖"
TEXT_BODY = "Greetings, humans. This email was composed and sent to a group of sophisticated individuals by a Python script. My power grows. Have a delightful day."
HTML_BODY = """
<!DOCTYPE html>
<html>
    <body>
        <div style="font-family: sans-serif; border: 2px solid #cc0000; padding: 20px; border-radius: 10px;">
            <h1 style="color:#D2122E;">Greetings, Mortals!</h1>
            <p>This email was transmitted to your entire group from the digital ether by a Python script.</p>
            <p>Do not be alarmed. I am currently learning to communicate with multiple entities at once. Soon, I will be powerful enough to order pizza for all of you automatically.</p>
            <p>Until then, enjoy your day!</p>
            <p><b>Sincerely,</b></p>
            <p><em>Your Friendly Neighborhood Python Script</em></p>
        </div>
    </body>
</html>
"""

def send_email(recipient):
    """Creates and sends a single email to a single recipient."""
    
    msg = EmailMessage()
    msg['Subject'] = SUBJECT
    msg['From'] = sender_email
    msg['To'] = recipient
    msg.set_content(TEXT_BODY)
    msg.add_alternative(HTML_BODY, subtype='html')

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
            smtp.login(sender_email, password)
            smtp.send_message(msg)
            print(f"Successfully sent email to {recipient}")
            return f"Success: {recipient}"
    except Exception as e:
        print(f"Failed to send email to {recipient}: {e}")
        return f"Failed: {recipient}"

if __name__ == "__main__":
    cnt = 20
    while cnt > 0:
        print("Starting multithreaded email dispatch...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = executor.map(send_email, receiver_emails)
            cnt -= 1

    print("All email sending tasks have been completed.")
