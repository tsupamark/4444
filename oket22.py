
import asyncio
import os
import re
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# Получаем данные из переменных окружения
api_id = int(os.getenv('24682981'))
api_hash = os.getenv('6e1838e609c9d9248e5f84092c3b1837')
bot_token = os.getenv('8098121171:AAGcumK5w_5PAn6Pk-LNafIWSiSstaJdZeA')
string_session = os.getenv('1ApWapzMBuwnN8RQtz19WW_rXksDanzyYyRMuyNKl1hoSinAAbmVZ2UH6FelvGJEFeye5Eemml5yRRsBx_cOqZoIafKEukA-Bl5lv3HgiU-u6WnHssuWsViFWheuGAkigh2aEFL1DddUFeYgi4R7zGPnYGza_4Sec_lIGec5PT8dhN49ODK3uhSDleeNo3uvC_57oKzMvLE3Qf8Nx6PLL6h2_-_0uaQ2QMdNJBQ8DCRXQDRHl_YqnuF5AcNYDemOhhfZ-hhIEA7ZD5nhN1KfTihVtvx7ugl4rhKKQrmihk697zsj1U1r6UuioDrQR0SkY0rnZKrI0miszCQcAEok_A4jlu4noGYE=')

# ⏱️ Задержки
delay_between_messages = 15
delay_between_cycles = 15

# 📄 Динамические данные
sending_enabled = False
recipients_list = []
message_refs = []

# ✉️ Разрешённые пользователи (ID)
allowed_users = [7756306224, 7151451389]  # Замени на свои ID

# Инициализация клиентов с StringSession
client = TelegramClient(StringSession(string_session), api_id, api_hash)
bot = TelegramClient(StringSession(string_session + "_bot"), api_id, api_hash).start(bot_token=bot_token)

async def send_to_group(name):
    global sending_enabled
    while True:
        if sending_enabled and recipients_list and message_refs:
            print(f"\n🔁 Рассылка: {name}")
            for source_chat, msg_id in message_refs:
                for chat in recipients_list:
                    try:
                        await client.forward_messages(entity=chat, from_peer=source_chat, id=msg_id)
                        print(f"[✅] {name} → {chat}")
                    except Exception as e:
                        print(f"[❌] {name} ошибка у {chat}: {e}")
                    await asyncio.sleep(delay_between_messages)
            print(f"⏸ {name}: Ожидание {delay_between_cycles} сек...")
        await asyncio.sleep(delay_between_cycles)

@bot.on(events.NewMessage(pattern='/start'))
async def bot_start(event):
    global sending_enabled
    if event.sender_id in allowed_users:
        sending_enabled = True
        await event.respond("[✅] Рассылка включена")
    else:
        await event.respond("[⛔] У вас нет доступа")

@bot.on(events.NewMessage(pattern='/stop'))
async def bot_stop(event):
    global sending_enabled
    if event.sender_id in allowed_users:
        sending_enabled = False
        await event.respond("[⏹] Рассылка остановлена")
    else:
        await event.respond("[⛔] У вас нет доступа")

@bot.on(events.NewMessage(pattern='/add (.+)'))
async def add_chat(event):
    global recipients_list
    if event.sender_id in allowed_users:
        chat_link = event.pattern_match.group(1).strip()
        recipients_list.append(chat_link)
        await event.respond(f"[➕] Чат добавлен: {chat_link}")
    else:
        await event.respond("[⛔] У вас нет доступа")

@bot.on(events.NewMessage(pattern='/list'))
async def list_chats(event):
    if event.sender_id in allowed_users:
        if recipients_list:
            chats = "\n".join(recipients_list)
            await event.respond(f"[📄] Список чатов:\n{chats}")
        else:
            await event.respond("[⚠️] Список пуст")
    else:
        await event.respond("[⛔] У вас нет доступа")

@bot.on(events.NewMessage(pattern=r'/msg (https://t.me/\S+/\d+)'))
async def add_message(event):
    global message_refs
    if event.sender_id in allowed_users:
        url = event.pattern_match.group(1)
        match = re.match(r'https://t.me/(.+)/(\d+)', url)
        if match:
            chat = match.group(1)
            msg_id = int(match.group(2))
            message_refs.append((chat, msg_id))
            await event.respond(f"[🔹] Сообщение добавлено: {url}")
        else:
            await event.respond("[❌] Не удалось обработать ссылку")
    else:
        await event.respond("[⛔] У вас нет доступа")

@bot.on(events.NewMessage(pattern='/msglist'))
async def list_messages(event):
    if event.sender_id in allowed_users:
        if message_refs:
            text = "\n".join([f"https://t.me/{chat}/{msg_id}" for chat, msg_id in message_refs])
            await event.respond(f"[📌] Список сообщений:\n{text}")
        else:
            await event.respond("[⚠️] Список сообщений пуст")

@bot.on(events.NewMessage(pattern='/msgclear'))
async def clear_messages(event):
    global message_refs
    if event.sender_id in allowed_users:
        message_refs.clear()
        await event.respond("[🧹] Список сообщений очищен")
    else:
        await event.respond("[⛔] У вас нет доступа")

async def main():
    await client.start()
    await bot.start()
    await send_to_group('Групповая_рассылка')

if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())
