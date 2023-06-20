import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from db import db_start, close, create_profile, sent_increase, posted_increase, get_user_data, get_all_users, get_ids
from variables import API_TOKEN, WALLS_CHAT, MY_ID, \
    inline_keyboard, status, cancel_keyboard, remove_keyboard, moderation_keyboard, check_post_keyboard

from user_class import User

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


# state for getting media and message
class Form(StatesGroup):
    get_media = State()
    message = State()
    send_message = State()


# -------------------------------------on_startup, on_shutdown-------------------------------------
async def on_startup(_):
    await db_start()


async def on_shutdown(_):
    await close()


# -------------------------------------/start-------------------------------------


@dp.message_handler(commands=['start', 'menu'])
async def start_handler(message: types.Message):
    logging.info("Processing command start")
    await message.delete()
    username = message['chat']['username']
    user_id = message.chat.id
    user_data = User(first_name=message['chat']['first_name'], language_code=message["from"]["language_code"])
    await create_profile(user_id, username, user_data)
    if message.chat.type != "private":
        await message.answer("❗️<b>Warning</b>❗️"
                             "\n<i>We are sorry, but when bot is in <b>group</b> it does not displays on rank.</i>  ️"
                             "\nIf you are 🆗 with this - continue", parse_mode="html")
    await message.answer("<b>Hello!</b>👋😊\n<i>This is a bot where you can share your favorite wallpaper, "
                            "and compete with other people in wallpaper coolness!</i>😁",
                            reply_markup=inline_keyboard, parse_mode="html")


# -------------------------------------Send media-------------------------------------


@dp.callback_query_handler(text="send_wallpaper")
async def send_wallpaper(callback: types.CallbackQuery):
    logging.info("Processing sending wallpaper")
    await Form.get_media.set()
    await callback.message.answer("📩 Send <b>photo</b> / <b>video</b> / <b>file</b> of your wallpaper",
                                  reply_markup=cancel_keyboard, parse_mode="html")


@dp.message_handler(state=Form.get_media, content_types=['photo', 'video', 'document'])
async def media_awaiting(message: types.Message, state: FSMContext):
    caption = message.caption if message.caption is not None else ""
    # Checking what user sent to bot
    await bot.copy_message(chat_id=WALLS_CHAT, from_chat_id=message.chat.id, message_id=message.message_id,
                           reply_markup=moderation_keyboard, parse_mode='html',
                           caption=f"{message.chat.id}|<a href='tg://user?id={message.chat.id}'>"
                                   f"{message.chat.username}</a>|<code>{caption}</code>")
    # Increasing sent wallpapers in db
    await sent_increase(user_id=message.chat.id)
    # Informing user about success and deleting the reply keyboard
    await message.reply("✅<b>Success!</b>\nYour wallpaper has been sent for <b>moderation.</b>"
                        "\nWhen it passes the check it will be <i>published!</i>",
                        reply_markup=remove_keyboard, parse_mode="html")
    await message.answer("<b>Hello!</b>👋😊\n<i>This is a bot where you can share your favorite wallpaper, "
                         "and compete with other people in wallpaper coolness!</i>😁",
                         reply_markup=inline_keyboard, parse_mode="html")
    await state.finish()


@dp.message_handler(state=Form.get_media, text="Cancel")
async def cancel_send_media(message: types.Message, state: FSMContext):
    await message.delete()
    await state.finish()
    await message.answer("❗️ Wallpaper sending has been cancelled", reply_markup=remove_keyboard)
    await message.answer("<b>Hello!</b>👋😊\n<i>This is a bot where you can share your favorite wallpaper, "
                         "and compete with other people in wallpaper coolness!</i>😁",
                         reply_markup=inline_keyboard, parse_mode="html")


# -------------------------------------Handle moderation callbacks-------------------------------------


@dp.callback_query_handler(text="approve_wallpaper")
async def approving_wallpaper(callback: types.CallbackQuery):
    logging.info("Approving user wallpaper")
    caption = callback.message.caption.split("|")
    await callback.message.edit_reply_markup(None)
    await callback.message.reply("✅ This wallpaper has been approved")
    await callback.message.pin()
    await posted_increase(caption[0])
    await bot.copy_message(chat_id=caption[0], from_chat_id=callback.message.chat.id,
                           message_id=callback.message.message_id,
                           caption="✅ <i>Your wallpaper has been <b>approved!</b></i>😊", parse_mode="html")


@dp.callback_query_handler(text="decline_wallpaper")
async def declining_wallpaper(callback: types.CallbackQuery):
    logging.info("Declining user wallpaper")
    caption = callback.message.caption.split("|")
    await callback.message.edit_reply_markup(None)
    await callback.message.reply("🚫 This wallpaper has been declined", reply_markup=remove_keyboard)
    await bot.copy_message(chat_id=caption[0], from_chat_id=callback.message.chat.id,
                           message_id=callback.message.message_id,
                           caption="🚫 <i>Your wallpaper has been <b>declined</b></i>😔", parse_mode="html")


# -------------------------------------Send status-------------------------------------


