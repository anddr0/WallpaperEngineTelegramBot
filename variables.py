from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

PAY_TOKEN = '410694247:TEST:706675bb-1b2b-4f1d-8b6a-2201002ca1f4'
API_TOKEN='6053290916:AAFutZWUeod-FpJnOHb8lW9d_GQJpSt0t50'
MY_ID=840550973
CHANNELS_ID=-1001557123971
WALLS_CHAT=-855257472

RANKS = ['Newbie🔰', 'Wallpaper 🖼', 'Artisan🧑‍🎨', 'Wallpaperist🎨', 'Enthusiast🤩', 'Decorator🎉', 'Master👨‍🎓',
         'Wizard🧙‍♂️', 'Connoisseur👑', 'Emperor🤴', 'God🙌']


def ranks_check(num):
    if num in range(5):
        return RANKS[0]
    elif num in range(5, 10):
        return RANKS[1]
    elif num in range(10, 20):
        return RANKS[2]
    elif num in range(20, 30):
        return RANKS[3]
    elif num in range(30, 40):
        return RANKS[4]
    elif num in range(40, 50):
        return RANKS[5]
    elif num in range(50, 70):
        return RANKS[6]
    elif num in range(70, 100):
        return RANKS[7]
    elif num in range(100, 150):
        return RANKS[8]
    elif num in range(150, 200):
        return RANKS[9]
    else:
        return RANKS[10]


# /start, /help Keyboard
send_button = InlineKeyboardButton(text="Send wallpaper✉️", callback_data="send_wallpaper")
stats_button = InlineKeyboardButton(text="My stats📈", callback_data="stats")
sent_button = InlineKeyboardButton(text="Top 5 ranks🏆", callback_data="top_5")
inline_keyboard = InlineKeyboardMarkup(row_width=2).add(send_button, stats_button, sent_button)

stats_keyboard = InlineKeyboardMarkup().add(stats_button)
