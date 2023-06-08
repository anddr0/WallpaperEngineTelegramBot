import sqlite3 as sq
from pickle import dumps, loads

# -------------------------------------START DB, END DB-------------------------------------


async def db_start():
    global db, cur

    db = sq.connect('users.db')
    cur = db.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS "
                "users(user_id INTEGER PRIMARY KEY, username TEXT, user_data BLOB)")
    db.commit()


async def close():
    db.close()

# -------------------------------------CREATE PROFILE-------------------------------------


async def create_profile(user_id, username, user_data):
    user = cur.execute(f"SELECT 1 FROM users WHERE user_id == '{user_id}'").fetchone()
    if not user:
        cur.execute("INSERT INTO users VALUES(?, ?, ?)", (user_id, username, dumps(user_data)))
        db.commit()

# -------------------------------------EDIT PROFILE-------------------------------------


async def sent_increase(user_id):
    user = await get_user_data(user_id)
    user.increase_sent()
    await update_user_data(user_id, user)
    db.commit()


async def posted_increase(user_id):
    user = await get_user_data(user_id)
    user.increase_posted()
    await update_user_data(user_id, user)
    db.commit()

# -------------------------------------GETTERS-------------------------------------


async def get_user_data(user_id):
    return loads(cur.execute(f"SELECT user_data FROM users WHERE user_id = '{user_id}'").fetchone()[0])


async def get_all_users():
    user_id_name = cur.execute(f"SELECT user_id, username FROM users").fetchall()
    user_data = cur.execute(f"SELECT user_data FROM users").fetchall()
    users = []
    for i in range(len(user_id_name)):
        users.append((user_id_name[i][0], user_id_name[i][1], loads(user_data[i][0])))
    return users


async  def get_ids():
    return cur.execute(f"SELECT user_id FROM users").fetchall()

# -------------------------------------UPDATERS-------------------------------------


async def update_user_data(user_id, user):
    cur.execute(f"UPDATE users SET user_data = ? WHERE user_id = ?", (dumps(user), user_id))
    db.commit()
