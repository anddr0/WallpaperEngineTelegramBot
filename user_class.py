import datetime
from variables import RANKS


class User:
    def __init__(self, first_name="", rank="Newbie🔰", sent_walls=0, posted_walls=0, language_code="en"):
        self.first_name = first_name
        self.create_date = datetime.datetime.now()
        self.last_activity_date = datetime.datetime.now()
        self.rank = rank
        self.sent_walls = sent_walls
        self.posted_walls = posted_walls
        self.language_code = language_code

    def increase_posted(self):
        self.posted_walls += 1
        self.user_update()

    def increase_sent(self):
        self.sent_walls += 1
        self.user_update()

    def rank_update(self):
        if self.posted_walls in range(5):
            self.rank = RANKS[0]
        elif self.posted_walls in range(5, 10):
            self.rank = RANKS[1]
        elif self.posted_walls in range(10, 20):
            self.rank = RANKS[2]
        elif self.posted_walls in range(20, 30):
            self.rank = RANKS[3]
        elif self.posted_walls in range(30, 40):
            self.rank = RANKS[4]
        elif self.posted_walls in range(40, 50):
            self.rank = RANKS[5]
        elif self.posted_walls in range(50, 70):
            self.rank = RANKS[6]
        elif self.posted_walls in range(70, 100):
            self.rank = RANKS[7]
        elif self.posted_walls in range(100, 150):
            self.rank = RANKS[8]
        elif self.posted_walls in range(150, 200):
            self.rank = RANKS[9]
        else:
            self.rank = RANKS[10]

    def user_update(self):
        self.rank_update()
        self.last_activity_date = datetime.datetime.now()

    def get_stats(self):
        self.user_update()
        return self.first_name, self.rank, str(self.sent_walls), str(self.posted_walls), \
               self.create_date, self.last_activity_date, self.language_code

    def __repr__(self):
        return f"First name: {self.first_name} | Rank: {self.rank}" \
               f" | Sent wallpapers: {str(self.sent_walls)} | Posted wallpapers: {str(self.posted_walls)}" \
               f" | Created: {self.create_date.date()} | Last activity: {self.last_activity_date.date()}" \
               f" | Language code: {self.language_code}"