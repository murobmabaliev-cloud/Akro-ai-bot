

import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from openai import AsyncOpenAI

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN or not OPENAI_API_KEY:
    raise RuntimeError(
        "BOT_TOKEN yoki OPENAI_API_KEY sozlanmagan!"
    )

client = AsyncOpenAI(api_key=OPENAI_API_KEY)
MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Men Akro AI 🤖\nSavolingni yoz!"
    )


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    await update.message.chat.send_action("typing")

    try:
        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Sen Akro AI nomli foydali yordamchisan. "
                        "O'zbek tilida sodda va tushunarli javob ber."
                    ),
                },
                {"role": "user", "content": update.message.text},
            ],
        )

        answer = response.choices[0].message.content
        await update.message.reply_text(
            answer or "Hozir javob tayyorlay olmadim."
        )

    except Exception:
        logging.exception("OpenAI API xatosi")
        await update.message.reply_text(
            "Xatolik yuz berdi. API kaliti, balans va modelni tekshir."
        )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, chat)
    )

    print("Akro AI ishga tushmoqda...")
    app.run_polling()


if __name__ == "__main__":
    main()
