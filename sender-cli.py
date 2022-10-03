import smtplib
import json
from cmd import Cmd
from typing import Optional

from sender.email import Email
from sender.smtp import Sender


class CLManager(Cmd):
    intro = 'Welcome to the HuanMail (SMTP).'
    prompt = 'HuanMail>'
    file = None

    def __init__(self):
        super(CLManager, self).__init__()
        self.sender: Optional[Sender] = None
        self.email: Optional[Email] = None

    def do_load(self, path):
        """Load setting from file."""

        try:
            with open(path, "r", encoding="utf-8") as f:
                try:
                    conf = json.load(f)
                    sender = conf.get("sender")
                    if sender:
                        self.sender = Sender(
                            user=sender["user"],
                            passwd=sender["passwd"],
                            host=sender.get("host", "localhost"),
                            port=sender.get("port", 465),
                            debug=sender.get("debug", False),
                            ssl=sender.get("ssl", True),
                            start_ssl=sender.get("start_ssl", False)
                        )

                    email = conf.get("email", {})
                    if input("Load email?[Yes/No]") == "Yes" and email:
                        self.email = Email(
                            from_addr=(email["from_name"], email["from_addr"]),
                            subject=input("Title:")
                        )
                except smtplib.SMTPAuthenticationError:
                    print("Sorry, SMTP Authentication error. Please check your user and password.")
                except smtplib.SMTPException:
                    print("Sorry, SMTP error.")
                except KeyError:
                    print("Key error.")
                except Exception:
                    print("Sorry, Unknown error.")
                else:
                    print("Okay.")
        except FileNotFoundError:
            print("File not fount.")
        except IOError:
            print("IO error.")

    def do_save(self, arg):
        """Save setting to file."""

        conf = {}
        if self.sender:
            conf["sender"] = {}
            conf["sender"]["user"] = self.sender.user
            conf["sender"]["passwd"] = self.sender.passwd
            conf["sender"]["host"] = self.sender.host
            conf["sender"]["port"] = self.sender.port
            conf["sender"]["debug"] = self.sender.debug
            conf["sender"]["ssl"] = self.sender.ssl
            conf["sender"]["start_ssl"] = self.sender.start_ssl

        if input("Save email?[Yes/No]") == "Yes" and self.email:
            conf["email"] = {}
            conf["email"]["from_name"], conf["email"]["from_addr"] = self.email.from_addr

        try:
            with open(arg, "w", encoding="utf-8") as f:
                f.write(json.dumps(conf))
        except FileNotFoundError:
            print("File not found.")
        except IOError:
            print("IO error.")
        else:
            print("Okay.")

    def do_sender(self, arg):
        """sender setting    --    setting the sender.
sender show       --    show sender info.
sender delete     --    delete the sender."""

        if arg == "setting":
            self.sender_setting()
        elif arg == "show":
            self.sender_show()
        elif arg == "delete":
            self.sender_delete()
        else:
            print(f"Bad syntax.")
            return

    def sender_show(self):
        print(f"""Host: {self.sender.host}:{self.sender.port}
User: {self.sender.user}
Passwd: {self.sender.passwd}""")

    def sender_setting(self):
        user = input("User:")
        passwd = input("Passwd:")
        host = input("Host[localhost]:")
        port = input("Port[465]:")
        debug = input("Debug[n]:")
        ssl = input("SSL[y]:")

        if len(host) == 0:
            host = "localhost"

        if len(port) == 0:
            port = 465
        else:
            try:
                port = int(port)
            except (ValueError, TypeError):
                print("Port must be number")
                return

        if len(debug) == 0 or debug == "n":
            debug = False
        else:
            debug = True

        if len(ssl) == 0 or ssl == "y":
            ssl = True
        else:
            ssl = False

        print(f"""Setting sender
Host: {host}:{port}
User: {user}
Passwd: {passwd}
Debug: {debug}
SSL: {ssl}
Sure? [Yes/No]""")

        if input() == "No":
            print("Stop.")
            return

        try:
            self.sender = Sender(user, passwd, host=host, port=port, debug=debug, ssl=ssl)
        except smtplib.SMTPAuthenticationError:
            print("Sorry, SMTP Authentication error. Please check your user and password.")
        except smtplib.SMTPException:
            print("Sorry, SMTP error.")
        except Exception:
            print("Sorry, Unknown error.")
        else:
            print("Okay.")

    def sender_delete(self):
        if input("Sure?[Yes/No]") == "No":
            print("Stop.")
            return

        self.sender = None
        print("Sender has been delete.")

    def do_email(self, arg):
        """email new         --    create a new email.
email delete      --    delete the email.
email text        --    add test to email.
email text-file   --    add text from file to email.
email html        --    add html to email.
email html-file   --    add html from file to email.
email file        --    add a file to email.
email show        --    show the email info."""

        if arg == "new":
            self.email_new()
        else:
            if not self.email:
                print("Please create email first.")
                return

            if arg == "delete":
                self.email_delete()
            elif arg == "text":
                self.email_text()
            elif arg == "text-file":
                self.email_text_file()
            elif arg == "html":
                self.email_html()
            elif arg == "html-file":
                self.email_html_file()
            elif arg == "file":
                self.email_file()
            elif arg == "show":
                self.email_show()
            else:
                print(f"Bad syntax.")

    def email_new(self):
        if self.email and input("Sure?[Yes/No]") == "No":
            print("Stop.")
            return

        from_addr = input("From email address:")
        from_name = input("From name:")
        subject = input("Title:")

        self.email = Email((from_name, from_addr), subject)
        print("Okay.")

    def email_delete(self):
        if input("Sure?[Yes/No]") == "No":
            print("Stop.")
            return

        self.email = None
        print("Okay.")

    def email_text(self):
        self.email.add_text(self.get_text())
        print("Okay.")

    def email_text_file(self):
        try:
            self.email.add_text_from_file(input("Path:"))
        except FileNotFoundError:
            print("File not fount.")
        except IOError:
            print("IO error.")
        else:
            print("Okay.")

    def email_html(self):
        self.email.add_html(self.get_text())
        print("Okay.")

    def email_html_file(self):
        try:
            self.email.add_html_from_file(input("Path:"))
        except FileNotFoundError:
            print("File not fount.")
        except IOError:
            print("IO error.")
        else:
            print("Okay.")

    def email_file(self):
        filename = input("Filename:")
        path = input("Path:")
        try:
            self.email.add_from_file(filename, path)
        except FileNotFoundError:
            print("File not fount.")
        except IOError:
            print("IO error.")
        else:
            print("Okay.")

    def email_show(self):
        print(f"From: {self.email.from_addr[0]} <{self.email.from_addr[1]}>")
        print(f"Title: {self.email.subject}")

        print("* Text: ")
        for i in self.email.text:
            print(i)
            print("-" * 5)

        print("* HTML: ")
        for i in self.email.html:
            print(i)
            print("-" * 5)

        print("* File: ")
        for i in self.email.file:
            print(i[0])

    @staticmethod
    def get_text():
        end = input("End:")
        text = ""
        while True:
            get = input(">>> ")
            if get == end:
                return text[:-1]
            text += get + "\n"

    def do_rc(self, arg):
        """rc add-to    --    add recipient.
rc add-cc    --    add CC person.
rc add-bcc   --    add BCC person.
rc show      --    show recipient, CC person, BCC person."""

        if not self.email:
            print("Please create email first.")
            return

        if arg == "add-to":
            self.rc_add_to()
        elif arg == "add-cc":
            self.rc_add_cc()
        elif arg == "add-bcc":
            self.rc_add_bcc()
        elif arg == "show":
            self.rc_show()
        else:
            print(f"Bad syntax.")

    def rc_add_to(self):
        name = input("Name:")
        email = input("Email:")
        self.email.add_to_addr(name, email)
        print("Okay.")

    def rc_add_cc(self):
        name = input("Name:")
        email = input("Email:")
        self.email.add_cc_addr(name, email)
        print("Okay.")

    def rc_add_bcc(self):
        name = input("Name:")
        email = input("Email:")
        self.email.add_bcc_addr(name, email)
        print("Okay.")

    def rc_show(self):
        print("* Recipient:")
        for name, email in self.email.to_addr:
            print(f"{name} <{email}>")

        print("* CC Person:")
        for name, email in self.email.cc_addr:
            print(f"{name} <{email}>")

        print("* BCC Person:")
        for name, email in self.email.bcc_addr:
            print(f"{name} <{email}>")

    def do_send(self, arg):
        """Send email"""
        if len(arg) != 0:
            print(f"Bad syntax for '{arg}'.")
            return

        if not self.email:
            print("Please create email first.")
            return

        if not self.sender:
            print("Please create sender first.")
            return

        try:
            self.sender.send(self.email)
        except smtplib.SMTPException:
            print("SMTP error.")
        else:
            print("Okay.")

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
