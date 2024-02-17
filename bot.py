import logging
from os import getenv

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import db
from db import db_start, close, create_profile, sent_increase, posted_increase, get_ids, get_stats, activity_update
from variables import inline_keyboard, status, cancel_keyboard, remove_keyboard, moderation_keyboard,\
    check_post_keyboard, HELP

from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
load_dotenv()

# Initialize bot and dispatcher
bot = Bot(token=getenv("API_TOKEN"))
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


# -------------------------------------/start, menu-------------------------------------


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    logging.info("Processing command start")
    await message.delete()
    username = message['chat']['username']
    user_id = message.chat.id
    await create_profile(user_id, username, message['chat']['first_name'], message["from"]["language_code"])
    if message.chat.type != "private":
        await message.answer("❗️<b>Warning</b>❗️"
                             "\n<i>We are sorry, but when bot is in <b>group</b> it does not displays on rank.</i>  ️"
                             "\nIf you are 🆗 with this - continue", parse_mode="html")
    await message.answer("<b>Hello!</b>👋😊\n<i>This is a bot where you can share your favorite wallpaper, "
                         "and compete with other people in wallpaper coolness!</i> 😁",
                         reply_markup=inline_keyboard, parse_mode="html")
    await message.answer("/info - information about bot")


@dp.message_handler(commands=['menu'])
async def menu_handler(message: types.Message):
    await activity_update(message.chat.id)
    await message.answer("<b>Hello!</b>👋😊\n<i>This is a bot where you can share your favorite wallpaper, "
                         "and compete with other people in wallpaper coolness!</i> 😁",
                         reply_markup=inline_keyboard, parse_mode="html")

# -------------------------------------/help-------------------------------------


@dp.message_handler(commands=['help', 'info'])
async def help_handler(message: types.Message):
    await activity_update(message.chat.id)
    logging.info("Processing command help")
    await message.answer(HELP, parse_mode="html")


# -------------------------------------Send media-------------------------------------


@dp.callback_query_handler(text="send_wallpaper")
async def send_wallpaper(callback: types.CallbackQuery):
    await activity_update(callback.message.chat.id)
    logging.info("Processing sending wallpaper")
    await Form.get_media.set()
    await callback.message.answer("📩 Send <b>photo</b> / <b>video</b> / <b>file</b> of your wallpaper",
                                  reply_markup=cancel_keyboard, parse_mode="html")


@dp.message_handler(state=Form.get_media, content_types=['photo', 'video', 'document'])
async def media_awaiting(message: types.Message, state: FSMContext):
    caption = message.caption if message.caption is not None else ""
    # Checking what user sent to bot
    await bot.copy_message(chat_id=getenv("WALLS_CHAT"), from_chat_id=message.chat.id, message_id=message.message_id,
                           reply_markup=moderation_keyboard, parse_mode='html',
                           caption=f"{message.chat.id}|<a href='tg://user?id={message.chat.id}'>"
                                   f"{message.chat.username}</a>"
                                   f"\n<code>{caption}</code>")
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
    await activity_update(callback.message.chat.id)
    logging.info("Approving user wallpaper")
    user_id, username = callback.message.caption.split("|")
    await callback.message.edit_reply_markup(None)
    await callback.message.reply("✅ This wallpaper has been approved")
    await callback.message.pin()
    await posted_increase(user_id)
    await bot.copy_message(chat_id=user_id, from_chat_id=callback.message.chat.id,
                           message_id=callback.message.message_id,
                           caption="✅ <i>Your wallpaper has been <b>approved!</b></i>😊", parse_mode="html")
    stats = (await get_stats(user_id))[0]
    await bot.copy_message(chat_id=-1001768811954, from_chat_id=callback.message.chat.id,
                           message_id=callback.message.message_id, parse_mode="html",
                           caption=f"<a href='tg://user?id={user_id}'>{username}</a> <b>[ {stats['rank']} ]</b>")


