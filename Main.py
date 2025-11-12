from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# 🏠 მთავარი მენიუ
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("🛍 აირჩიეთ პროდუქტი", callback_data="products_menu"),
        InlineKeyboardButton("💰 ბალანსი", callback_data="balance_menu")
    )

    photo_path = "banner.png"
    caption = "👋 მოგესალმებით Black Tbilisi Meth მაღაზიაში !!\n\nაირჩიეთ ქმედება ქვემოთ 👇"

    with open(photo_path, "rb") as photo:
        await bot.send_photo(message.chat.id, photo=photo, caption=caption, reply_markup=keyboard)

# 💰 ბალანსის მენიუ
@dp.callback_query_handler(lambda c: c.data == "balance_menu")
async def balance_menu(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("💰 მიმდინარე ბალანსი", callback_data="balance_show"),
        InlineKeyboardButton("➕ ბალანსის შევსება", callback_data="balance_add"),
        InlineKeyboardButton("🔙 უკან", callback_data="back_main")
    )
    await callback.message.edit_caption("💼 ბალანსის მენიუ:\nაირჩიეთ ქმედება 👇", reply_markup=keyboard)

# 💰 მიმდინარე ბალანსი
@dp.callback_query_handler(lambda c: c.data == "balance_show")
async def show_balance(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer("💰 შენი მიმდინარე ბალანსია: 0 GEL")

# ➕ ბალანსის შევსება
@dp.callback_query_handler(lambda c: c.data == "balance_add")
async def add_balance(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer("💳 ბალანსის შევსების ფუნქცია მალე დაემატება 💸")

# 🔙 უკან მთავარ მენიუში
@dp.callback_query_handler(lambda c: c.data == "back_main")
async def back_main(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("🛍 აირჩიეთ პროდუქტი", callback_data="products_menu"),
        InlineKeyboardButton("💰 ბალანსი", callback_data="balance_menu")
    )
    photo_path = "banner.png"
    caption = "🏠 დაბრუნდით მთავარ მენიუში.\nაირჩიეთ ქმედება 👇"
    with open(photo_path, "rb") as photo:
        await callback.message.edit_media(InputMediaPhoto(photo, caption=caption), reply_markup=keyboard)

# 🛍 პროდუქციის მენიუ
@dp.callback_query_handler(lambda c: c.data == "products_menu")
async def products_menu(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("🔥 მეტა 0.15 გ", callback_data="product_meta15"),
        InlineKeyboardButton("💎 მეტა 0.30 გ", callback_data="product_meta30"),
        InlineKeyboardButton("👑 მეტა 0.50 გ", callback_data="product_meta50"),
        InlineKeyboardButton("🔙 უკან", callback_data="back_main")
    )
    await callback.message.edit_caption("🛍 აირჩიეთ სასურველი პროდუქტი 👇", reply_markup=keyboard)

# პროდუქტის დეტალები
@dp.callback_query_handler(lambda c: c.data.startswith("product_"))
async def product_details(callback: types.CallbackQuery):
    data = callback.data
    if data == "product_meta15":
        text = "🔥 **მეტა 0.15 გ**\n💵 ფასი: 115 GEL"
    elif data == "product_meta30":
        text = "💎 **მეტა 0.30 გ**\n💵 ფასი: 200 GEL"
    elif data == "product_meta50":
        text = "👑 **მეტა 0.50 გ**\n💵 ფასი: 350 GEL"
    else:
        text = "❌ პროდუქტი ვერ მოიძებნა."

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("💳 ყიდვა", callback_data=f"buy_{data}"),
        InlineKeyboardButton("🔙 უკან", callback_data="products_menu")
    )

    await callback.message.answer(text, parse_mode="Markdown", reply_markup=keyboard)

# ყიდვის ღილაკი (ჯერ მხოლოდ შეტყობინება)
@dp.callback_query_handler(lambda c: c.data.startswith("buy_"))
async def buy_product(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer("💳 გადახდის ფუნქცია მალე დაემატება (CryptoBot ინტეგრაცია მოდის).")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
