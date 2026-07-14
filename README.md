# Haven 💙
### *A safe place for everything unsaid.*

---

## What Is Haven?

Haven is an AI-powered emotional companion for patients in their final days. It gives them:

- Someone to talk to, any time of day
- A place to track how they're feeling
- A vault to store letters, memories, and wishes for the people they love
- A way to make sure those words reach the right people at the right moment

Haven doesn't give medical advice. It doesn't offer false hope. It just listens — and remembers.

---

## Features

### 🤝 AI Companion
A warm, empathetic chat companion powered by **Groq's LLaMA 3.3 70B**. Haven knows the patient's name, age, and condition. It remembers every conversation and references past discussions naturally — like a trusted friend who has been paying attention. It speaks slowly, warmly, and gently. When the patient is scared, it stays. When they want to laugh, it laughs with them.

### 🌿 Mood Tracker
Patients log how they're feeling on a 1–10 slider with an optional note. Haven quietly monitors these entries. If a score is critically low or the note contains concerning language, Haven responds with a gentle message of support. All mood history is stored privately and displayed chronologically.

### ✉️ Legacy Vault
The heart of Haven. Patients write letters, memories, and wishes for their loved ones — a note for a spouse, a message for a child's wedding day, a memory they want preserved. Each entry includes:
- Recipient name, email, and WhatsApp number
- A scheduled delivery date — or "send after I'm gone"
- A unique private access link for family members

### 📬 Automated Delivery System
Letters are delivered automatically at the right moment:
- **On a specific date** — a birthday, an anniversary, a graduation
- **After 14 days of inactivity** — Haven assumes the patient can no longer visit and delivers all remaining letters
- **Via email** — a warm, beautifully formatted HTML email (SendGrid)
- **Via WhatsApp** — a gentle nudge to check their inbox (Twilio)
- **As a PDF** — all letters compiled into a single vault document (ReportLab)

### 🔗 Family Access Page
Every letter generates a unique, unguessable UUID link. Family members can open this link directly from their email — no Haven account needed. They see the letter exactly as it was written, in a clean and respectful interface.

### 📊 Dashboard Stats
The home dashboard shows:
- Total letters written
- Total messages shared with Haven
- Last recorded mood score
- Days since last visit

Small numbers that tell a big story.

### ⚙️ Account Management
- Update name, age, and condition
- Change password securely
- Forgot password via WhatsApp OTP (6-digit code, 10-minute expiry)
- Delete account and all associated data permanently

### 🔒 Activity Monitor
A background scheduler (APScheduler) runs every 24 hours:
- **7 days inactive** → sends the patient a gentle reminder
- **14 days inactive** → triggers delivery of all legacy letters
- **Scheduled date** → delivers letters on the exact date set by the patient

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3 |
| Web Framework | Flask |
| Database | Supabase (PostgreSQL) |
| AI | Groq — LLaMA 3.3 70B |
| Email Delivery | SendGrid |
| WhatsApp | Twilio |
| Background Jobs | APScheduler |
| Password Security | bcrypt |
| PDF Generation | ReportLab |
| UI Design | Neumorphism CSS |
| Version Control | Git / GitHub |

---

## Project Structure
Haven/
│
├── app.py               → All Flask routes and application logic
├── database.py          → Every database function
├── ai.py                → AI companion — Groq integration and personality
├── delivery.py          → Email, WhatsApp, and PDF delivery
├── scheduler.py         → Daily background activity monitor
├── security.py          → bcrypt password hashing
│
├── static/
│   └── style.css        → Neumorphism UI — warm, calm, and gentle
│
├── templates/
│   ├── landing.html     → Public landing page
│   ├── register.html    → Patient registration
│   ├── login.html       → Login
│   ├── home.html        → Dashboard with stats
│   ├── companion.html   → AI chat interface
│   ├── mood.html        → Mood tracker and history
│   ├── legacy.html      → Legacy vault home
│   ├── write.html       → Write a new letter/memory/wish
│   ├── view.html        → View a single entry
│   ├── edit.html        → Edit an existing entry
│   ├── family.html      → Family access page (no login required)
│   ├── settings.html    → Account settings
│   ├── forgot_password.html  → Forgot password
│   ├── verify_otp.html       → OTP verification
│   ├── reset_password.html   → Reset password
│   └── 404.html         → Not found page
│
├── .env                 → Secret keys (never committed)
├── .gitignore
└── requirements.txt

---

## Database Schema

```sql
haven_patients   → Patient accounts, credentials, phone, OTP
conversations    → Full AI chat history per patient
moods            → Mood logs with score, note, timestamp
legacy           → Letters, memories, wishes with delivery details
activity_log     → Last seen timestamp and delivery status
```

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/Taha-Mohii/haven.git
cd haven
```

### 2. Create virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file in the root:
DATABASE_URL=your_supabase_connection_string
GROQ_API_KEY=your_groq_api_key
SENDGRID_API_KEY=your_sendgrid_api_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE=whatsapp:+14155238886
SECRET_KEY=your_flask_secret_key
BASE_URL=http://127.0.0.1:5000

### 5. Set up Supabase
Run the SQL schema in your Supabase SQL editor to create all tables. Schema is available in the repository.

### 6. Run Haven
```bash
python app.py
```

Visit `http://127.0.0.1:5000`

---

## Known Limitations

- Twilio WhatsApp uses a sandbox — recipients must opt in every 72 hours
- Currently runs locally only — deployment ready for Railway or Render

---

## What's Next

- Voice note support in the legacy vault
- Photo attachments alongside letters
- Sentiment analysis alerts to family members for critical mood entries
- Railway deployment with a live demo
- A demo mode for judges and reviewers to experience Haven without registering

---

## About This Project

Haven was built by **Taha Mohii**, a Computer Science student at **College of Engineering Trivandrum** (graduating 2028).

This wasn't just a college project. It came from watching my father go through a serious illness, and from meeting other patients like him in hospital waiting rooms — people who had so much left to say and no quiet place to say it. I wanted to build something that could hold space for those moments. Something warm. Something private. Something that would carry their words forward, even after they were gone.

If this project helps even one person feel a little less alone in those final days, it will have been worth building.

---

*Built with care, and dedicated to everyone who needed a Haven.*

💙