@dp.callback_query_handler(text="stats")
async def send_user_status(callback: types.CallbackQuery):
    logging.info("Sending stats to user")
    user_data = (await get_user_data(callback.message.chat.id)).get_stats()
    await callback.message.edit_text(f'◼️◼️<b>STATISTIC</b>◼️◼️\n\n'
                                     f'| <i>📨 Sent wallpapers:</i> <b>{user_data[2]}</b>,\n|'
                                     f'\n| <i>🖼 Posted wallpapers:</i> <b>{user_data[3]}</b>,\n|'
                                     f'\n| <i>🥇 Current rank:</i> <b>{user_data[1]}</b>\n',
                                     reply_markup=inline_keyboard, parse_mode="html")


# -------------------------------------Send top 5-------------------------------------


def check_username(user):
    return user[2].first_name is not None


async def get_top_5():
    logging.info("Sending to user top 5")
    users = await get_all_users()
    str_to_send = ""
    sorted_users = list(filter(check_username, sorted(users, key=lambda x: (x[2].posted_walls, x[2].sent_walls), reverse=True)))
    length = len(sorted_users) if len(sorted_users) < 5 else 5
    for i in range(length):
        user = sorted_users[i]
        name_to_print = user[1] if user[1] is not None else user[2].first_name
        str_to_send += f'\n{i + 1}: {status[i]} <a href = "tg://user?id={user[0]}">{name_to_print}</a>' \
                       f'\n-------------------------------' \
                       f'\n|<i>Posted wallpapers</i>: <b>{user[2].posted_walls}</b>' \
                       f'\n|<i>Sent wallpapers</i>: <b>{user[2].sent_walls}</b>' \
                       f'\n|<i>Rank</i>: <b>{user[2].rank}</b> \n'

    return "It's empty here..." if str_to_send == "" else str_to_send


@dp.callback_query_handler(text="top_5")
async def send_user_status(callback: types.CallbackQuery):
    await callback.message.edit_text(await get_top_5(), parse_mode='html', reply_markup=inline_keyboard)


# -------------------------------------Send messages to all users-------------------------------------


@dp.message_handler(commands=['send_message', 's_m'])
async def send_message_to_all_users(message: types.Message):
    logging.info("Processing command send message to all users")
    if message.chat.id == MY_ID:
        await Form.message.set()
        await message.delete()
        await message.answer("📩 Send <b>photo</b> / <b>video</b> / <b>file</b> or <b>text</b> of your message",
                             reply_markup=cancel_keyboard, parse_mode="html")
    else:
        await message.answer(text="You do not have permission to use this command")


@dp.message_handler(state=Form.message, text="Cancel")
async def cancel_send_message(message: types.Message, state: FSMContext):
    await message.delete()
    await state.finish()
    await message.answer("❗️ Sending message has been cancelled", reply_markup=remove_keyboard)
    await message.answer("<b>Hello!</b>👋😊\n<i>This is a bot where you can share your favorite wallpaper, "
                         "and compete with other people in wallpaper coolness!</i>😁",
                         reply_markup=inline_keyboard, parse_mode="html")


@dp.message_handler(state=Form.message, content_types=['photo', 'video', 'document', 'text'])
async def message_awaiting(message: types.Message, state: FSMContext):
    await bot.copy_message(chat_id=MY_ID, from_chat_id=message.chat.id, message_id=message.message_id,
                           reply_markup=message.reply_markup)
    await message.answer("❗️ <i>Post this message? ❗️</i>", reply_markup=check_post_keyboard, parse_mode="html")
    async with state.proxy() as data:
        data['message'] = message
    await Form.next()


@dp.callback_query_handler(state=Form.send_message, text="not_posting")
async def posting(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("🚫 <i>Canceling this post... ️</i>", parse_mode="html", reply_markup=remove_keyboard)
    await callback.message.answer("📩 Send <b>photo</b> / <b>video</b> / <b>file</b> or <b>text</b> of your message",
                                  reply_markup=cancel_keyboard, parse_mode="html")
    await Form.previous()


@dp.callback_query_handler(state=Form.send_message, text="posting")
async def posting(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        message = data['message']
    for id_tuple in await get_ids():
        current_id = id_tuple[0]
        await bot.copy_message(chat_id=current_id, from_chat_id=message.chat.id, message_id=message.message_id,
                               reply_markup=message.reply_markup)
    await callback.message.answer("✅ <i>Message has been posted successfully ️</i>",
                                  reply_markup=remove_keyboard, parse_mode="html")
    await message.answer("<b>Hello!</b>👋😊\n<i>This is a bot where you can share your favorite wallpaper, "
                         "and compete with other people in wallpaper coolness!</i>😁",
                         reply_markup=inline_keyboard, parse_mode="html")
    await state.finish()


# -------------------------------------Send db-------------------------------------


@dp.message_handler(commands=['send_database', 's_db'])
async def send_database(message: types.Message):
    logging.info("Processing command send database")
    await message.delete()
    if message.chat.id == MY_ID:
        try:
            await bot.send_document(chat_id=MY_ID, document=open('users.db', 'rb'))
            await message.answer("<b>Hello!</b>👋😊\n<i>This is a bot where you can share your favorite wallpaper, "
                                 "and compete with other people in wallpaper coolness!</i>😁",
                                 reply_markup=inline_keyboard, parse_mode="html")
        except:
            await message.answer("❗️<i> The database does not exist </i>❗️", parse_mode="html")
    else:
        await message.answer(text="You do not have permission to use this command")

# -------------------------------------MAIN-------------------------------------

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
