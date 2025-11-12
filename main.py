import os
import shutil
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

BOT_TOKEN = "YOUR_BOT_TOKEN"  # ჩასვი შენი ბოტის ტოკენი
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

BASE_DIR = "delivery_files"
DELIVERED_DIR = "delivered_files"

# მხოლოდ ეს 4 რაიონი იქნება გათვალისწინებული
DISTRICTS = ["გლდანი", "ვარკეთილი", "ისანი", "საბურთალო"]

# ✅ აბრუნებს მხოლოდ იმ რაიონებს, სადაც ატვირთული ფაილი არსებობს
def get_available_districts(weight):
    weight_path = os.path.join(BASE_DIR, str(weight))
    if not os.path.exists(weight_path):
        return []

    available = []
    for district in DISTRICTS:
        district_path = os.path.join(weight_path, district)
        if os.path.isdir(district_path) and os.listdir(district_path):
            available.append(district)
    return available

# ✅ აგზავნის ფაილს და გადააქვს delivered_files-ში
async def send_and_move_file(chat_id, weight, district):
    district_path = os.path.join(BASE_DIR, str(weight), district)
    if not os.path.exists(district_path):
        await bot.send_message(chat_id, "📁 ფაილი ვერ მოიძებნა.")
        return
    
    files = os.listdir(district_path)
    if not files:
        await bot.send_message(chat_id, "❌ ამ რაიონში ფაილები აღარ არის.")
        return

    file_name = files[0]
    file_path = os.path.join(district_path, file_name)
    delivered_path = os.path.join(DELIVERED_DIR, str(weight), district)
    os.makedirs(delivered_path, exist_ok=True)

    # 📤 გაგზავნა მომხმარებელზე
    with open(file_path, "rb") as f:
        await bot.send_document(chat_id, f)

    # 📦 გადატანა delivered_files-ში
    shutil.move(file_path, os.path.join(delivered_path, file_name))
    await bot.send_message(chat_id, f"✅ ფაილი გაგზავნილია და გადატანილია საქაღალდეში {delivered_path}")

# 📋 ბრძანება — ხელმისაწვდომი რაიონების სია
@dp.message_handler(commands=["areas"])
async def show_districts(message: types.Message):
    weights = ["0.15", "0.30", "0.50"]
    text = "📦 ხელმისაწვდომი რაიონები:\n\n"
    for w in weights:
        available = get_available_districts(w)
        if available:
            text += f"⚖️ {w} გრამი:\n" + "\n".join([f"• {d}" for d in available]) + "\n\n"
    if text.strip() == "📦 ხელმისაწვდომი რაიონები:":
        text = "⛔ ამჟამად ფაილები არ არის ატვირთული."
    await message.answer(text)

# 📋 ტესტად ფაილის გაგზავნა ხელით
@dp.message_handler(commands=["send"])
async def send_example(message: types.Message):
    # ფორმატი: /send 0.15 ვარკეთილი
    parts = message.text.split()
    if len(parts) != 3:
        await message.answer("გამოიყენე ფორმატი: /send 0.15 ვარკეთილი")
        return
    weight, district = parts[1], parts[2]
    if district not in DISTRICTS:
        await message.answer("❌ ასეთი რაიონი არ არსებობს სიაში.")
        return
    await send_and_move_file(message.chat.id, weight, district)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
