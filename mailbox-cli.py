import json
import imaplib
from cmd import Cmd
from typing import Optional
import os
from time import strftime, localtime, strptime

from mailbox.email import Mail
from mailbox.imap import Imap


class CLManager(Cmd):
    intro = 'Welcome to the HuanMail (IMAP).'
    prompt = 'HuanMail>'
    file = None

    def __init__(self):
        super(CLManager, self).__init__()
        self.imap: Optional[Imap] = None

    def do_load(self, path):
        """Load setting from file."""

        try:
            with open(path, "r", encoding="utf-8") as f:
                try:
                    conf = json.load(f)
                    imap = conf.get("imap")
                    if imap:
                        self.imap = Imap(
                            user=imap["user"],
                            passwd=imap["passwd"],
                            host=imap.get("host", "localhost"),
                            port=imap.get("port", 465),
                            ssl=imap.get("ssl", True),
                            start_ssl=imap.get("start_ssl", False)
                        )

                        self.imap.connect()
                        self.imap.disconnect()

                        self.imap.inbox = imap.get("inbox", "INBOX")
                        mailbox = imap.get("mailbox", {})
                        for num in imap.get("mailbox", {}):
                            byte: str = mailbox[num]
                            self.imap.add_mail(num, byte.encode("utf-8"))
                except KeyError:
                    print("Key error.")
                except imaplib.IMAP4.error:
                    print("Sorry, IMAP Authentication error. Please check your user and password.")
                except Exception:
                    print("Sorry, Unknown error.")
                else:
                    print("Okay.")
        except FileNotFoundError:
            print("File not fount.")
        except IOError:
            print("IO error.")

    def do_save(self, path):
        """Save setting to file."""

        conf = {}
        if self.imap:
            conf["imap"] = {}
            conf["imap"]["user"] = self.imap.user
            conf["imap"]["passwd"] = self.imap.passwd
            conf["imap"]["host"] = self.imap.host
            conf["imap"]["port"] = self.imap.port
            conf["imap"]["ssl"] = self.imap.ssl
            conf["imap"]["start_ssl"] = self.imap.start_ssl
            conf["imap"]["inbox"] = self.imap.inbox
            
            mailbox = {}
            for i in self.imap.mailbox:
                byte: bytes = i.byte
                mailbox[i.num] = byte.decode("utf-8")

            conf["imap"]["mailbox"] = mailbox

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(json.dumps(conf))
        except FileNotFoundError:
            print("File not found.")
        except IOError:
            print("IO error.")
        else:
            print("Okay.")

    def do_login(self, arg):
        """Login imap server."""
        if len(arg) != 0:
            print("Bad syntax.")
            return

        user = input("User:")
        passwd = input("Passwd:")
        host = input("Host[localhost]:")
        port = input("Port[993]:")
        ssl = input("SSL[y]:")

        if len(host) == 0:
            host = "localhost"

        if len(port) == 0:
            port = 993
        else:
            try:
                port = int(port)
            except (ValueError, TypeError):
                print("Port must be number")
                return

        if len(ssl) == 0 or ssl == "y":
            ssl = True
        else:
            ssl = False

        print(f"""Login imap
Host: {host}:{port}
User: {user}
Passwd: {passwd}
SSL: {ssl}
Sure? [Yes/No]""")

        if input() == "No":
            print("Stop.")
            return

        try:
            self.imap = Imap(user, passwd, host=host, port=port, ssl=ssl)
            self.imap.connect()
            self.imap.disconnect()
        except imaplib.IMAP4.error:
            print("Sorry, IMAP Authentication error. Please check your user and password.")
        except Exception:
            print("Sorry, Unknown error.")
        else:
            print("Okay.")

    def do_logout(self, arg):
        """Logout imap server."""
        if len(arg) != 0:
            print("Bad syntax.")
            return

        if input("Sure?[Yes/No]") == "No":
            print("Stop.")
            return

        self.imap = None
        print("Okay.")

    def do_info(self, arg):
        """Show imap info."""

        if len(arg) != 0:
            print("Bad syntax.")
            return

        if self.imap:
            print(f"""Host: {self.imap.host}:{self.imap.port}
User: {self.imap.user}
Passwd: {self.imap.passwd}
SSL: {self.imap.ssl}
MailBox: {self.imap.inbox}""")
        else:
            print("Not login.")

    def do_get(self, arg):
        """Get mail from mailbox."""

        if not self.imap:
            print("Please login first.")
            return

        if arg == "ALL":
            pass
        elif arg == "TODAY":
            arg = "ON " + strftime('%d-%b-%Y', localtime())
        else:
            try:
                arg = "ON " + strftime('%d-%b-%Y', strptime(arg, "%Y-%m-%d"))
            except ValueError:
                print("Bad syntax.")
                return

        print("Please wait...")
        try:
            self.imap.fetch_all(arg)
        except imaplib.IMAP4.error:
            print("IMAP4 error, please check setting.")
        else:
            print("Okay.")

    def do_show(self, arg):
        """Show Mail List"""

        try:
            start, step = arg.split()
            start = int(start)
            step = int(step)
        except (TypeError, ValueError):
            print("Bad syntax.")
            return

        if not self.imap:
            print("Please login first.")
            return

        try:
            mailbox = self.imap.mailbox[start:]
            count = 0
            for i in mailbox:
                print(f"* {i}")
                count += 1
                if count == step:
                    break
        except IndexError:
            print("Bad index.")
        else:
            print("Okay.")

    def do_check(self, arg):
        """check        ---    check mail text.
check save   ---    check mail text and save.
check source ---    check mail source and save.
check file   ---    check mail file and save."""

        if not self.imap:
            print("Please login first.")
            return

        num = input("Mail number:")
        mail = self.imap.fetch(num)

        if len(arg) == 0:
            self.check(mail)
        elif arg == "save":
            self.check_save(mail)
        elif arg == "source":
            self.check_source(mail)
        elif arg == "file":
            self.check_file(mail)
        else:
            print(f"Bad syntax.")

    @staticmethod
    def __print_check(mail: Mail):
        print(f"Title: {mail.title}")
        print(f"From: {mail.from_addr}")
        print(f"Date: {mail.date}")

    @staticmethod
    def check(mail: Mail):
        CLManager.__print_check(mail)
        print(f"\n{mail.body}\n")

    @staticmethod
    def check_save(mail: Mail):
        CLManager.__print_check(mail)
        path = input("Path:")
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(mail.body)
        except IOError:
            print("IO error.")
        else:
            print("Okay.")

    @staticmethod
    def check_source(mail: Mail):
        CLManager.__print_check(mail)
        path = input("Path:")
        try:
            with open(path, "wb") as f:
                f.write(mail.byte)
        except IOError:
            print("IO error.")
        else:
            print("Okay.")

    def check_file(self, mail: Mail):
        path = input("Path:")
        os.makedirs(path, exist_ok=True)

        try:
            mail.save_file(path)
        except IOError:
            print("IO error.")
        else:
            print("Okay.")

    def do_mailbox(self, arg):
        """mail show    ---    show all mailbox.
mail setting ---    select a mailbox."""
        if not self.imap:
            print("Please login first.")
            return

        if arg == "show":
            for i in self.imap.list():
                print(f"* {i}")
            print("Okay")
        elif arg == "setting":
            mailbox = input("Mailbox:")
            try:
                self.imap.inbox = mailbox
            except imaplib.IMAP4.error:
                print("Bad mailbox.")
            else:
                print("Okay")
        else:
            print("Bad syntax.")

    def do_quit(self, _):
        """Exit HuanMail."""

        print("Bye~")
        if self.file:
            self.file.close()
            self.file = None
        return True


if __name__ == '__main__':
    manager = CLManager()
    try:
        manager.cmdloop()
    except KeyboardInterrupt:
        print("\nBye~")
        quit(0)
