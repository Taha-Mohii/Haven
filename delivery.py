import os 
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = "rathertaha786@gmail.com" 

def send_email(recipient_name, recipient_email, patient_name,title , content):
    html_content = f"""
    <div style="font-family: Georgia, serif; max-width: 600px; margin: auto; color: #3d3d3d;">
        <h2 style="color: #7a9e9f;">A letter for you, from {patient_name}</h2>
        <hr style="border: none; border-top: 1px solid #eee;">
        <p>Dear {recipient_name},</p>
        <p>{patient_name} wrote this for you. They wanted you to have these words.</p>
        <hr style="border: none; border-top: 1px solid #eee;">
        <div style="background: #fdf6f0; padding: 1.5rem; border-radius: 8px; line-height: 1.8; white-space: pre-wrap;">
            {content}
        </div>
        <hr style="border: none; border-top: 1px solid #eee;">
        <p style="color: #aaa; font-size: 0.85rem;">Written with love. Delivered by Haven.</p>
    </div>
    """

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=recipient_email,
        subject=f"A letter to you from {patient_name}",
        html_content=html_content
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
        print(f"Email sent to {recipient_email}")
        return True
    except Exception as e:
        print(f"Email failed: {e}")
        return False