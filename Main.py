import json
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from dotenv import load_dotenv

# .env ფაილიდან ტოკენის წაკითხვა
load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

with open("Data.json", "r", encoding="utf-8") as f:
    products = json.load(f)

@dp.message_handler(commands=["start", "menu"])
async def start_menu(message: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📦 პროდუქცია", "💸 ბალანსი")
    kb.add("🧾 გადახდა", "ℹ️ დახმარება")

    await message.answer(
        "👋 მოგესალმებით თბილისში საუკეთესო შოპში Black Tbilisi Life !!!\n"
        "მიყევით მენიუს და აირჩიეთ კატეგორია 👇",
        reply_markup=kb
    )

@dp.message_handler(lambda message: message.text == "📦 პროდუქცია")
async def show_products(message: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for p in products:
        kb.add(p["name"])
    kb.add("🔙 უკან")
    await message.answer("აირჩიეთ პროდუქტი 👇", reply_markup=kb)

@dp.message_handler(lambda message: any(p["name"] == message.text for p in products))
async def show_product_details(message: types.Message):
    product = next(p for p in products if p["name"] == message.text)
    text = f"🛍 <b>{product['name']}</b>\n💰 ფასი: {product['price']}\n\n{product['desc']}"
    await message.answer(text, parse_mode="HTML")

@dp.message_handler(lambda message: message.text == "🔙 უკან")
async def back_to_menu(message: types.Message):
    await start_menu(message)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