@dp.callback_query_handler(text="decline_wallpaper")
async def declining_wallpaper(callback: types.CallbackQuery):
    await activity_update(callback.message.chat.id)
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
    await activity_update(callback.message.chat.id)
    logging.info("Sending stats to user")
    user_data = (await db.get_stats(callback.message.chat.id))[0]
    await callback.message.edit_text(f'⚡️️<b>STATISTIC</b>️⚡️'
                                     f'\n-------------------------'
                                     f'\n| <i>📨 Sent wallpapers:</i> <b>{user_data["sent"]}</b>,\n|'
                                     f'\n| <i>🖼 Posted wallpapers:</i> <b>{user_data["posted"]}</b>,\n|'
                                     f'\n| <i>🥇 Current rank:</i> <b>{user_data["rank"]}</b>\n',
                                     reply_markup=inline_keyboard, parse_mode="html")


# -------------------------------------Send top 5-------------------------------------


def check_username(user):
    return user["user_data"].first_name is not None


async def get_top_5():
    sorted_users = await db.get_top_5()
    length = len(sorted_users) if len(sorted_users) < 5 else 5
    str_to_send = ""
    for i in range(length):
        user = sorted_users[i]
        print(user["user_id"])
        name_to_print = user["username"] if user["username"] is not None else user["first_name"]
        str_to_send += f'\n{i + 1}: {status[i]} <a href = "tg://user?id={user["user_id"]}">{name_to_print}</a>' \
                       f'\n-------------------------------' \
                       f'\n|<i>Posted wallpapers</i>: <b>{user["posted"]}</b>' \
                       f'\n|<i>Sent wallpapers</i>: <b>{user["sent"]}</b>' \
                       f'\n|<i>Rank</i>: <b>{user["rank"]}</b> \n'

    return "It's empty here..." if str_to_send == "" else str_to_send


@dp.callback_query_handler(text="top_5")
async def send_user_status(callback: types.CallbackQuery):
    await activity_update(callback.message.chat.id)
    await callback.message.edit_text(await get_top_5(), parse_mode='html', reply_markup=inline_keyboard)


# -------------------------------------Send messages to all users-------------------------------------


@dp.message_handler(commands=['send_message', 's_m'])
async def send_message_to_all_users(message: types.Message):
    logging.info("Processing command send message to all users")
    if message.chat.id == int(getenv("MY_ID")):
        await Form.message.set()
        await message.delete()
        await message.answer("📩 Send message to post",
                             reply_markup=cancel_keyboard, parse_mode="html")
    else:
        await message.answer(f"{getenv('MY_ID').__class__}")
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
    await bot.copy_message(chat_id=getenv("MY_ID"), from_chat_id=message.chat.id, message_id=message.message_id,
                           reply_markup=message.reply_markup)
    await message.answer("❗️ <i>Post this message? ❗️</i>", reply_markup=check_post_keyboard, parse_mode="html")
    async with state.proxy() as data:
        data['message'] = message
    await Form.next()


@dp.callback_query_handler(state=Form.send_message, text="not_posting")
async def posting(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("🚫 <i>Canceling this post... ️</i>", parse_mode="html", reply_markup=remove_keyboard)
    await callback.message.answer("📩 Send message to post",
                                  reply_markup=cancel_keyboard, parse_mode="html")
    await Form.previous()


@dp.callback_query_handler(state=Form.send_message, text="posting")
async def posting(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        message = data['message']
    for id_tuple in await get_ids():
        current_id = id_tuple["user_id"]
        await bot.copy_message(chat_id=current_id, from_chat_id=message.chat.id, message_id=message.message_id,
                               reply_markup=message.reply_markup)
    await callback.message.answer("✅ <i>Message has been posted successfully ️</i>",
                                  reply_markup=remove_keyboard, parse_mode="html")
    await message.answer("<b>Hello!</b>👋😊\n<i>This is a bot where you can share your favorite wallpaper, "
                         "and compete with other people in wallpaper coolness!</i>😁",
                         reply_markup=inline_keyboard, parse_mode="html")
    await state.finish()


# -------------------------------------MAIN-------------------------------------

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
