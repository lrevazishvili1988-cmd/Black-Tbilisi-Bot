import os
import random
import shutil
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")
CRYPTOPAY_TOKEN = os.getenv("CRYPTOPAY_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# ძირითადი საქაღალდე ფაილებისთვის
FILES_DIR = "delivery_files"
USED_DIR = "used_files"

# შექმნის შემთხვევაში "used_files" თუ არ არსებობს
os.makedirs(USED_DIR, exist_ok=True)


# ---------------------- მთავარი მენიუ ----------------------
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🛍 პროდუქცია", callback_data="products_menu"),
        InlineKeyboardButton("💰 ბალანსი", callback_data="balance_menu"),
        InlineKeyboardButton("🧾 ბოლო ყიდვა", callback_data="last_purchase"),
        InlineKeyboardButton("💬 Support", callback_data="support_menu")
    )

    photo_path = "banner.PNG"
    caption = "👋 მოგესალმებით Black Tbilisi Meth მაღაზიაში !!\n\nაირჩიეთ ქმედება ქვემოთ 👇"

    if os.path.exists(photo_path):
        with open(photo_path, "rb") as photo:
            await bot.send_photo(message.chat.id, photo=photo, caption=caption, reply_markup=keyboard)
    else:
        await message.answer(caption, reply_markup=keyboard)


# ---------------------- პროდუქციის მენიუ ----------------------
@dp.callback_query_handler(lambda c: c.data == "products_menu")
async def products_menu(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("🔥 მეტა 0.15 გ — 115 GEL", callback_data="product_meta15"),
        InlineKeyboardButton("💎 მეტა 0.30 გ — 200 GEL", callback_data="product_meta30"),
        InlineKeyboardButton("👑 მეტა 0.50 გ — 350 GEL", callback_data="product_meta50"),
        InlineKeyboardButton("🔙 უკან", callback_data="back_main")
    )
    await callback.message.edit_caption("🛍 აირჩიეთ სასურველი პროდუქტი 👇", reply_markup=keyboard)


# --- ამოწმებს ხელმისაწვდომ რაიონებს ---
def get_available_regions(weight_folder):
    path = os.path.join(FILES_DIR, weight_folder)
    if not os.path.exists(path):
        return []

    return [
        name for name in os.listdir(path)
        if os.path.isdir(os.path.join(path, name)) and os.listdir(os.path.join(path, name))
    ]


# --- აბრუნებს შემთხვევით ფაილს ---
def get_random_file(weight_folder, region):
    path = os.path.join(FILES_DIR, weight_folder, region)
    if not os.path.exists(path):
        return None
    files = os.listdir(path)
    if not files:
        return None
    return os.path.join(path, random.choice(files))


# ---------------------- რაიონის არჩევა ----------------------
@dp.callback_query_handler(lambda c: c.data.startswith("product_"))
async def product_details(callback: types.CallbackQuery):
    products = {
        "product_meta15": ("🔥 მეტა 0.15 გ", "0.15", 115),
        "product_meta30": ("💎 მეტა 0.30 გ", "0.30", 200),
        "product_meta50": ("👑 მეტა 0.50 გ", "0.50", 350),
    }

    key = callback.data
    if key not in products:
        return await callback.message.answer("❌ პროდუქტი ვერ მოიძებნა.")

    name, weight, price = products[key]
    available_regions = get_available_regions(weight)

    if not available_regions:
        return await callback.message.answer("❌ ამ წონაზე რაიონები ჯერ არ არის დამატებული.")

    keyboard = InlineKeyboardMarkup(row_width=2)
    for region in available_regions:
        keyboard.add(InlineKeyboardButton(region, callback_data=f"region_{weight}_{region}"))

    await callback.message.answer(
        f"{name}\n💵 ფასი: {price} GEL\n📍 აირჩიეთ მიწოდების რაიონი 👇",
        reply_markup=keyboard
    )


# ---------------------- ყიდვა ----------------------
@dp.callback_query_handler(lambda c: c.data.startswith("region_"))
async def region_selected(callback: types.CallbackQuery):
    _, weight, region = callback.data.split("_", 2)

    confirm_keyboard = InlineKeyboardMarkup(row_width=1)
    confirm_keyboard.add(
        InlineKeyboardButton("✅ დადასტურება და მიღება", callback_data=f"buy_{weight}_{region}"),
        InlineKeyboardButton("🔙 უკან", callback_data="products_menu")
    )

    await callback.message.answer(
        f"📦 არჩეული წონა: {weight} გ\n📍 რაიონი: {region}\n\nგსურთ შეკვეთის დადასტურება?",
        reply_markup=confirm_keyboard
    )


# ---------------------- ყიდვის დადასტურება და ფაილის გაგზავნა ----------------------
@dp.callback_query_handler(lambda c: c.data.startswith("buy_"))
async def buy_product(callback: types.CallbackQuery):
    _, weight, region = callback.data.split("_", 2)
    file_path = get_random_file(weight, region)

    if file_path and os.path.exists(file_path):
        with open(file_path, "rb") as f:
            await callback.message.answer_photo(f, caption=f"📍 {region}\n📦 თქვენი შეკვეთა ✔️")

        # გადააქვს ფაილი used_files-ში
        used_folder = os.path.join(USED_DIR, weight, region)
        os.makedirs(used_folder, exist_ok=True)
        shutil.move(file_path, os.path.join(used_folder, os.path.basename(file_path)))

    else:
        await callback.message.answer("❌ ამ რაიონისთვის ფაილი ვერ მოიძებნა.")


# ---------------------- Support ----------------------
@dp.callback_query_handler(lambda c: c.data == "support_menu")
async def support(callback: types.CallbackQuery):
    await callback.message.answer("💬 დახმარებისთვის მოგვწერე: @support_username")


# ---------------------- უკან დაბრუნება ----------------------
@dp.callback_query_handler(lambda c: c.data == "back_main")
async def back_main(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🛍 პროდუქცია", callback_data="products_menu"),
        InlineKeyboardButton("💰 ბალანსი", callback_data="balance_menu"),
        InlineKeyboardButton("🧾 ბოლო ყიდვა", callback_data="last_purchase"),
        InlineKeyboardButton("💬 Support", callback_data="support_menu")
    )

    caption = "🏠 დაბრუნდით მთავარ მენიუში.\nაირჩიეთ ქმედება 👇"
    photo_path = "banner.PNG"

    if os.path.exists(photo_path):
        with open(photo_path, "rb") as photo:
            await callback.message.edit_media(InputMediaPhoto(photo, caption=caption), reply_markup=keyboard)
    else:
        await callback.message.answer(caption, reply_markup=keyboard)


# ---------------------- ბოტის გაშვება ----------------------
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
