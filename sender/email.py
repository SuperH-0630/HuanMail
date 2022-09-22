from time import strftime, localtime

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.header import Header
from email.utils import parseaddr, formataddr


class Email:
    @staticmethod
    def _format_addr(s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))

    def __init__(self, from_addr: tuple, subject: str, to_addr=None, cc_addr=None, bcc_addr=None, subtype="mixed"):
        self.from_addr = from_addr
        self.subject = subject
        self.to_addr = to_addr if to_addr else []
        self.cc_addr = cc_addr if cc_addr else []
        self.bcc_addr = bcc_addr if bcc_addr else []

        self.text = []
        self.html = []
        self.file = []
        self.subtype = subtype

    def add_text(self, text: str):
        self.text.append(text)

    def add_text_from_file(self, path):
        with open(path, "r") as f:
            self.add_text(f.read())

    def add_html(self, html: str):
        self.html.append(html)

    def add_html_from_file(self, path):
        with open(path, "r") as f:
            self.add_html(f.read())

    def add_bytes(self, filename: str, file: bytes):
        self.file.append((filename, file))

    def add_from_file(self, filename, path):
        with open(path, "rb") as f:
            self.add_bytes(filename, f.read())

    def add_to_addr(self, name, email):
        self.to_addr.append((name, email))

    def add_cc_addr(self, name, email):
        self.cc_addr.append((name, email))

    def add_bcc_addr(self, name, email):
        self.bcc_addr.append((name, email))

    def as_msg(self):
        msg = MIMEMultipart(_subtype=self.subtype)
        msg['From'] = self._format_addr(f"{self.from_addr[0]}<{self.from_addr[1]}>")
        msg['To'] = ",".join([self._format_addr(f"{i[0]}<{i[1]}>") for i in self.to_addr])
        msg['Cc'] = ",".join([self._format_addr(f"{i[0]}<{i[1]}>") for i in self.cc_addr])
        msg['Subject'] = Header(self.subject, 'utf-8').encode()
        msg["Date"] = Header(strftime('%a, %d %b %Y %H:%M:%S %z', localtime())).encode()

        for i in self.text:
            msg.attach(MIMEText(i, 'plain', 'utf-8'))
        for i in self.html:
            msg.attach(MIMEText(i, 'html', 'utf-8'))
        for filename, i in self.file:
            msg_file = MIMEApplication(i)
            msg_file.add_header('Content-Disposition', 'attachment', filename=filename)
            msg.attach(msg_file)
        return msg

    def as_string(self):
        return self.as_msg().as_string()
