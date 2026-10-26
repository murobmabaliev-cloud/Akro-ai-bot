
import os
import logging
from openai import AsyncOpenAI
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, ContextTypes, filters
)

logging.basicConfig(level=logging.INFO)

client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
histories = {}
MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Men Akro AI 🤖\nMenga istalgan savolingni yoz!"
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    histories.pop(update.effective_user.id, None)
    await update.message.reply_text("Suhbat xotirasi tozalandi! 🧹")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    history = histories.setdefault(user_id, [])
    history.append({"role": "user", "content": text})
    history[:] = history[-20:]

    try:
        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Sen Akro AI nomli foydali, do'stona yordamchisan. O'zbek tilida javob ber."},
                *history
            ]
        )
        answer = response.choices[0].message.content
        history.append({"role": "assistant", "content": answer})
        await update.message.reply_text(answer)
    except Exception:
        logging.exception("AI xatosi")
        await update.message.reply_text(
            "Hozir javob bera olmadim. API kaliti, model va balansni tekshir."
        )

async def main():
    app = ApplicationBuilder().token(os.environ["BOT_TOKEN"]).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await app.updater.idle()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
