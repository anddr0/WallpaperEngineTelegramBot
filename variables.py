from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

# -------------------------------------FOR MESSAGES-------------------------------------
# Emoji of user in top 5
status = ["👑", "💎", "⭐️", "🥶", "🥵"]
# Ranks
RANKS = ['Newbie🔰', 'Wallpaper🖼', 'Artisan🧑‍🎨', 'Wallpaperist🎨', 'Enthusiast🤩', 'Decorator🎉', 'Master👨‍🎓',
         'Wizard🧙‍♂️', 'Connoisseur👑', 'Emperor🤴', 'God🙌']
HELP = """
ℹ️ INFORMATION ℹ️

<code>|Send wallpaper✉️|</code> - <i>using this button you can send for moderation your wallpapers</i>
-----------------------
<code>|My stats📈|</code> - <i>find out how many wallpapers you've sent, how many have been posted to the channel, \
 and your current rank!</i>
-----------------------
<code>|Top 5 wallpaperists🏆|</code> - <i>stats of top 5 best users</i>
-----------------------
<code>|/menu|</code> - <i>button that send you message with available buttons</i>
-----------------------
<code>|/info|</code> - <i>button that send you message with info about available actions</i>
"""
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
