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


class FILE:
    def __init__(self, filename, byte: bytes, content_type: str, content_disposition: str):
        self.filename = filename
        self.size = len(byte) / 1024 / 1024  # 换算得到mb
        self.content_type = content_type
        self.content_disposition = content_disposition

        if self.size >= 0.1:
            self.size_str = f"{self.size:.2f}MB"
        elif self.size * 1024 > 0.1:
            self.size_str = f"{self.size * 1024:.2f}KB"
        else:
            self.size_str = f"{int(self.size * 1024 * 1024):d}B"



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
    def to_addr(self):
        if not self.msg_data['To']:
            return []
        res = str(email.header.make_header(email.header.decode_header(self.msg_data['To'])))
        return [i.strip() for i in res.split(",")]

    @property
    def cc_addr(self):
        if not self.msg_data['Cc']:
            return []
        res = str(email.header.make_header(email.header.decode_header(self.msg_data['Cc'])))
        return [i.strip() for i in res.split(",")]

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

    @property
    def file_list(self):
        res = []
        for part in self.msg_data.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue

            filename = part.get_filename()
            if filename:
                res.append(FILE(filename, part.get_payload(decode=True),
                                part.get_content_type(), part.get('Content-Disposition')))
        return res

    def get_file(self, filename) -> "(bytes, str, str) | (None, None, None)":
        for part in self.msg_data.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue

            if filename == part.get_filename():
                return part.get_payload(decode=True), part.get_content_type(), part.get('Content-Disposition')
        return None, None, None

    def __lt__(self, other: "Mail"):
        return self.date < other.date

    def __eq__(self, other: "Mail"):
        return self.date == other.date

    def __le__(self, other: "Mail"):
        return self.date <= other.date

    def __str__(self):
        return f"{self.num} {self.title} {self.from_addr} {self.date}"
