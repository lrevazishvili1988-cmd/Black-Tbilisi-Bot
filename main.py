from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
import os
from dotenv import load_dotenv
import requests

load_dotenv()
TOKEN = os.getenv("TOKEN")

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

    photo_path = "banner.PNG"  # ← შეცვლილია სწორ ფაილზე
    caption = "👋 მოგესალმებით Black Tbilisi Meth მაღაზიაში !!\n\nაირჩიეთ ქმედება ქვემოთ 👇"

    with open(photo_path, "rb") as photo:
        await bot.send_photo(message.chat.id, photo=photo, caption=caption, reply_markup=keyboard)


# --- ბალანსის შევსება (CryptoBot ინტეგრაცია) ---
@dp.callback_query_handler(lambda c: c.data == "balance_add")
async def add_balance(callback: types.CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    await callback.message.answer("შეიყვანე თანხა (USD-ში) რომლის შევსებაც გინდა 💵")

    @dp.message_handler(lambda m: m.text.isdigit())
    async def process_amount(message: types.Message):
        amount = message.text
        payload = str(user_id)

        url = "https://pay.crypt.bot/api/createInvoice"
        headers = {"Crypto-Pay-API-Token": os.getenv("CRYPTOPAY_TOKEN")}
        data = {
            "asset": "USDT",
            "amount": amount,
            "currency_type": "crypto",
            "description": "Black Tbilisi Life ბალანსის შევსება",
            "payload": payload
        }

        r = requests.post(url, headers=headers, json=data).json()
        if r.get("ok"):
            pay_url = r["result"]["pay_url"]
            await message.answer(f"💳 გადახდის ბმული მზადაა:\n👉 {pay_url}")
        else:
            await message.answer("❌ ვერ მოხერხდა გადახდის ბმულის შექმნა.")


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
    photo_path = "banner.PNG"
    caption = "🏠 დაბრუნდით მთავარ მენიუში.\nაირჩიეთ ქმედება 👇"
    with open(photo_path, "rb") as photo:
        await callback.message.edit_media(InputMediaPhoto(photo, caption=caption), reply_markup=keyboard)


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


# ---------------------- პროდუქტის დეტალები ----------------------
@dp.callback_query_handler(lambda c: c.data.startswith("product_"))
async def product_details(callback: types.CallbackQuery):
    products = {
        "product_meta15": ("🔥 მეტა 0.15 გ", 115),
        "product_meta30": ("💎 მეტა 0.30 გ", 200),
        "product_meta50": ("👑 მეტა 0.50 გ", 350)
    }

    key = callback.data
    if key not in products:
        return await callback.message.answer("❌ პროდუქტი ვერ მოიძებნა.")

    name, price = products[key]
    text = f"{name}\n💵 ფასი: {price} GEL\n\n📍 აირჩიეთ მიწოდების რაიონი 👇"

    region_keyboard = InlineKeyboardMarkup(row_width=2)
    regions = [
        "ვაკე", "საბურთალო", "გლდანი", "ისანი",
        "ნაძალადევი", "ვერა", "დიდუბე", "სამგორი"
    ]
    for r in regions:
        region_keyboard.add(InlineKeyboardButton(r, callback_data=f"region_{key}_{r}"))

    region_keyboard.add(InlineKeyboardButton("🔙 უკან", callback_data="products_menu"))

    await callback.message.answer(text, reply_markup=region_keyboard)


# ---------------------- რაიონის არჩევა ----------------------
@dp.callback_query_handler(lambda c: c.data.startswith("region_"))
async def region_selected(callback: types.CallbackQuery):
    _, product_key, region = callback.data.split("_", 2)

    products = {
        "product_meta15": ("🔥 მეტა 0.15 გ", 115),
        "product_meta30": ("💎 მეტა 0.30 გ", 200),
        "product_meta50": ("👑 მეტა 0.50 გ", 350)
    }

    if product_key not in products:
        return await callback.message.answer("❌ პროდუქტი ვერ მოიძებნა.")

    name, price = products[product_key]

    confirm_keyboard = InlineKeyboardMarkup(row_width=1)
    confirm_keyboard.add(
        InlineKeyboardButton("✅ დადასტურება და გადახდა", callback_data=f"buy_{product_key}_{region}"),
        InlineKeyboardButton("🔙 უკან", callback_data="products_menu")
    )

    text = (
        f"📦 {name}\n💵 ფასი: {price} GEL\n"
        f"📍 არჩეული რაიონი: {region}\n\n"
        "გსურთ გადახდაზე გადასვლა?"
    )
    await callback.message.answer(text, reply_markup=confirm_keyboard)


# ---------------------- ყიდვა ----------------------
@dp.callback_query_handler(lambda c: c.data.startswith("buy_"))
async def buy_product(callback: types.CallbackQuery):
    parts = callback.data.split("_", 3)
    if len(parts) == 3:
        _, product_key, region = parts
    else:
        product_key, region = "product_meta15", "უცნობი"

    await callback.answer()
    await callback.message.answer(
        f"💳 გადახდის ბმული მალე დაემატება.\n📍 არჩეული რაიონი: {region}"
    )


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
