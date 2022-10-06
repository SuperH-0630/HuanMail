import tkinter as tk
import tkinter.messagebox as msg
import tkinter.filedialog as fd
import tkinter.scrolledtext as st
import json
import imaplib
from typing import Optional, List
from time import strftime, localtime, strptime

from mailbox.email import Mail
from mailbox.imap import Imap

# 顶层Frame
FRAME_PADX = 5

# 顶层窗口按钮
BUTTON_WIDTH = 40
BUTTON_WIDTH_L = 20
BUTTON_HEIGHT = 1
MAILBOX_WIDTH = 60
MAILBOX_HEIGHT = 5

# 登录框
LOGIN_LABEL_WIDTH = 10
LOGIN_LABEL_HEIGHT = 1
LOGIN_ENTRY_WIDTH = 35
LOGIN_BTN_WIDTH = 20
LOGIN_RBTN_WIDTH = 6
LOGIN_MAILBOX_WIDTH = 45
LOGIN_MAILBOX_HEIGHT = 10

# GET框
GET_LABEL_WIDTH = 10
GET_LABEL_HEIGHT = 1
GET_ENTRY_WIDTH = 35

# refresh框
REFRESH_LABEL_WIDTH = 10
REFRESH_LABEL_HEIGHT = 1
REFRESH_ENTRY_WIDTH = 35

# 邮件信息显示框
EMAIL_INFO_BUTTON_WIDTH = 20
EMAIL_INFO_BUTTON_HEIGHT = 1
EMAIL_INFO_WIDTH = 100
EMAIL_INFO_HEIGHT = 40


class MailboxGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.imap: Optional[Imap] = None

        self.iconbitmap('HuanMail.ico')
        self.title("HuanMail (IMAP)")
        self.resizable(False, False)

        self.btn_frame = tk.Frame(self)
        self.mailbox_frame = tk.Frame(self)
        self.btn_frame.grid(column=0, row=0)
        self.mailbox_frame.grid(column=1, row=0)

        self.mailbox_num: List[str] = []
        self.mailbox_x = tk.Scrollbar(self.mailbox_frame, orient=tk.HORIZONTAL)
        self.mailbox_y = tk.Scrollbar(self.mailbox_frame)
        self.mailbox = tk.Listbox(self.mailbox_frame,
                                  xscrollcommand=self.mailbox_x.set, yscrollcommand=self.mailbox_y.set,
                                  width=MAILBOX_WIDTH, height=MAILBOX_HEIGHT)
        self.mailbox_x.config(command=self.mailbox.xview)
        self.mailbox_y.config(command=self.mailbox.yview)

        self.mailbox.grid(column=0, row=0, ipady=38)
        self.mailbox_x.grid(column=0, row=1, sticky="NEWS")
        self.mailbox_y.grid(column=1, row=0, sticky="NEWS")

        self.login_frame = tk.Frame(self.btn_frame)
        self.mailbox_frame = tk.Frame(self.btn_frame)
        self.check_frame = tk.Frame(self.btn_frame)
        self.config_frame = tk.Frame(self.btn_frame)
        self.quit_frame = tk.Frame(self.btn_frame)

        for i, frame in enumerate([self.login_frame, self.mailbox_frame, self.check_frame,
                                   self.config_frame, self.quit_frame]):
            frame.grid(column=0, row=i, padx=FRAME_PADX)

        button_arg = dict(width=BUTTON_WIDTH_L, height=BUTTON_HEIGHT, border=2)
        button_big_arg = dict(width=BUTTON_WIDTH, height=BUTTON_HEIGHT, border=2)

        self.login = tk.Button(self.login_frame, text="Login", command=self.show_login, **button_arg)
        self.info = tk.Button(self.login_frame, text="Info", command=self.show_info, **button_arg)

        self.get = tk.Button(self.mailbox_frame, text="Get", command=self.show_get, **button_arg)
        self.refresh = tk.Button(self.mailbox_frame, text="Refresh", command=self.show_refresh, **button_arg)

        self.check = tk.Button(self.check_frame, text="Check", command=self.show_email, **button_big_arg)
        self.check.pack(side="top", pady=2.5, ipadx=8)

        self.load = tk.Button(self.config_frame, text="Load", command=self.load_config, **button_arg)
        self.save = tk.Button(self.config_frame, text="Save", command=self.save_config, **button_arg)

        for i in (self.login, self.info, self.get, self.refresh, self.load, self.save):
            i.pack(side="left", pady=2.5, ipadx=2)

        self.quit_btn = tk.Button(self.quit_frame, text="Quit", command=self.destroy, **button_big_arg)
        self.quit_btn.pack(side="top", pady=2.5, ipadx=8)

    def show_login(self):
        win = tk.Toplevel(self)
        win.title("User Login")
        win.resizable(False, False)

        label_arg = dict(width=LOGIN_LABEL_WIDTH, height=LOGIN_LABEL_HEIGHT)
        entry_arg = dict(width=LOGIN_ENTRY_WIDTH)

        host_frame = tk.Frame(win)
        host_label = tk.Label(host_frame, text="Host: ", **label_arg)
        host = tk.Entry(host_frame, **entry_arg)
        host_label.pack(side="left")
        host.pack(side="left")
        host_frame.pack(side="top", pady=2, padx=5)

        port_frame = tk.Frame(win)
        port_label = tk.Label(port_frame, text="Port: ", **label_arg)
        port = tk.Entry(port_frame, **entry_arg)
        port_label.pack(side="left")
        port.pack(side="left")
        port_frame.pack(side="top", pady=2, padx=5)

        user_frame = tk.Frame(win)
        user_label = tk.Label(user_frame, text="User: ", **label_arg)
        user = tk.Entry(user_frame, **entry_arg)
        user_label.pack(side="left")
        user.pack(side="left")
        user_frame.pack(side="top", pady=2, padx=5)

        passwd_frame = tk.Frame(win)
        passwd_label = tk.Label(passwd_frame, text="Passwd: ", **label_arg)
        passwd = tk.Entry(passwd_frame, **entry_arg)
        passwd_label.pack(side="left")
        passwd.pack(side="left")
        passwd_frame.pack(side="top", pady=2, padx=5)

        ssl_frame = tk.Frame(win)
        ssl_label = tk.Label(ssl_frame, text="SSL: ", **label_arg)
        ssl = tk.IntVar(ssl_frame)
        ssl.set(1)
        ssl_btn = (tk.Radiobutton(ssl_frame, variable=ssl, value=1, text="No", width=LOGIN_RBTN_WIDTH),
                   tk.Radiobutton(ssl_frame, variable=ssl, value=2, text="SSL", width=LOGIN_RBTN_WIDTH),
                   tk.Radiobutton(ssl_frame, variable=ssl, value=3, text="StartSSL", width=LOGIN_RBTN_WIDTH))
        ssl_label.pack(side="left")
        for i in ssl_btn:
            i.pack(side="left")
        ssl_frame.pack(side="top", pady=2, padx=5)

        login_btn = tk.Button(win, text="Login", width=LOGIN_BTN_WIDTH,
                              command=lambda: self.login_user(host.get(), port.get(), user.get(), passwd.get(),
                                                              ssl.get(), mailbox_list))
        login_btn.pack(side="top", pady=2)

        mailbox_list = tk.Listbox(win, width=LOGIN_MAILBOX_WIDTH, height=LOGIN_MAILBOX_HEIGHT)
        mailbox_list.pack(side="top", pady=(20, 2), padx=5)
        self.refresh_mailbox(mailbox_list)

        select_btn = tk.Button(win, text="Select", width=LOGIN_BTN_WIDTH,
                               command=lambda: self.select_mailbox(mailbox=mailbox_list))
        select_btn.pack(side="top", pady=2)

    def refresh_mailbox(self, mailbox: tk.Listbox):
        if self.imap:
            mailbox.delete("0", tk.END)
            for i in self.imap.list():
                mailbox.insert(tk.END, f"{i}")

    def login_user(self, host, port, user, passwd, ssl: int, listbox):
        try:
            port = int(port)
        except (TypeError, ValueError):
            msg.showerror("Login error", "Port must be int.")
            return

        if ssl == 1:
            ssl = False
            start_ssl = False
        elif ssl == 2:
            ssl = True
            start_ssl = False
        else:
            ssl = False
            start_ssl = True

        try:
            self.imap = Imap(user, passwd, host=host, port=port, ssl=ssl, start_ssl=start_ssl)
            self.imap.connect()
            self.imap.disconnect()
        except imaplib.IMAP4.erro:
            msg.showerror("Login error", "Sorry, IMAP Authentication error. Please check your user and password.")
        except Exception:
            msg.showerror("Login error", "Sorry, Unknown error.")
        else:
            self.refresh_mailbox(listbox)
            msg.showinfo("Login", "Success!")

    def select_mailbox(self, mailbox: tk.Listbox):
        try:
            index = mailbox.curselection()
            if len(index) != 1:
                msg.showwarning("Select", "Please select a mailbox.")
                return

            self.imap.inbox = mailbox.get(index[0])
        except imaplib.IMAP4.error:
            msg.showerror("Select error", "Bad mailbox.")
        else:
            msg.showinfo("Select", "Success!")

    def show_info(self):
        if self.imap:
            msg.showinfo("Info", f"""Host: {self.imap.host}:{self.imap.port}
User: {self.imap.user}
Passwd: {self.imap.passwd}
SSL: {self.imap.ssl}
MailBox: {self.imap.inbox}""")
        else:
            msg.showwarning("Not login", "You should login first.")

    def show_get(self):
        win = tk.Toplevel(self)
        win.title("User Login")
        win.resizable(False, False)

        label_arg = dict(width=GET_LABEL_WIDTH, height=GET_LABEL_HEIGHT)
        entry_arg = dict(width=GET_ENTRY_WIDTH)

        date_frame = tk.Frame(win)
        date_label = tk.Label(date_frame, text="Date: ", **label_arg)
        date = tk.Entry(date_frame, **entry_arg)
        date_label.pack(side="left")
        date.pack(side="left")
        date_frame.pack(side="top", pady=2, padx=5)

        get_btn = tk.Button(win, text="Get", width=LOGIN_BTN_WIDTH,
                            command=lambda: self.get_mail(date.get()))
        get_btn.pack(side="top", pady=2)

    def get_mail(self, date):
        if not self.imap:
            msg.showwarning("Not login", "You should login first.")
            return

        if date == "ALL":
            pass
        elif date == "TODAY":
            date = "ON " + strftime('%d-%b-%Y', localtime())
        else:
            try:
                date = "ON " + strftime('%d-%b-%Y', strptime(date, "%Y-%m-%d"))
            except ValueError:
                msg.showerror("Get error", "Bad date.")
                return

        if not msg.askyesno("Sure", "Sure to load the mail from the server?\nYou should wait a moment."):
            return

        try:
            self.imap.fetch_all(date)
        except imaplib.IMAP4.error:
            msg.showerror("Get error", "IMAP4 error, please check setting.")
        else:
            msg.showinfo("Get", "Success!")

    def show_refresh(self):
        win = tk.Toplevel(self)
        win.title("User Login")
        win.resizable(False, False)

        label_arg = dict(width=REFRESH_LABEL_WIDTH, height=REFRESH_LABEL_HEIGHT)
        entry_arg = dict(width=REFRESH_ENTRY_WIDTH)

        start_frame = tk.Frame(win)
        start_label = tk.Label(start_frame, text="Start: ", **label_arg)
        start = tk.Entry(start_frame, **entry_arg)
        start_label.pack(side="left")
        start.pack(side="left")
        start_frame.pack(side="top", pady=2, padx=5)

        step_frame = tk.Frame(win)
        step_label = tk.Label(step_frame, text="Step: ", **label_arg)
        step = tk.Entry(step_frame, **entry_arg)
        step_label.pack(side="left")
        step.pack(side="left")
        step_frame.pack(side="top", pady=2, padx=5)

        get_btn = tk.Button(win, text="Refresh", width=LOGIN_BTN_WIDTH,
                            command=lambda: self.refresh_mail(start.get(), step.get()))
        get_btn.pack(side="top", pady=2)

    def refresh_mail(self, start, step):
        if not self.imap:
            msg.showwarning("Not login", "You should login first.")
            return

        try:
            start = int(start)
            step = int(step)
        except (TypeError, ValueError):
            msg.showerror("refresh error", "Port must be int.")
            return

        try:
            self.mailbox.delete("0", tk.END)
            self.mailbox_num = []

            mailbox = self.imap.mailbox[start:]
            count = 0
            for i in mailbox:
                self.mailbox.insert(tk.END, f"{i}")
                self.mailbox_num.append(i.num)
                count += 1
                if count == step:
                    break
        except IndexError:
            msg.showerror("Refresh error", "Bad Index.")

    def show_email(self):
        index: tuple = self.mailbox.curselection()
        if len(index) != 1:
            msg.showwarning("Check", "Please select a email.")
            return
        else:
            index: int = index[0]

        if not self.imap:
            msg.showwarning("Not login", "You should login first.")
            return

        email: Mail = self.imap.get_mail(self.mailbox_num[index])
        win = tk.Toplevel(self)
        win.title("Email info")
        win.resizable(False, False)

        arg = dict(width=EMAIL_INFO_WIDTH)
        from_addr = tk.Label(win, text=f"From: {email.from_addr}", **arg)
        title = tk.Label(win, text=f"Title: {email.title}", **arg)
        info = st.ScrolledText(win, height=EMAIL_INFO_HEIGHT, state=tk.DISABLED, **arg)
        btn_frame = tk.Frame(win)

        for i in (from_addr, title, info, btn_frame):
            i.pack(side="top", pady=2.5, ipadx=8, padx=2)

        button_arg = dict(width=EMAIL_INFO_BUTTON_WIDTH, height=EMAIL_INFO_BUTTON_HEIGHT, border=2)
        source = tk.Button(btn_frame, text="Source", command=lambda: self.save_email_source(email), **button_arg)
        save = tk.Button(btn_frame, text="Save", command=lambda: self.save_email(email), **button_arg)
        file = tk.Button(btn_frame, text="File", command=lambda: self.save_file(email), **button_arg)

        for i in (source, save, file):
            i.pack(side="left", ipadx=0.5)

        self.show_email_text(info, email)

    @staticmethod
    def show_email_text(text: st.ScrolledText, email: Mail):
        text.config(state=tk.NORMAL)
        text.delete("0.0", tk.END)
        text.insert(tk.END, email.body)
        text.config(state=tk.DISABLED)

    @staticmethod
    def save_email_source(email: Mail):
        file = None
        try:
            file = fd.asksaveasfile(mode="wb", title="Saving email source", filetypes=[("Email", ".email")],
                                    defaultextension=".email")
            if file is not None:
                file.write(email.byte)
        except IOError:
            msg.showerror("Save source", "Sorry, IO Error.")
        except Exception:
            msg.showerror("Save source", "Sorry, Unknown error.")
        finally:
            if file:
                file.close()
                msg.showinfo("Saving source", "Success!")

    @staticmethod
    def save_email(email: Mail):
        file = None
        try:
            file = fd.asksaveasfile(mode="w", title="Saving email text", filetypes=[("Text", ".txt")],
                                    defaultextension=".txt")
            if file is not None:
                file.write(email.body)
        except IOError:
            msg.showerror("Save email", "Sorry, IO Error.")
        except Exception:
            msg.showerror("Save email", "Sorry, Unknown error.")
        finally:
            if file:
                file.close()
                msg.showinfo("Saving email", "Success!")

    @staticmethod
    def save_file(email: Mail):
        path = fd.askdirectory(mustexist=True, title="Saving file")
        if path is None:
            return

        try:
            email.save_file(path)
        except IOError:
            msg.showerror("Save file", "Sorry, IO Error.")
        except Exception:
            msg.showerror("Save file", "Sorry, Unknown error.")
        else:
            msg.showinfo("Saving file", "Success!")

    def save_config(self):
        file = None
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
            file = fd.asksaveasfile(mode="w", title="Saving config file", filetypes=[("JSON", ".json")],
                                    defaultextension=".json")
            if file is not None:
                file.write(json.dumps(conf))
        except IOError:
            msg.showerror("Load config", "Sorry, IO Error.")
        except Exception:
            msg.showerror("Load config", "Sorry, Unknown error.")
        finally:
            if file:
                file.close()
                msg.showinfo("Saving success", "Success!")

    def load_config(self):
        file = None

        try:
            file = fd.askopenfile(mode="r", title="Loading config file", filetypes=[("JSON", ".json")])
            if file is None:
                return

            conf = json.load(file)
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
        except imaplib.IMAP4.error:
            msg.showerror("Load config", "Sorry, IMAP Authentication error. Please check your user and password.")
        except KeyError:
            msg.showerror("Load config", "Sorry, Key Error.")
        except IOError:
            msg.showerror("Load config", "Sorry, IO Error.")
        except Exception:
            msg.showerror("Load config", "Sorry, Unknown error.")
        finally:
            if file:
                file.close()
                msg.showinfo("Loading success", "Success!")


if __name__ == '__main__':
    window = MailboxGUI()
    window.mainloop()
