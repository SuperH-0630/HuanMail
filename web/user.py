from sender.smtp import Sender
from sender.email import Email
from mailbox.imap import Imap
from mailbox.email import Mail
from .db import redis
from .configure import conf

from flask_login import UserMixin
from threading import Thread
from .logger import Logger


EXPIRE = conf["REDIS_EXPIRE"]


class User(UserMixin):
    def __init__(self, username, passwd=None):
        self.id = username
        self.username = username

        if passwd:
            redis.hmset(f"user:{username}", {"passwd": passwd})

    @property
    def smtp_address(self):
        return conf["SMTP_USERNAME"].format(self.username)

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
            Logger.print_user_opt_success_log("imap check login")
            return False

        if not sender.check_login():
            Logger.print_user_opt_success_log("smtp check login")
            return False

        Logger.print_user_opt_success_log("check login")
        return True

    @property
    def info(self):
        return redis.hgetall(f"user:{self.username}")

    @property
    def passwd(self):
        return self.info.get("passwd", "123456789")

    class DownloadMail(Thread):
        def __init__(self, username, passwd, inbox, date):
            super(User.DownloadMail, self).__init__()

            self.imap = Imap(user=conf["IMAP_USERNAME"].format(username),
                             passwd=conf["IMAP_PASSWD"].format(passwd),
                             host=conf["IMAP_HOST"],
                             port=conf["IMAP_PORT"],
                             ssl=conf["IMAP_SSL"],
                             start_ssl=conf["IMAP_START_SSL"])
            self.username = username
            self.imap.inbox = inbox
            self.date = date
            self.inbox = inbox

        def run(self):
            try:
                for i in redis.keys(f"mailbox:{self.username}:{self.inbox}:{self.date}:*"):
                    num = i.split(":")[-1]
                    byte = redis.get(i)
                    if byte:  # 避免在keys和get之前键过期
                        self.imap.add_mail(num, byte.encode("utf-8"))

                self.imap.fetch_all(f"ON {self.date}")

                for i in self.imap.mailbox:
                    name = f"mailbox:{self.username}:{self.inbox}:{self.date}:{i.num}"
                    try:
                        redis.set(name, i.byte)
                    except UnicodeDecodeError:
                        redis.set(name, b"")
                    redis.expire(name, EXPIRE)
            except Exception:
                Logger.print_user_opt_fail_log(f"thread load email")
                raise
            else:
                Logger.print_user_opt_success_log(f"thread load email")
            finally:
                redis.set(f"download:mutex:{self.username}", 0)

    def get_mail_list(self, inbox: str, date: str):
        imap = Imap(user=conf["IMAP_USERNAME"].format(self.username),
                    passwd=conf["IMAP_PASSWD"].format(self.passwd),
                    host=conf["IMAP_HOST"],
                    port=conf["IMAP_PORT"],
                    ssl=conf["IMAP_SSL"],
                    start_ssl=conf["IMAP_START_SSL"])
        imap.inbox = inbox

        for i in redis.keys(f"mailbox:{self.username}:{inbox}:{date}:*"):
            num = i.split(":")[-1]
            byte = redis.get(i)
            if byte:
                imap.add_mail(num, byte.encode("utf-8"))

        if imap.fetch_remote_count(f"ON {date}") != 0:
            # 需要从远程服务器下载资源
            res = redis.incr(f"download:mutex:{self.username}")
            if res != 1:
                return None, False  # 已经有线程
            th = User.DownloadMail(self.username, self.passwd, inbox, date)
            th.start()
            return imap.mailbox, True
        return imap.mailbox, False

    def get_inbox_list(self):
        inbox = redis.lrange(f"inbox:{self.username}", 0, -1)
        if len(inbox) != 0:
            return inbox

        imap = Imap(user=conf["IMAP_USERNAME"].format(self.username),
                    passwd=conf["IMAP_PASSWD"].format(self.passwd),
                    host=conf["IMAP_HOST"],
                    port=conf["IMAP_PORT"],
                    ssl=conf["IMAP_SSL"],
                    start_ssl=conf["IMAP_START_SSL"])

        inbox = imap.list()
        redis.lpush(f"inbox:{self.username}", *inbox)
        redis.expire(f"inbox:{self.username}", EXPIRE)
        return inbox

    def get_mail(self, date, inbox, mail_id):
        name = f"mailbox:{self.username}:{inbox}:{date}:{mail_id}"
        byte = redis.get(name)
        if not byte:
            return None
        redis.expire(name, EXPIRE)
        return Mail(str(mail_id), byte.encode("utf-8"))


    def send(self, email: Email):
        sender = Sender(user=conf["SMTP_USERNAME"].format(self.username),
                        passwd=conf["SMTP_PASSWD"].format(self.passwd),
                        host=conf["SMTP_HOST"],
                        port=conf["SMTP_PORT"],
                        ssl=conf["SMTP_SSL"],
                        start_ssl=conf["SMTP_START_SSL"],
                        debug=False)
        sender.send(email)
        Logger.print_user_opt_success_log("send email")
