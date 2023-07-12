import os
import json
import supabase
from dotenv import load_dotenv

from user_class import User

# -------------------------------------START DB, END DB-------------------------------------
load_dotenv()


async def db_start():
    global sb
    sb = supabase.create_client(os.getenv("URL"), os.getenv("KEY"))


async def close():
    sb.auth.close()

# -------------------------------------CREATE PROFILE-------------------------------------


async def create_profile(user_id, username, user_data):
    user = sb.table("user_data").select("user_id").eq("user_id", f"{user_id}").execute().data
    if not user:
        sb.table("user_data").insert({"user_id": f"{user_id}",
                                      "username": f"{username}",
                                      "user_data": f"{user_data.to_json()}"}).execute()


# -------------------------------------EDIT PROFILE-------------------------------------


async def sent_increase(user_id):
    user = await get_user_data(user_id)
    user.increase_sent()
    await update_user_data(user_id, user)


async def posted_increase(user_id):
    user = await get_user_data(user_id)
    user.increase_posted()
    await update_user_data(user_id, user)

# -------------------------------------GETTERS-------------------------------------


async def get_user_data(user_id):
    return User.from_dict(json.loads(sb.table("user_data").select("user_data")
                                     .eq("user_id", user_id).execute().data[0]["user_data"]))


async def get_all_users():
    data = sb.table("user_data").select("*").execute().data
    for user in data:
        if user["user_data"]:
            user_obj = User.from_dict(json.loads(
                sb.table("user_data").select("user_data")
                .eq("user_id", user['user_id']).execute().data[0]["user_data"]))
            user["user_data"] = user_obj
    return data


async def get_ids():
    return sb.table("user_data").select("user_id").execute().data

# -------------------------------------UPDATERS-------------------------------------


async def update_user_data(user_id, user):
    sb.table("user_data").update({"user_data": user.to_json()}).eq("user_id", user_id).execute()

