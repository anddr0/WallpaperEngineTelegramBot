import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ContentType

import variables
from db import db_start, create_profile, edit_num_of_walls, edit_posted, get_stats, get_top, get_id
from variables import API_TOKEN, WALLS_CHAT, CHANNELS_ID, MY_ID, inline_keyboard, stats_keyboard


async def on_startup(_):
    await db_start()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


# state for getting media
class Form(StatesGroup):
    get_media = State()

# -------------------------------------/start-------------------------------------


@dp.message_handler(commands=['start', 'help'])
async def start_handler(message: types.Message):
    await create_profile(username=message['chat']['username'],
                         user_id=message.chat.id, first_name=message['chat']['first_name'])
    await message.answer("Hi. This is a bot where you can offer your wallpaper, "
                         "and compete with other people!", reply_markup=inline_keyboard)
    await message.delete()

# -------------------------------------Handle user posted wallpapers-------------------------------------


@dp.channel_post_handler(content_types=['photo', 'video', 'document'])
async def handle_sends(message: types.Message):
    if message.chat.id == CHANNELS_ID and message.caption is not None and message.caption[0] == "@":
        message_id = await get_id(message.caption[1:])
        await edit_posted(username=message.caption[1:])
        try:
            await bot.send_message(chat_id=message_id[0], text="Hey! Your wallpaper <i>has been posted!</i>👍",
                                   parse_mode="html", reply_markup=stats_keyboard)
        except:
            await bot.send_message(chat_id=MY_ID, text=f'User {message.caption} blocked the bot')


# -------------------------------------Send media-------------------------------------


@dp.callback_query_handler(text="send_wallpaper")
async def send_wallpaper(callback: types.CallbackQuery):
    await Form.get_media.set()
    await callback.message.delete()
    await callback.message.answer("Send photo / video / file of your wallpaper")


@dp.message_handler(state=Form.get_media, content_types=['photo', 'video', 'document'])
async def media_awaiting(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.content_type == 'photo':
            photo = message.photo[0].file_id
            await bot.send_photo(chat_id=WALLS_CHAT, photo=photo, caption=message.chat.username)
        elif message.content_type == 'video':
            video = message['video']['file_id']
            await bot.send_video(chat_id=WALLS_CHAT, video=video, caption=message.chat.username)
        elif message.content_type == 'document':
            doc = message['document']['file_id']
            await bot.send_document(chat_id=WALLS_CHAT, document=doc, caption=message.chat.username)

    await edit_num_of_walls(username=message.chat.username)
    await message.answer("✅<b>Success!</b>\nYour wallpaper has been sent for <b>moderation.</b>"
                         "\nWhen it passes the check it will be <i>published!</i>",
                         reply_markup=inline_keyboard, parse_mode="html")
    await state.finish()

# -------------------------------------Send status-------------------------------------


@dp.callback_query_handler(text="stats")
async def send_user_status(callback: types.CallbackQuery):
    stats = await get_stats(callback.message.chat.username)
    await callback.message.delete()
    await callback.message.answer(f'<b>📨Number of sent wallpapers:</b> <i>{stats[0]}</i>,'
                                  f'\n<b>🖼Your posted wallpapers:</b> <i>{stats[1]}</i>,'
                                  f'\n<b>🥇Your current rank:</b> <i>{stats[2]}</i>',
                                  reply_markup=inline_keyboard, parse_mode="html")

# -------------------------------------Send top 5-------------------------------------


@dp.callback_query_handler(text="top_5")
async def send_user_status(callback: types.CallbackQuery):
    await callback.message.delete()
    top = await get_top()
    val = 0
    str_to_print = ""
    for i in sorted(top, key=lambda x: x[3], reverse=True):
        if val < 5:
            str_to_print += f'<b>{i[2]}</b> <b>[{i[5]}]</b>: ' \
                            f'\n<i>posted</i> - <b>{i[4]}</b> <b>|</b> <i>sent wallpapers</i> - <b>{i[3]}</b>\n\n'
            val += 1
        else:
            break
    await callback.message.answer(str_to_print, parse_mode='html', reply_markup=inline_keyboard)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

