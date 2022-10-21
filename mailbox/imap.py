import imaplib
import re
from typing import List

from .email import Mail


imaplib.Commands['ID'] = 'AUTH'


class Imap:
    def __init__(self, user: str, passwd: str, host="localhost", port=993, ssl=True, start_ssl=False):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.ssl = ssl
        self.start_ssl = False if ssl else start_ssl
        self.server: None | imaplib.IMAP4 = None
        self.__mailbox = {}
        self.__inbox = "INBOX"

    @property
    def inbox(self):
        return self.__inbox

    @inbox.setter
    def inbox(self, inbox):
        self.__inbox = inbox
        self.connect()  # 测试连接
        self.disconnect()
        self.__mailbox = {}

    def connect(self):
        if not self.server:
            if self.ssl:
                self.server = imaplib.IMAP4_SSL(self.host, port=self.port)
            else:
                self.server = imaplib.IMAP4(self.host, port=self.port)
                if self.start_ssl:
                    self.server.starttls()
            self.server.login(self.user, self.passwd)
            args = ("name", "HuanMail", "contact", "songzihuan@song-zh.com", "version", "1.0.0", "vendor", "HuanMail")
            self.server._simple_command('ID', '("' + '" "'.join(args) + '")')
            self.server.select(self.__inbox.encode("utf-7").replace(b"+", b"&").decode("utf-8"))

    def disconnect(self):
        if self.server:
            self.server.logout()
            self.server = None

    def search(self):
        self.connect()
        res = self.__search()
        self.disconnect()
        return res

    def __search(self, opt="ALL"):
        _, data = self.server.search(None, opt)
        return data[0].decode("utf-8").split()

    def list(self):
        self.connect()
        res = self.__list()
        self.disconnect()
        return res

    def __list(self):
        res = []
        mailbox_pattern = re.compile(r"\(.*\) \".*\" \"(.+)\"")
        for i in self.server.list()[1]:
            i: bytes
            mailbox = re.match(mailbox_pattern, i.replace(b"&", b"+").decode("utf-7"))
            if mailbox:
                res.append(mailbox.groups()[0])
        return res

    def fetch(self, num: str) -> Mail:
        self.connect()
        res = self.__fetch(num)
        self.disconnect()
        return res

    def __fetch(self, num: str):
        mail = self.__mailbox.get(num)
        if mail:
            return mail

        _, data = self.server.fetch(num, '(RFC822)')
        mail = Mail(num, data[0][1])
        self.__mailbox[num] = mail
        return mail

    def fetch_all(self, opt="ALL"):
        self.connect()
        for i in self.__search(opt):
            self.__fetch(i)
        self.disconnect()

    def fetch_remote_count(self, opt="ALL"):
        self.connect()
        res = len(set(self.__search(opt)) - set(self.__mailbox.keys()))
        self.disconnect()
        return res

    @property
    def mailbox(self) -> List[Mail]:
        return sorted(self.__mailbox.values(), reverse=True)

    @mailbox.setter
    def mailbox(self, args: dict):
        if type(args) is dict and len(args) == 0:
            self.__mailbox = {}
        else:
            raise ValueError

    def add_mail(self, num: str, data: bytes):
        self.__mailbox[num] = Mail(num, data)

    def get_mail(self, num: str):
        return self.__mailbox.get(num, None)

    def check_login(self):
        try:
            self.connect()
            self.disconnect()
        except imaplib.IMAP4.error:
            return False
        return True
