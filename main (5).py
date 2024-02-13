import asyncio
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

waiting = False
isphoto = False
run = True
ANSWER_TEXT = "Ваш подарок 🎁 действует только 24 часа. Только сегодня есть хорошая возможность максимально сэкономить 🔥. Пришлите в ответ на данное сообщение фото, оно Вас ни к чему не обязывает, как только пришлёте - в этот самый момент я рассчитаю стоимость и активирую Ваш подарок, а все вопросы обсудим перед покупкой 👌."
ANSWER2_TEXT = "Наши портреты:\n🔥 из 100% хлопка\n🔥25 лет гарантии от выцветания и провисания\n🔥Ручная отрисовка художником\n\nВаш бонус сгорит ⏳ через 21 час, не упустите шанс им воспользоваться\n Вам нужна помощь с выбором фото?"
ANSWER3_TEXT = "Сейчас подключится Мила и поможет Вам"

bot_token = '6513741895:AAHZxWPTy8Z833pOSD3aVvDwECe3ZeREf9M'
bot = Bot(token=bot_token)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


class Form(StatesGroup):
    photo = State()

@dp.message_handler(state=Form.photo)
@dp.message_handler(content_types=types.ContentType.PHOTO, state=None)
async def process_name(message: types.Message, state: FSMContext):
    global isphoto
    async with state.proxy() as data:
        if waiting and not isphoto:
            isphoto = True
            await message.answer(ANSWER3_TEXT)

async def wait(chat_id, timeToWait, text, message_id):
    global isphoto
    await asyncio.sleep(timeToWait)
    if text and not isphoto and run:
        await bot.send_message(chat_id, text)
    elif not text and isphoto:
        try:
            await bot.delete_message(chat_id, message_id)
            isphoto = False
        except:
            pass


@dp.callback_query_handler(text='off') 
async def inline_kb_answer_callback_handler(query: types.CallbackQuery):
    global run
    if query.data == "off":
        run = False
        await bot.delete_message(mes.chat.id, mes.message_id)

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    global keyboard_markup, mes, run
    PHOTO = types.InputFile("photo.jpeg")
    run = True
    keyboard_markup = types.InlineKeyboardMarkup()
    text_and_data = (("Ваш подарок 🎁  - 1!", 'accept'), ("Ваш подарок 🎁  - 2!", 'accept'), ("Ваш подарок 🎁  - 3!", 'accept'),(("Не беспокоить", 'off')))
    row_btns = [types.InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data]
    for item in row_btns:
        keyboard_markup.row(item)
    mes = await message.answer_photo(PHOTO, reply_markup=keyboard_markup)
    asyncio.create_task(wait(message.chat.id, 10800, ANSWER2_TEXT, mes.message_id))
    asyncio.create_task(wait(message.chat.id, 86400, None, mes.message_id))

@dp.callback_query_handler(text='accept') 
async def inline_kb_answer_callback_handler(query: types.CallbackQuery):
    global waiting
    if query.data == "accept":
        await bot.send_message(query.from_user.id, ANSWER_TEXT)
        waiting = True

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, fast=True, relax=0, timeout=0)