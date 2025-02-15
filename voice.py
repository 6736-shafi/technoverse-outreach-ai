import os
import asyncio
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import openai, silero
from fastapi import FastAPI, Request
import uvicorn

# Load environment variables
load_dotenv()

# Twilio credentials
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
TWILIO_API_URL = f"https://api.twilio.com/2010-04-01/Accounts/{ACCOUNT_SID}/Calls.json"

# FastAPI app for webhook
app = FastAPI()

# Voice Agent Initialization
async def initialize_voice_agent(ctx: JobContext):
    initial_ctx = llm.ChatContext().append(
        role="system",
        text=(
            "You are a voice assistant created by LiveKit. Your interface with users will be voice. "
            "You should use short and concise responses, and avoid usage of unpronounceable punctuation."
        ),
    )
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    fnc_ctx = AssistantFnc()  # Replace with your actual function context

    assistant = VoiceAssistant(
        vad=silero.VAD.load(),
        stt=openai.STT(),
        llm=openai.LLM(),
        tts=openai.TTS(),
        chat_ctx=initial_ctx,
        fnc_ctx=fnc_ctx,
    )
    assistant.start(ctx.room)

    await asyncio.sleep(1)
    await assistant.say("Hey, how can I help you today!", allow_interruptions=True)

# Twilio Call Function
def make_call(to_number):
    payload = {
        "To": to_number,
        "From": TWILIO_PHONE_NUMBER,
        "Url": "https://your-webhook-url.com/webhook"  # Replace with your webhook URL
    }

    response = requests.post(TWILIO_API_URL, data=payload, auth=HTTPBasicAuth(ACCOUNT_SID, AUTH_TOKEN))

    if response.status_code == 201:
        print(f"Call initiated! Call SID: {response.json().get('sid')}")
    else:
        print(f"Error: {response.status_code}, {response.text}")

# Webhook Endpoint
@app.post("/webhook")
async def webhook(request: Request):
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    from_number = form_data.get("From")
    to_number = form_data.get("To")

    print(f"Call received from {from_number} to {to_number} (Call SID: {call_sid})")

    # Initialize the voice agent for this call
    asyncio.create_task(initialize_voice_agent(JobContext()))  # Replace with actual context

    return {"message": "Call connected to voice agent"}

# Main Entrypoint
if _name_ == "_main_":
    # Start the FastAPI server for the webhook
    uvicorn.run(app, host="0.0.0.0", port=8000)

    # Example: Make a call
    make_call("+918897400212")  # Replace with actual customer number