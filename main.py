import cv2, pytesseract, numpy as np, re
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from io import BytesIO
from PIL import Image

TOKEN = "YOUR_BOT_TOKEN"  # @BotFather dan olingan token

def extract_coeffs(image):
    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    text = pytesseract.image_to_string(thresh, config='--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789.x')
    return [float(x.replace('x', '')) for x in re.findall(r'\d+\.\d+x', text)]

def predict_next(coeffs):
    if len(coeffs) < 3: return "⚠️ Yetarli ma'lumot yo'q"
    last = coeffs[-3:]
    avg = sum(last)/3
    return f"📊 Keyingi ehtimol: {avg*0.9:.2f}x - {avg*1.1:.2f}x"

def handle_photo(update: Update, context):
    photo = update.message.photo[-1].get_file()
    img = Image.open(BytesIO(photo.download_as_bytearray()))
    coeffs = extract_coeffs(img)
    update.message.reply_text(
        f"🔍 Topildi: {coeffs[-3:] if coeffs else '❌ Koeffitsient topilmadi'}\n"
        f"{predict_next(coeffs) if coeffs else ''}"
    )

updater = Updater(TOKEN)
updater.dispatcher.add_handler(MessageHandler(Filters.photo, handle_photo))
updater.start_polling()
print("🤖 Bot ishga tushdi!")
updater.idle()
