import asyncio
import os
import random
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

SCHEDULED_MESSAGES = {
    "morning": [
        "Bom dia! Já fez {valor}. Nada mal pra começar. 💰",
        "08h e você já colocou {valor} no placar. 🔥",
        "{valor} antes mesmo do café terminar. Começamos bem. ☕",
        "Seu dia começou com {valor}. Agora é descobrir onde isso vai parar. 👀",
        "{valor} já são seus. E o dia mal começou. 😎",
        "O relógio marcou 08h. Seu faturamento marcou {valor}. Gostei mais do segundo.",
        "Você acordou e já encontrou {valor} no painel. Bom dia mesmo. 😂",
        "{valor} logo cedo? Seu eu de ontem ficaria orgulhoso. 🫡",
        "08h: {valor} faturados. Se continuar assim, hoje promete. 🚀",
        "Primeira missão do dia: olhar para esses {valor} e fazer esse número crescer.",
    ],
    "noon": [
        "Pode almoçar tranquilo: já são {valor} no bolso hoje. 🍽️💰",
        "Meio-dia e {valor} faturados. O almoço foi pago. 😎",
        "Seu almoço tem gosto de {valor}. Aproveita. 😂",
        "Até meio-dia: {valor}. Agora imagina onde esse número pode chegar. 👀",
        "{valor} até agora. Se o resto do dia acompanhar, vai ficar bonito. 💸",
    ],
    "evening": [
        "18h e você já fez {valor} hoje. Respeita esse número. 🫡",
        "{valor} faturados. O expediente acabou, mas esse número ficou bonito.",
        "Olha esses {valor}. Foi isso que seu trabalho colocou no placar hoje. 💰",
        "18h: {valor}. Nada mal para mais um dia de vendas. 🔥",
        "{valor} hoje. Seu eu de amanhã vai querer repetir esse número.",
        "O relógio marcou 18h. O painel marcou {valor}. Eu sei qual número importa mais. 😂",
        "{valor} faturados até agora. Pode fechar o notebook com orgulho. 🫡",
        "18h. {valor} no placar. Se esse número pudesse falar, provavelmente pediria mais. 😂",
    ],
    "closing": [
        "23:59. Hoje você fez {valor}. Pode dormir tranquilo. 😴💰",
        "Dia encerrado: {valor} faturados. Amanhã tem mais. 🚀",
        "{valor}. Esse é o número que resume seu dia de hoje. 🫡",
        "Hoje começou em $0 e terminou em {valor}. É disso que estamos falando. 🔥",
        "{valor} faturados hoje. Agora sim você pode desligar tudo.",
        "Mais um dia transformado em {valor}. Nada mal. Nada mal mesmo. 😎",
    ],
}

STARS_TO_USD = {
    80: 1, 99: 1, 100: 1, 125: 2, 150: 2, 200: 3, 249: 3, 250: 3,
    280: 4, 400: 5, 490: 6, 499: 6, 500: 7, 699: 9, 750: 10,
    980: 13, 1000: 13, 1200: 16,
}

daily_profit = 0.0
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)


def format_amount(value: float) -> str:
    return f"${value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


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


async def send_scheduled_message(message_group: str):
    me = await client.get_me()
    amount = format_amount(daily_profit)
    message = random.choice(SCHEDULED_MESSAGES[message_group]).format(valor=amount)
    send_via_my_bot(me.id, message)
    print(f"🕒 Mensagem programada ({message_group}): {message}")


async def send_daily_report():
    global daily_profit
    await send_scheduled_message("closing")
    daily_profit = 0.0


async def send_test_closing():
    me = await client.get_me()
    test_amount = format_amount(1342.45)
    message = random.choice(SCHEDULED_MESSAGES["closing"]).format(valor=test_amount)
    send_via_my_bot(me.id, message)
    print(f"🧪 Teste temporário das 23:47 enviado: {message}")


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
    scheduler.add_job(lambda: send_scheduled_message("morning"), "cron", hour=8, minute=0)
    scheduler.add_job(lambda: send_scheduled_message("noon"), "cron", hour=12, minute=0)
    scheduler.add_job(lambda: send_scheduled_message("evening"), "cron", hour=18, minute=0)
    # TESTE TEMPORÁRIO ÀS 23:47: remover depois de validar a mensagem das 23:59.
    scheduler.add_job(send_test_closing, "cron", hour=23, minute=47)
    scheduler.add_job(send_daily_report, "cron", hour=23, minute=59)
    scheduler.start()

    await client.run_until_disconnected()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Desligado.")
