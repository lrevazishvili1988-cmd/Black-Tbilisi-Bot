import json
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from dotenv import load_dotenv
import requests

load_dotenv()

BOT_TOKEN = os.getenv("TOKEN")
CRYPTOPAY_TOKEN = os.getenv("CRYPTOPAY_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

with open("Data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# მონაცემების შენახვა
def save_data():
    with open("Data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    user_id = str(message.from_user.id)
    if "users" not in data:
        data["users"] = {}
    if user_id not in data["users"]:
        data["users"][user_id] = {"balance": 0}
        save_data()
    bal = data["users"][user_id]["balance"]
    await message.answer(f"👋 მოგესალმები Black Tbilisi Life ბოტში!\n\n💰 შენი ბალანსია: {bal} GEL")

@dp.message_handler(commands=["balance"])
async def balance_cmd(message: types.Message):
    user_id = str(message.from_user.id)
    bal = data["users"].get(user_id, {}).get("balance", 0)
    await message.answer(f"💰 შენი ბალანსია: {bal} GEL")

@dp.message_handler(commands=["pay"])
async def create_invoice(message: types.Message):
    try:
        args = message.text.split()
        if len(args) < 2:
            return await message.answer("გამოიყენე ფორმატი:\n`/pay 10` — გადახდა 10 GEL", parse_mode="Markdown")

        amount = float(args[1])
        payload = str(message.from_user.id)  # რომ ვიცოდეთ, ვის ეკუთვნის გადახდა

        url = "https://pay.crypt.bot/api/createInvoice"
        headers = {"Crypto-Pay-API-Token": CRYPTOPAY_TOKEN}
        params = {
            "asset": "USDT",
            "amount": amount,
            "currency_type": "fiat",
            "fiat": "USD",
            "description": "Black Tbilisi Life balance refill",
            "hidden_message": f"User ID: {payload}",
            "payload": payload
        }
        r = requests.post(url, headers=headers, json=params).json()

        if r.get("ok"):
            pay_url = r["result"]["pay_url"]
            await message.answer(f"💳 გადახდის ბმული:\n👉 {pay_url}")
        else:
            await message.answer("❌ გადახდის ბმულის შექმნა ვერ მოხერხდა.")
    except Exception as e:
        await message.answer(f"შეცდომა: {e}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
