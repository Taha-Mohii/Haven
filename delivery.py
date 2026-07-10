import os 
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
from twilio.rest import Client
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch

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
    
def send_whatsapp(recipient_phone, patient_name, title):
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_phone = os.getenv("TWILIO_PHONE")

    client = Client(account_sid , auth_token)

    message = f"{patient_name} left something for you — words they wrote just for you.\n\n*{title}*\n\nCheck your email. It's waiting there. 💙"
    try:
        client.messages.create(
            body = message,
            from_= from_phone,
            to=f"whatsapp:{recipient_phone}"
        )
        print(f"Whatsapp sent to {recipient_phone}")
        return True
    except Exception as e:
        print(f"WhatsApp failed: {e}")
        return False
    

def generate_legacy_pdf(patient_name ,entries ,output_path="legacy_vault.pdf"):
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "title", parent = styles["Heading1"],
        fontSize=24 , textColor="#7a9e9f",
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        "subtitle", parent=styles["Normal"],
        fontSize=11, textColor="#999999",
        spaceAfter=20
    )

    entry_title_style = ParagraphStyle(
        "entry_title", parent=styles["Heading2"],
        fontSize=14, textColor="#3d3d3d",
        spaceBefore=20, spaceAfter=4
    )

    meta_style = ParagraphStyle(
        "meta", parent=styles["Normal"],
        fontSize=9, textColor="#aaaaaa",
        spaceAfter=10
    )

    body_style = ParagraphStyle(
        "body", parent=styles["Normal"],
        fontSize=11, textColor="#3d3d3d",
        leading=18, spaceAfter=20
    )
    doc = SimpleDocTemplate(output_path, pagesize=A4,rightMargin=inch, leftMargin=inch,topMargin=inch, bottomMargin=inch)

    story = []

    story.append(Paragraph("Haven — Legacy Vault", title_style))
    story.append(Paragraph(f"Words left behind by {patient_name}", subtitle_style))
    story.append(Spacer(1, 0.3 * inch))

    for entry in entries:
        entry_type      = entry[2]
        recipient_name  = entry[3]
        title           = entry[6]
        content         = entry[7]

        story.append(Paragraph(title, entry_title_style))
        story.append(Paragraph(f"{entry_type.capitalize()} — For {recipient_name}", meta_style))
        story.append(Paragraph(content.replace("\n", "<br/>"), body_style))
        story.append(Spacer(1, 0.2 * inch))
    doc.build(story)
    print(f"PDF generated at {output_path}")
    return output_path