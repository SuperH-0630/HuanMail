from email import message_from_bytes
import email.header
import os
import re
import datetime
import calendar


class HTML:
    def __init__(self, body):
        self.body = body
        self.type = "text/html"


class PLAIN:
    def __init__(self, body):
        self.body = body
        self.type = "text/plain"


class Mail:
    date_pattern = re.compile(
        r"[A-Za-z]+, "
        r"([0-9]{1,2}) "
        r"([A-Za-z]+) "
        r"([0-9]{4}) "
        r"([0-9]{1,2}):([0-9]{1,2}):([0-9]{1,2}) "
        r"([\s\S]*)"
    )

    time_zone_pattern = re.compile(r"([+-])([0-9]{2})00")

    def __init__(self, num: str, data: bytes):
        self.__date_ = None
        self.byte = data
        self.num = num

    @property
    def msg_data(self):  # 有需要的时候才加载
        if self.__date_:
            return self.__date_
        self.__date_ = message_from_bytes(self.byte)
        return self.__date_

    @property
    def from_addr(self):
        if not self.msg_data['From']:
            return ""
        return str(email.header.make_header(email.header.decode_header(self.msg_data['From'])))

    @property
    def date(self):
        if not self.msg_data['Date']:
            return datetime.datetime(2022, 1, 1)
        date = str(email.header.make_header(email.header.decode_header(self.msg_data['Date'])))
        res = self.date_pattern.match(str(date)).groups()
        time = datetime.datetime(int(res[2]),
                                 list(calendar.month_abbr).index(res[1]),
                                 int(res[0]),
                                 int(res[3]),
                                 int(res[4]),
                                 int(res[5]))

        timezone = self.time_zone_pattern.match(res[6])
        if timezone:
            if timezone.groups()[0] == '-':
                time += datetime.timedelta(hours=int(timezone.groups()[1]))
            else:
                time -= datetime.timedelta(hours=int(timezone.groups()[1]))
            time += datetime.timedelta(hours=8)  # 转换为北京时间
        return time

    @property
    def title(self):
        if not self.msg_data['Subject']:
            return ""
        return (str(email.header.make_header(email.header.decode_header(self.msg_data['Subject'])))
                .replace('\n', '')
                .replace('\r', ''))

    @property
    def body(self):
        return self.__get_body(self.msg_data)

    def __get_body(self, msg):
        if msg.is_multipart():
            res = ""
            for i in msg.get_payload():
                res += self.__get_body(i)
            return res
        else:
            msg_type = msg.get_content_type()
            if msg_type == "text/plain":
                return "text/plain:\n" + msg.get_payload(decode=True).decode('utf-8') + "\n"
            elif msg_type == "text/html":
                return "text/html:\n" + msg.get_payload(decode=True).decode('utf-8') + "\n"
            else:
                return ""

    @property
    def body_list(self):
        return self.__get_body_list(self.msg_data)

    def __get_body_list(self, msg):
        if msg.is_multipart():
            res = []
            for i in msg.get_payload():
                son = self.__get_body_list(i)
                if son is not None:
                    res += son
            return res
        else:
            msg_type = msg.get_content_type()
            if msg_type == "text/plain":
                return [PLAIN(msg.get_payload(decode=True).decode('utf-8'))]
            elif msg_type == "text/html":
                return [HTML(msg.get_payload(decode=True).decode('utf-8'))]
            else:
                return None

    def save_file(self, file_dir: str):
        return self.__get_files(self.msg_data, file_dir)

    @staticmethod
    def __get_files(msg, file_dir: str):
        create = False
        for part in msg.walk():
            if not create:
                os.makedirs(file_dir, exist_ok=True)
                create = True

            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue
            filename = part.get_filename()

            if filename:
                filepath = os.path.join(file_dir, filename)
                with open(filepath, 'wb') as f:
                    f.write(part.get_payload(decode=True))

    def __lt__(self, other: "Mail"):
        return self.date < other.date

    def __eq__(self, other: "Mail"):
        return self.date == other.date

    def __le__(self, other: "Mail"):
        return self.date <= other.date

    def __str__(self):
        return f"{self.num} {self.title} {self.from_addr} {self.date}"
