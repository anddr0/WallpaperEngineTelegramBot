import sqlite3 as sq
from variables import ranks_check


async def db_start():
    global db, cur

    db = sq.connect('users.db')
    cur = db.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS "
                "users(username TEXT PRIMARY KEY, user_id TEXT,"
                "first_name TEXT, num_of_walls INTEGER, posted_wallpapers INTEGER, rank TEXT)")
    db.commit()

# -------------------------------------CREATE PROFILE-------------------------------------


async def create_profile(user_id, username, first_name):
    user = cur.execute("SELECT 1 FROM users WHERE username == '{key}'".format(key=username)).fetchone()
    if not user:
        cur.execute("INSERT INTO users VALUES(?, ?, ?, ?, ?, ?)", (username, user_id, first_name, 0, 0, 'Newbie🔰'))
        db.commit()

# -------------------------------------EDIT PROFILE-------------------------------------


async def edit_posted(username):
    cur.execute("UPDATE users SET posted_wallpapers = posted_wallpapers + 1 WHERE username = '{}'".format(username))
    num = cur.execute("SELECT posted_wallpapers FROM users WHERE username = '{}'".format(username)).fetchone()[0]
    rank = ranks_check(num)
    cur.execute("UPDATE users SET rank = '{}' WHERE username = '{}'".format(rank, username))
    db.commit()


async def edit_num_of_walls(username):
    cur.execute("UPDATE users SET num_of_walls = num_of_walls + 1 WHERE username = '{}'".format(username))
    db.commit()

# -------------------------------------GETTERS-------------------------------------


async def get_top():
    top = cur.execute("SELECT * FROM users").fetchall()
    return top


async def get_stats(username):
    stats = cur.execute("SELECT num_of_walls, posted_wallpapers, rank FROM users WHERE username = '{}'".format(username)).fetchone()
    return stats


async def get_id(username):
    user_id = cur.execute("SELECT user_id FROM users WHERE username = '{}'".format(username)).fetchone()
    return user_id
