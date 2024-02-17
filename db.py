import datetime
import os
import supabase
from dotenv import load_dotenv
from variables import RANKS

# -------------------------------------START DB, END DB-------------------------------------
load_dotenv()


async def db_start():
    global sb
    sb = supabase.create_client(os.getenv("URL"), os.getenv("KEY"))


async def close():
    sb.auth.close()

# -------------------------------------CREATE PROFILE-------------------------------------


async def create_profile(user_id, username, first_name, language_code):
    user = sb.table("user_data_v2").select("user_id").eq("user_id", f"{user_id}").execute().data
    if not user:
        sb.table("user_data_v2").insert({"user_id": f"{user_id}",
                                         "username": f"{username}",
                                         "first_name": f"{first_name}",
                                         "created": f"{datetime.datetime.now()}",
                                         "last_activity": f"{datetime.datetime.now()}",
                                         "rank": f"{'Newbie🔰'}",
                                         "sent": f"{0}",
                                         "posted": f"{0}",
                                         "language_code": f"{language_code}"}).execute()


# -------------------------------------GETTERS------------------------------------


async def get_top_5():
    return sb.table("user_data_v2").select("*").order("posted", desc=True).limit(5).execute().data

async def get_stats(user_id):
    return sb.table("user_data_v2").select("*").eq("user_id", f"{user_id}").execute().data

async def get_ids():
    return sb.table("user_data_v2").select("user_id").execute().data

# -------------------------------------UPDATERS-------------------------------------


async def sent_increase(user_id):
    sent = sb.table("user_data_v2").select("sent").eq("user_id", user_id).execute().data[0]["sent"]
    sb.table("user_data_v2").update({"sent": sent + 1}).eq("user_id", user_id).execute()


async def posted_increase(user_id):
    posted = sb.table("user_data_v2").select("posted").eq("user_id", user_id).execute().data[0]["posted"]
    sb.table("user_data_v2").update({"posted": posted + 1}).eq("user_id", user_id).execute()
    await rank_update(user_id)


async def activity_update(user_id):
    sb.table("user_data_v2").update({"last_activity": f"{datetime.datetime.now()}"}).eq("user_id", user_id).execute()


async def rank_update(user_id):
    posted = sb.table("user_data_v2").select("posted").eq("user_id", f"{user_id}").execute().data[0]["posted"]
    if posted in range(5):
        rank = RANKS[0]
    elif posted in range(5, 10):
        rank = RANKS[1]
    elif posted in range(10, 20):
        rank = RANKS[2]
    elif posted in range(20, 30):
        rank = RANKS[3]
    elif posted in range(30, 40):
        rank = RANKS[4]
    elif posted in range(40, 50):
        rank = RANKS[5]
    elif posted in range(50, 70):
        rank = RANKS[6]
    elif posted in range(70, 100):
        rank = RANKS[7]
    elif posted in range(100, 150):
        rank = RANKS[8]
    elif posted in range(150, 200):
        rank = RANKS[9]
    else:
        rank = RANKS[10]
    sb.table("user_data_v2").update({"rank": rank}).eq("user_id", user_id).execute()


