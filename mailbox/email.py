from email import message_from_bytes
import email.header
import os
import re
import datetime
import calendar


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
        self.__data = message_from_bytes(data)
        self.byte = data
        self.num = num

    @property
    def from_addr(self):
        if not self.__data['From']:
            return ""
        return str(email.header.make_header(email.header.decode_header(self.__data['From'])))

    @property
    def date(self):
        if not self.__data['Date']:
            return datetime.datetime(2022, 1, 1)
        date = str(email.header.make_header(email.header.decode_header(self.__data['Date'])))
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
        if not self.__data['Subject']:
            return ""
        return (str(email.header.make_header(email.header.decode_header(self.__data['Subject'])))
                .replace('\n', '')
                .replace('\r', ''))

    @property
    def body(self):
        return self.__get_body(self.__data)

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

    def save_file(self, file_dir: str):
        return self.__get_files(self.__data, file_dir)

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
