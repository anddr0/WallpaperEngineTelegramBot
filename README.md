# Wallpaper Engine Bot

The Wallpaper Engine Bot is a Telegram bot designed to facilitate the discovery and sharing of wallpapers. Leveraging the Wallpaper Engine's vast collection, this bot provides users with a convenient way to find and share high-quality wallpapers directly through Telegram.

## Features

This is a telegram bot designed to moderate the different kinds of wallpaper offered by users (whether files, photos or videos). The bot has a database in which it stores the ID and username of a particular user and the User object, which is transformed into a BLOB (Binary Large Object) so that it can be stored in the database.

The bot has 3 main buttons: 
- Send wallpaper
- Stats
- Top 5 wallpaperists

Send wallpaper - a button that allows you to send the user wallpaper for moderation. 
Stats - user statistics (Number of uploaded/sent wallpaper, as well as rank). 
Top 5 wallpaperists - stats for the 5 most active members (if there are less members, the stats are less, too)

Also, the bot has 2 'hidden' commands, which can be used only by those users, whose ID is recorded in the MY_ID field (Owner's id in telegram). 
`/send_database (/s_db)` - the bot sends to the chat the actual database, which is operated by the bot. 
`/send_message (/s_m)` - a command that copies the message sent to the bot and sends it to each chat that is in the database (can be used to inform users or for promotional purposes)

## Getting Started

### Prerequisites

- Python 3.8 or newer
- Pip for installing Python packages
- A Telegram Bot Token (obtainable through BotFather on Telegram)
- Supabase URL and KEY

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/wallpaperenginebot.git
cd wallpaperenginebot
```

2. **Set up a virtual environment (optional but recommended)**

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Copy the `.env.example` to `.env` and fill in the necessary details like your Telegram Bot Token and database credentials.

### Running the Bot

To run the bot, execute:

```bash
python bot.py
```

Ensure that your environment variables are correctly set before starting the bot.

## Usage

After starting the bot, you can interact with it through Telegram. Use the `/start` command to initiate the bot and follow the instructions provided.

## Contributing

Contributions to the Wallpaper Engine Bot are welcome. Please feel free to fork the repository, make changes, and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.


