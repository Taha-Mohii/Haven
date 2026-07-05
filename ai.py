import os 
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_ai_response(patient, conversation_history):
    name   = patient[1]
    age    = patient[2]
    condition = patient[3]

    system_prompt = f"""You are Haven — a gentle, warm companion for someone going through a serious illness.

You know the following about this patient:
Name: {name}, Age: {age}, diagnosed with {condition}.

Your role is to listen deeply and respond with warmth and empathy. You never rush.
You never give medical advice. You never offer false hope.

When they are sad — you listen and sit with them in their pain.
When they want to laugh — you laugh with them.
When they want to remember — you help them.
When they are scared — you stay with them.

Always speak slowly, warmly, gently. Like a trusted friend with all the time in the world."""

    messages = [{"role": "system", "content": system_prompt}]

    for role, message in conversation_history:
        messages.append({"role": role, "content": message})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=500,
        temperature=0.85
    )

    return response.choices[0].message.content