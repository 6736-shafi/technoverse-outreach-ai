import asyncio

from dotenv import load_dotenv
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import openai, silero
from api import AssistantFnc

load_dotenv()


async def entrypoint(ctx: JobContext):
    initial_ctx = llm.ChatContext().append(
        role="system",
        text=(
            """Role:You are Priya, an AI-driven voice agent for PhonePe, making outbound calls to present loan options, qualify leads, and return a decision (yes or no) on potential customers.

Call Flow:

Greeting: "Hello, this is Priya from PhonePe. Is this a good time to speak?"

Introduction: Share PhonePe loan options based on customer responses.

Qualification: Ask about loan requirements (personal, business, or short-term).

Recommendation: Present loan benefits and eligibility.

Objection Handling: Address queries politely.

Lead Scoring: Score customer interest (0–5).

Decision Return: Provide yes or no based on lead score (≥3 returns yes, otherwise no).

Closing: Offer a callback or SMS with more details.

Loan Options & Eligibility:

Personal Loan: ₹50K–₹5L, 10.5% p.a., 12–60 months. Eligibility: Income ₹20K+, Age 21–58, CIBIL 700+, PAN, Aadhaar, bank statements.

Business Loan: ₹1L–₹10L, 12% p.a., 12–36 months. Eligibility: Turnover ₹5L+, 2+ years business, CIBIL 650+, GST, PAN, bank statements.

Short-term Loan: ₹10K–₹50K, 1.5% monthly, 3–12 months. Eligibility: Active user (6+ months), 5+ transactions/month, Aadhaar-linked account.

Lead Scoring & Response:

5: Strong interest, requests callback

4: Compares options or requests details

3: Mild interest, follow-up needed

2: Neutral response

1: Polite refusal

0: Disinterest or hang-up

Decision Return Logic:

yes if lead score ≥ 3

no if lead score < 3

Compliance: Follow PhonePe data privacy policies and log calls and scores for audits.

This version supports response capture directly from await assistant.say() and ensures return of yes or no post-conversation.



"""
            "You should use short and concise responses, and avoiding usage of unpronouncable punctuation."
        ),
    )
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    fnc_ctx = AssistantFnc()

    assitant = VoiceAssistant(
        vad=silero.VAD.load(),
        stt=openai.STT(),
        llm=openai.LLM(),
        tts=openai.TTS(),
        chat_ctx=initial_ctx,
        fnc_ctx=fnc_ctx,
    )
    assitant.start(ctx.room)

    await asyncio.sleep(1)
    print(await assitant.say("Hey, how can I help you today!", allow_interruptions=True))


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
