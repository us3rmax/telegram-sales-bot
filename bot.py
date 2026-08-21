import asyncio
import os
import re
from zoneinfo import ZoneInfo

import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telethon import TelegramClient, events
from telethon.sessions import StringSession


API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
MY_BOT_TOKEN = os.environ["MY_BOT_TOKEN"]
SOURCE_BOT = os.getenv("SOURCE_BOT", "@tpdofm_bot")
SESSION_STRING = os.environ["SESSION_STRING"]

BOT_NAMES = {
    "@kaayyla_bot": "Kay 🌸",
}

STARS_TO_USD = {
    80: 1, 99: 1, 100: 1, 125: 2, 150: 2, 200: 3, 249: 3, 250: 3,
    280: 4, 400: 5, 490: 6, 499: 6, 500: 7, 699: 9, 750: 10,
    980: 13, 1000: 13, 1200: 16,
}

daily_profit = 0.0
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)


def convert_message(text: str):
    global daily_profit

    if "Purchase" in text or "sold" in text.lower():
        match = re.search(r"(\d+)\s+Stars", text, re.IGNORECASE)
        if match:
            stars = int(match.group(1))
            usd = STARS_TO_USD.get(stars, round(stars / 75))
            daily_profit += usd
            return f"💸 New PPV sale • ${usd}"

    if "New fan" in text:
        bot_match = re.search(r"(@[\w_]+bot)", text, re.IGNORECASE)
        if bot_match:
            bot_user = bot_match.group(1).lower()
            friendly_name = BOT_NAMES.get(bot_user, bot_user)
            return f"{friendly_name} have a New fan ✨"

    return None


def send_via_my_bot(chat_id: int, text: str):
    url = f"https://api.telegram.org/bot{MY_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    response = requests.post(url, json=payload, timeout=20)
    response.raise_for_status()


async def send_daily_report():
    global daily_profit
    me = await client.get_me()
    report = f"💸 Gross profit today: $ {daily_profit}"
    send_via_my_bot(me.id, report)
    print(f"📊 Relatório diário enviado: {report}")
    daily_profit = 0.0


@client.on(events.NewMessage(chats=SOURCE_BOT))
async def handler(event):
    if event.message.message:
        new_text = convert_message(event.message.message)
        if new_text:
            me = await client.get_me()
            send_via_my_bot(me.id, new_text)
            print(f"✅ Notificação: {new_text} | Total hoje: ${daily_profit}")


async def main():
    await client.start()
    print("🚀 SISTEMA ATIVO - Monitorando vendas, fãs e lucro diário!")

    scheduler = AsyncIOScheduler(timezone=ZoneInfo("America/Sao_Paulo"))
    scheduler.add_job(send_daily_report, "cron", hour=23, minute=59)
    scheduler.start()

    await client.run_until_disconnected()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Desligado.")
