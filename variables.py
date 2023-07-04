from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

# -------------------------------------ID'S, TOKENS-------------------------------------
API_TOKEN = '6344045610:AAE27jD-wsl2aD3FPd7vlKDDD7W7JH-zFbI'
MY_ID = 840550973
WALLS_CHAT = -855257472
# -------------------------------------FOR MESSAGES-------------------------------------
# Emoji of user in top 5
status = ["👑", "💎", "⭐️", "🥶", "🥵"]
# Ranks
RANKS = ['Newbie🔰', 'Wallpaper🖼', 'Artisan🧑‍🎨', 'Wallpaperist🎨', 'Enthusiast🤩', 'Decorator🎉', 'Master👨‍🎓',
         'Wizard🧙‍♂️', 'Connoisseur👑', 'Emperor🤴', 'God🙌']
# -------------------------------------KEYBOARDS-------------------------------------
# /start, /help Keyboard
send_button = InlineKeyboardButton(text="Send wallpaper✉️", callback_data="send_wallpaper")
stats_button = InlineKeyboardButton(text="My stats📈", callback_data="stats")
sent_button = InlineKeyboardButton(text="Top 5 wallpaperists🏆", callback_data="top_5")
inline_keyboard = InlineKeyboardMarkup(row_width=2).add(send_button, stats_button, sent_button)

# Cancel send wallpaper keyboard
cancel_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(KeyboardButton("Cancel"))

# Remove reply keyboard
remove_keyboard = ReplyKeyboardRemove()

# Moderation keyboard
approved_button = InlineKeyboardButton(text="✅ Approve", callback_data="approve_wallpaper")
declined_button = InlineKeyboardButton(text="🚫 Decline", callback_data="decline_wallpaper")
moderation_keyboard = InlineKeyboardMarkup().add(approved_button, declined_button)

# Post all users keyboard
post = InlineKeyboardButton(text="✅ Post", callback_data="posting")
do_not_post = InlineKeyboardButton(text="🚫 Do not post", callback_data="not_posting")
check_post_keyboard = InlineKeyboardMarkup().add(post, do_not_post)