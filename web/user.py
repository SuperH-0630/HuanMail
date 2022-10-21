from sender.smtp import Sender
from mailbox.imap import Imap
from .db import redis
from .configure import conf

from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, username, passwd=None):
        self.id = username
        self.username = username

        if passwd:
            redis.hmset(f"user:{username}", {"passwd": passwd})

    def check_login(self):
        imap = Imap(user=conf["IMAP_USERNAME"].format(self.username),
                    passwd=conf["IMAP_PASSWD"].format(self.passwd),
                    host=conf["IMAP_HOST"],
                    port=conf["IMAP_PORT"],
                    ssl=conf["IMAP_SSL"],
                    start_ssl=conf["IMAP_START_SSL"])

        sender = Sender(user=conf["SMTP_USERNAME"].format(self.username),
                        passwd=conf["SMTP_PASSWD"].format(self.passwd),
                        host=conf["SMTP_HOST"],
                        port=conf["SMTP_PORT"],
                        ssl=conf["SMTP_SSL"],
                        start_ssl=conf["SMTP_START_SSL"],
                        debug=False)

        if not imap.check_login():
            return False
        return sender.check_login()

    @property
    def info(self):
        return redis.hgetall(f"user:{self.username}")

    @property
    def passwd(self):
        return self.info.get("passwd", "123456789")
