from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
import os
from dotenv import load_dotenv
import requests

# .env ფაილიდან ტოკენის ჩატვირთვა
load_dotenv()
TOKEN = os.getenv("TOKEN")
CRYPTOPAY_TOKEN = os.getenv("CRYPTOPAY_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

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


# ---------------------- პროდუქტის დეტალები (ფაილებიდან რაიონების ჩვენება) ----------------------
@dp.callback_query_handler(lambda c: c.data.startswith("product_"))
async def product_details(callback: types.CallbackQuery):
    products = {
        "product_meta15": ("🔥 მეტა 0.15 გ", "0.15", 115),
        "product_meta30": ("💎 მეტა 0.30 გ", "0.30", 200),
        "product_meta50": ("👑 მეტა 0.50 გ", "0.50", 350)
    }

    key = callback.data
    if key not in products:
        return await callback.message.answer("❌ პროდუქტი ვერ მოიძებნა.")

    name, weight, price = products[key]
    base_folder = "delivery_files"
    weight_folder = os.path.join(base_folder, weight)

    # მოიძიე მხოლოდ ის რაიონები, სადაც ფაილი არსებობს
    available_regions = []
    if os.path.exists(weight_folder):
        for file in os.listdir(weight_folder):
            if file.lower().endswith((".jpg", ".png", ".jpeg", ".pdf", ".zip")):
                region_name = os.path.splitext(file)[0].capitalize()
                available_regions.append(region_name)

    if not available_regions:
        return await callback.message.answer("📂 ამ წონისთვის ფაილები ჯერ არ არის ატვირთული.")

    # ღილაკები მხოლოდ ხელმისაწვდომი რაიონებისთვის
    region_keyboard = InlineKeyboardMarkup(row_width=2)
    for region in available_regions:
        region_keyboard.add(InlineKeyboardButton(region, callback_data=f"buy_{key}_{region.lower()}"))

    region_keyboard.add(InlineKeyboardButton("🔙 უკან", callback_data="products_menu"))

    await callback.message.answer(
        f"{name}\n💵 ფასი: {price} GEL\n📍 აირჩიე მიწოდების რაიონი 👇",
        reply_markup=region_keyboard
    )


# ---------------------- ყიდვა (გადახდა და ფაილის გაგზავნა) ----------------------
@dp.callback_query_handler(lambda c: c.data.startswith("buy_"))
async def buy_product(callback: types.CallbackQuery):
    parts = callback.data.split("_", 3)
    if len(parts) < 3:
        return await callback.message.answer("⚠️ მონაცემი არასწორია.")

    _, product_key, region = parts
    region = region.lower()

    weights = {
        "product_meta15": ("0.15", 115),
        "product_meta30": ("0.30", 200),
        "product_meta50": ("0.50", 350)
    }

    if product_key not in weights:
        return await callback.message.answer("❌ პროდუქტის ინფორმაცია ვერ მოიძებნა.")

    weight, price = weights[product_key]
    base_path = os.path.join("delivery_files", weight)

    # სცადე სხვადასხვა გაფართოება
    file_path = None
    for ext in [".jpg", ".png", ".jpeg", ".pdf", ".zip"]:
        test_path = os.path.join(base_path, f"{region}{ext}")
        if os.path.exists(test_path):
            file_path = test_path
            break

    if not file_path:
        return await callback.message.answer("❌ ამ რაიონისთვის ფაილი ვერ მოიძებნა.")

    # აქ უნდა დაემატოს გადახდის შემოწმება (ახლა უბრალოდ იგზავნება)
    await callback.message.answer(f"✅ გადახდა დადასტურებულია.\n📦 აი, შენი ფაილი ({region.title()}) 👇")

    with open(file_path, "rb") as file:
        await bot.send_document(callback.from_user.id, file)


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
    await callback.message.edit_caption(caption, reply_markup=keyboard)


# ---------------------- ბოლო ყიდვა ----------------------
@dp.callback_query_handler(lambda c: c.data == "last_purchase")
async def last_purchase(callback: types.CallbackQuery):
    await callback.message.answer("🧾 შენი ბოლო ყიდვა:\nჯერ არაფერი შეგიძენია 🕓")


# ---------------------- Support ----------------------
@dp.callback_query_handler(lambda c: c.data == "support_menu")
async def support(callback: types.CallbackQuery):
    await callback.message.answer("💬 დახმარებისთვის მოგვწერე: @support_username")


# ---------------------- ბოტის გაშვება ----------------------
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
