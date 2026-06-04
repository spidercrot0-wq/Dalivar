import asyncio
import logging
import json
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# ⚠️ ВСТАВЬ СВОЙ ТОКЕН ИЗ BOTFATHER МЕЖДУ КАВЫЧКАМИ:
BOT_TOKEN = "8803937143:AAE_RLWCQTZbVWphuup0e0Zb5hooNOtVBtY"
WEBAPP_URL = "https://dalivar.vercel.app"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🚀 Открыть Хабза-Пром", web_app=WebAppInfo(url=WEBAPP_URL))]
        ],
        resize_keyboard=True
    )
    
    await message.answer(
        f"Привет, {message.from_user.first_name}!\n\n"
        f"🏃‍♂️ **Если ты БЕГУН:**\n"
        f"Твой личный код для заказов: `{message.from_user.id}`\n"
        f"*(Нажми на него, чтобы скопировать, и дай покупателю)*\n\n"
        f"🛒 **Если ты ПОКУПАТЕЛЬ:**\n"
        f"Нажми кнопку ниже, чтобы открыть меню доставки.",
        reply_markup=kb,
        parse_mode="Markdown"
    )

@dp.message(F.web_app_data)
async def handle_webapp_data(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        if data.get("action") == "new_order":
            order_text = data.get("text")
            runner_id = data.get("runner_id") # Считываем ID бегуна, который ввели на сайте
            
            inline_kb = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Принять заказ", callback_data=f"accept_{message.from_user.id}"),
                    InlineKeyboardButton(text="❌ Отклонить", callback_data="decline_order")
                ]
            ])
            
            if runner_id:
                try:
                    # Отправляем сообщение напрямую бегуну по его Telegram ID
                    await bot.send_message(
                        chat_id=int(runner_id), 
                        text=f"🔔 **Новый заказ лично для тебя!**\n\n{order_text}", 
                        parse_mode="Markdown", 
                        reply_markup=inline_kb
                    )
                    await message.answer("🎉 Заказ успешно отправлен выбранному бегуну в личку!")
                except Exception:
                    await message.answer("⚠ Ошибка: Бот не смог отправить сообщение бегуну. Проверь ID, или пусть бегун сначала зайдет в этого бота и нажмет /start.")
            else:
                await message.answer("⚠ Ошибка: Код бегуна не указан.")
                
    except Exception as e:
        logging.error(f"Ошибка WebApp: {e}")

@dp.callback_query(F.data.startswith("accept_"))
async def process_accept_order(callback: types.CallbackQuery):
    await callback.message.edit_text(text=f"{callback.message.text}\n\n🏃‍♂️ **Статус: Заказ принят бегуном!**", parse_mode="Markdown")
    await callback.answer("Вы приняли заказ!", show_alert=True)

@dp.callback_query(F.data == "decline_order")
async def process_decline_order(callback: types.CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer("Заказ отклонен.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
