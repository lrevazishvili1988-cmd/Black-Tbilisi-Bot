import telebot
import os
import json
from dotenv import load_dotenv
from decimal import Decimal
from cryptopay import CryptoPay

# დატვირთე გარემოს ცვლადები
load_dotenv()

TOKEN = os.getenv("TOKEN")
CRYPTOPAY_TOKEN = os.getenv("CRYPTOPAY_TOKEN")

bot = telebot.TeleBot(TOKEN)
crypto = CryptoPay(CRYPTOPAY_TOKEN, testnet=False)

# ------------------------
# დამხმარე ფუნქციები
# ------------------------
def load_data():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(data):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ------------------------
# /start
# ------------------------
@bot.message_handler(commands=["start"])
def start(message):
    user_id = str(message.chat.id)
    data = load_data()

    if user_id not in data:
        data[user_id] = {"balance": 0}
        save_data(data)

    balance = data[user_id]["balance"]

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🛍 პროდუქცია", "💰 ბალანსი")
    markup.row("🧾 ბოლო ყიდვა", "💬 Support")

    bot.send_message(
        message.chat.id,
        f"გამარჯობა {message.from_user.first_name}!\n"
        f"შენი ბალანსი: 💸 {balance} GEL",
        reply_markup=markup
    )

# ------------------------
# ბალანსი
# ------------------------
@bot.message_handler(func=lambda m: m.text == "💰 ბალანსი")
def balance_menu(message):
    user_id = str(message.chat.id)
    data = load_data()
    balance = data.get(user_id, {}).get("balance", 0)

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("➕ შევსება", callback_data="topup"))

    bot.send_message(message.chat.id, f"შენი ბალანსი: 💸 {balance} GEL", reply_markup=markup)

# ------------------------
# ბალანსის შევსება
# ------------------------
@bot.callback_query_handler(func=lambda call: call.data == "topup")
def ask_topup_amount(call):
    bot.send_message(call.message.chat.id, "💵 რა თანხის დამატება გსურთ? ჩაწერეთ თანხა ლარში:")
    bot.register_next_step_handler(call.message, process_topup_amount)

def process_topup_amount(message):
    try:
        amount_gel = Decimal(message.text)
        usdt_rate = Decimal("2.70")  # 1 USDT ≈ 2.70 GEL
        usdt_amount = round(amount_gel / usdt_rate, 2)

        invoice = crypto.create_invoice(asset="USDT", amount=float(usdt_amount), description="ბალანსის შევსება")

        bot.send_message(
            message.chat.id,
            f"შესატანი თანხა: {usdt_amount} USDT\n"
            f"გადაიხადე აქ 👇\n{invoice.pay_url}"
        )
    except Exception:
        bot.send_message(message.chat.id, "❌ არასწორი თანხა. სცადეთ თავიდან.")

# ------------------------
print("🤖 ბოტი გაეშვა...")
bot.infinity_polling()
