import smtplib

from .email import Email


class Sender:
    def __init__(self, user: str, passwd: str, host="localhost", port=465, debug=False, ssl=True, start_ssl=False):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.debug = debug
        self.ssl = ssl
        self.start_ssl = False if ssl else start_ssl

    def send(self, msg: Email):
        if self.ssl:
            server = smtplib.SMTP_SSL(self.host, self.port)
        else:
            server = smtplib.SMTP(self.host, self.port)
        server.set_debuglevel(self.debug)
        if self.start_ssl:
            server.starttls()
        server.login(self.user, self.passwd)
        server.sendmail(msg.from_addr[1],
                        [i[1] for i in msg.to_addr + msg.cc_addr + msg.bcc_addr],
                        msg.as_string())
        server.quit()

    def check_login(self):
        if self.ssl:
            server = smtplib.SMTP_SSL(self.host, self.port)
        else:
            server = smtplib.SMTP(self.host, self.port)
        server.set_debuglevel(self.debug)
        if self.start_ssl:
            server.starttls()

        try:
            server.login(self.user, self.passwd)
            server.quit()
        except (smtplib.SMTPHeloError, smtplib.SMTPAuthenticationError,
                smtplib.SMTPNotSupportedError, smtplib.SMTPException):
            return False
        return True
