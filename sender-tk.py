import tkinter as tk
import tkinter.messagebox as msg
import tkinter.filedialog as fd
import tkinter.scrolledtext as st
from typing import Optional
import smtplib
import json
import os.path

from sender.email import Email
from sender.smtp import Sender

# 顶层Frame
FRAME_PADX = 5

# 顶层窗口按钮
BUTTON_WIDTH = 40
BUTTON_WIDTH_L = 20
BUTTON_HEIGHT = 1

# 邮件输入框
TEXT_WIDTH = 40
TEXT_HEIGHT = 20

# 邮件信息显示框
EMAIL_INFO_BUTTON_WIDTH = 20
EMAIL_INFO_BUTTON_HEIGHT = 1
EMAIL_INFO_WIDTH = 100
EMAIL_INFO_HEIGHT = 40

# 登录框
LOGIN_LABEL_WIDTH = 10
LOGIN_LABEL_HEIGHT = 1
LOGIN_ENTRY_WIDTH = 35
LOGIN_BTN_WIDTH = 20
LOGIN_RBTN_WIDTH = 6

# 邮件框
CREATE_LABEL_WIDTH = 15
CREATE_LABEL_HEIGHT = 1
CREATE_ENTRY_WIDTH = 35

# 收件人添加
ADD_RC_LABEL_WIDTH = 10
ADD_RC_LABEL_HEIGHT = 1
ADD_RC_ENTRY_WIDTH = 25
ADD_RC_BUTTON_WIDTH = 10
ADD_RC_BUTTON_HEIGHT = 1
ADD_RC_LISTBOX_WIDTH = 35
ADD_RC_LISTBOX_HEIGHT = 10


class SenderGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.sender: Optional[Sender] = None
        self.email: Optional[Email] = None

        self.iconbitmap('static/HuanMail.ico')
        self.title("HuanMail (SMTP)")
        self.resizable(False, False)

        self.login_frame = tk.Frame(self)
        self.email_create_frame = tk.Frame(self)
        self.add_to_frame = tk.Frame(self)
        self.text_frame = tk.Frame(self)
        self.file_frame = tk.Frame(self)
        self.config_frame = tk.Frame(self)
        self.control_frame = tk.Frame(self)

        for i in (self.login_frame, self.email_create_frame, self.add_to_frame, self.text_frame,
                  self.file_frame, self.config_frame, self.control_frame):
            i.pack(side="top", padx=FRAME_PADX)

        button_arg = dict(width=BUTTON_WIDTH_L, height=BUTTON_HEIGHT, border=2)
        button_big_arg = dict(width=BUTTON_WIDTH, height=BUTTON_HEIGHT, border=2)

        self.login = tk.Button(self.login_frame, text="Login", command=self.show_login, **button_arg)
        self.user_show = tk.Button(self.login_frame, text="Show User", command=self.show_user, **button_arg)

        self.create = tk.Button(self.email_create_frame, text="Create", command=self.show_create, **button_arg)
        self.email_show = tk.Button(self.email_create_frame, text="Show Email", command=self.show_email, **button_arg)

        self.add_to = tk.Button(self.add_to_frame, text="Add Recipient", command=self.show_add_rc, **button_big_arg)

        self.text = st.ScrolledText(self.text_frame, width=TEXT_WIDTH, height=TEXT_HEIGHT)
        self.text_control_frame = tk.Frame(self.text_frame)
        self.add_as_html = tk.Button(self.text_control_frame, text="Add as HTML",
                                     command=self.add_as_html, **button_arg)
        self.add_as_text = tk.Button(self.text_control_frame, text="Add as TEXT",
                                     command=self.add_as_text, **button_arg)
        self.text.pack(side="top")
        self.text_control_frame.pack(side="top")

        self.load = tk.Button(self.config_frame, text="Load", command=self.load_config, **button_arg)
        self.save = tk.Button(self.config_frame, text="Save", command=self.save_config, **button_arg)

        self.send_btn = tk.Button(self.control_frame, text="Send", command=self.send_mail, **button_arg)
        self.quit_btn = tk.Button(self.control_frame, text="Quit", command=self.destroy, **button_arg)

        for i in (self.login, self.user_show, self.create, self.email_show, self.add_as_html,
                  self.add_as_text, self.load, self.save, self.send_btn, self.quit_btn):
            i.pack(side="left", pady=2.5, ipadx=2)
        self.add_to.pack(side="left", pady=2.5, ipadx=8)

        self.add_html = tk.Button(self.file_frame, text="Add HTML From File", command=self.add_html, **button_big_arg)
        self.add_text = tk.Button(self.file_frame, text="Add TEXT From File", command=self.add_text, **button_big_arg)
        self.add_file = tk.Button(self.file_frame, text="Add File", command=self.add_file, **button_big_arg)
        for i in (self.add_html, self.add_text, self.add_file):
            i.pack(side="top", pady=2.5, ipadx=8)

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
                                                              ssl.get(), win=win))
        login_btn.pack(side="top", pady=2)

    def login_user(self, host, port, user, passwd, ssl: int, win=None):
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
            self.sender = Sender(user, passwd, host=host, port=port, debug=False, ssl=ssl, start_ssl=start_ssl)
        except smtplib.SMTPAuthenticationError:
            msg.showerror("Login error", "Sorry, SMTP Authentication error. Please check your user and password.")
        except smtplib.SMTPException:
            msg.showerror("Login error", "Sorry, SMTP error.")
        except Exception:
            msg.showerror("Login error", "Sorry, Unknown error.")
        else:
            if win:
                win.destroy()
            msg.showinfo("Login", "Success!")

    def show_user(self):
        if self.sender:
            msg.showinfo("User",
                         f"""Host: {self.sender.host}:{self.sender.port}
User: {self.sender.user}
Passwd: {self.sender.passwd}""")
        else:
            msg.showwarning("Not login", "You should login first.")

    def show_create(self):
        win = tk.Toplevel(self)
        win.title("Email Create")
        win.resizable(False, False)

        label_arg = dict(width=CREATE_LABEL_WIDTH, height=CREATE_LABEL_HEIGHT)
        entry_arg = dict(width=CREATE_ENTRY_WIDTH)

        from_name_frame = tk.Frame(win)
        from_name_label = tk.Label(from_name_frame, text="From Name: ", **label_arg)
        from_name = tk.Entry(from_name_frame, **entry_arg)
        from_name_label.pack(side="left")
        from_name.pack(side="left")
        from_name_frame.pack(side="top", pady=2, padx=5)

        from_address_frame = tk.Frame(win)
        from_address_label = tk.Label(from_address_frame, text="From Address: ", **label_arg)
        from_address = tk.Entry(from_address_frame, **entry_arg)
        from_address_label.pack(side="left")
        from_address.pack(side="left")
        from_address_frame.pack(side="top", pady=2, padx=5)

        title_frame = tk.Frame(win)
        title_label = tk.Label(title_frame, text="Title: ", **label_arg)
        title = tk.Entry(title_frame, **entry_arg)
        title_label.pack(side="left")
        title.pack(side="left")
        title_frame.pack(side="top", pady=2, padx=5)

        create_btn = tk.Button(win, text="Create", width=LOGIN_BTN_WIDTH,
                               command=lambda: self.create_email(from_name.get(), from_address.get(),
                                                                 title.get(), win=win))
        create_btn.pack(side="top", pady=2)

    def create_email(self, from_name, from_address, title, win=None):
        self.email = Email((from_name, from_address), title)
        if win:
            win.destroy()
        msg.showinfo("Create", "Success!")

    def show_email(self):
        if not self.email:
            msg.showwarning("Not email", "You should create email first.")
            return

        win = tk.Toplevel(self)
        win.title("Email info")
        win.resizable(False, False)

        arg = dict(width=EMAIL_INFO_WIDTH)
        from_addr = tk.Label(win, text=f"From: {self.email.from_addr[0]} <{self.email.from_addr[1]}>", **arg)
        title = tk.Label(win, text=f"Title: {self.email.subject}", **arg)
        info = st.ScrolledText(win, height=EMAIL_INFO_HEIGHT, state=tk.DISABLED, **arg)
        btn_frame = tk.Frame(win)

        for i in (from_addr, title, info, btn_frame):
            i.pack(side="top", pady=2.5, ipadx=8, padx=2)

        button_arg = dict(width=EMAIL_INFO_BUTTON_WIDTH, height=EMAIL_INFO_BUTTON_HEIGHT, border=2)
        text = tk.Button(btn_frame, text="TEXT", command=lambda: self.show_email_text(info), **button_arg)
        html = tk.Button(btn_frame, text="HTML", command=lambda: self.show_email_html(info), **button_arg)
        file = tk.Button(btn_frame, text="FILE", command=lambda: self.show_email_file(info), **button_arg)

        for i in (text, html, file):
            i.pack(side="left", ipadx=0.5)

        self.show_email_text(info)

    def show_email_text(self, text: st.ScrolledText):
        if not self.email:
            msg.showwarning("Not email", "You should create email first.")
            return

        text.config(state=tk.NORMAL)
        text.delete("0.0", tk.END)

        if len(self.email.text) == 0:
            text.insert(tk.END, "Not any TEXT ...")
        else:
            for i in self.email.text:
                text.insert(tk.END, i + "\n")
                text.insert(tk.END, "-" * 5 + "\n")
        text.config(state=tk.DISABLED)

    def show_email_html(self, text: st.ScrolledText):
        if not self.email:
            msg.showwarning("Not email", "You should create email first.")
            return

        text.config(state=tk.NORMAL)
        text.delete("0.0", tk.END)

        if len(self.email.html) == 0:
            text.insert(tk.END, "Not any HTML ...")
        else:
            for i in self.email.html:
                text.insert(tk.END, i + "\n")
                text.insert(tk.END, "-" * 5 + "\n")
        text.config(state=tk.DISABLED)

    def show_email_file(self, text: st.ScrolledText):
        if not self.email:
            msg.showwarning("Not email", "You should create email first.")
            return

        text.config(state=tk.NORMAL)
        text.delete("0.0", tk.END)

        if len(self.email.file) == 0:
            text.insert(tk.END, "Not any FILE ...")
        else:
            for i in self.email.file:
                text.insert(tk.END, i[0] + "\n")
        text.config(state=tk.DISABLED)

    def show_add_rc(self):
        if not self.email:
            msg.showwarning("Not email", "You should create email first.")
            return

        win = tk.Toplevel(self)
        win.title("Add Recipient")
        win.resizable(False, False)

        label_arg = dict(width=ADD_RC_LABEL_WIDTH, height=ADD_RC_LABEL_HEIGHT)
        entry_arg = dict(width=ADD_RC_ENTRY_WIDTH)

        name_frame = tk.Frame(win)
        name_label = tk.Label(name_frame, text="Name: ", **label_arg)
        name = tk.Entry(name_frame, **entry_arg)
        name_label.pack(side="left")
        name.pack(side="left")
        name_frame.pack(side="top", pady=2, padx=5)

        address_frame = tk.Frame(win)
        address_label = tk.Label(address_frame, text="Address: ", **label_arg)
        address = tk.Entry(address_frame, **entry_arg)
        address_label.pack(side="left")
        address.pack(side="left")
        address_frame.pack(side="top", pady=2, padx=5)

        lb = tk.Listbox(win, width=ADD_RC_LISTBOX_WIDTH, height=ADD_RC_LISTBOX_HEIGHT, selectmode=tk.SINGLE)
        lb.pack(side="top", pady=2.5, padx=2)
        self.show_rc(lb)

        btn_frame = tk.Frame(win)
        btn_frame.pack(side="top", pady=2.5, padx=2)

        button_arg = dict(width=ADD_RC_BUTTON_WIDTH, height=ADD_RC_BUTTON_HEIGHT, border=2)
        rc = tk.Button(btn_frame, text="Add RC",
                       command=lambda: self.rc_add_to(name.get(), address.get(), lb), **button_arg)
        cc = tk.Button(btn_frame, text="Add CC",
                       command=lambda: self.rc_add_cc(name.get(), address.get(), lb), **button_arg)
        bcc = tk.Button(btn_frame, text="Add BCC",
                        command=lambda: self.rc_add_bcc(name.get(), address.get(), lb), **button_arg)

        for i in (rc, cc, bcc):
            i.pack(side="left")

    def rc_add_to(self, name, address, lb):
        if self.email:
            if msg.askyesno("Add rc", f"Sure to add {name} <{address}> as rc?"):
                self.email.add_to_addr(name, address)
                self.show_rc(lb)
        else:
            msg.showwarning("Not email", "You should create email first.")

    def rc_add_cc(self, name, address, lb):
        if self.email:
            if msg.askyesno("Add cc", f"Sure to add {name} <{address}> as cc?"):
                self.email.add_cc_addr(name, address)
                self.show_rc(lb)
        else:
            msg.showwarning("Not email", "You should create email first.")

    def rc_add_bcc(self, name, address, lb):
        if self.email:
            if msg.askyesno("Add bcc", f"Sure to add {name} <{address}> as bcc?"):
                self.email.add_bcc_addr(name, address)
                self.show_rc(lb)
        else:
            msg.showwarning("Not email", "You should create email first.")

    def show_rc(self, lb: tk.Listbox):
        lb.delete("0", tk.END)
        if self.email:
            for i in self.email.to_addr:
                lb.insert(tk.END, f"TO: {i[0]} <{i[1]}>")

            for i in self.email.cc_addr:
                lb.insert(tk.END, f"CC: {i[0]} <{i[1]}>")

            for i in self.email.bcc_addr:
                lb.insert(tk.END, f"BCC: {i[0]} <{i[1]}>")
        else:
            msg.showwarning("Not email", "You should create email first.")

    def add_as_text(self):
        if not self.email:
            msg.showwarning("Not email", "You should create email first.")
            return
        if msg.askyesno("Sure?", "Sure to add text?"):
            self.email.add_text(self.text.get("0.0", tk.END))
            self.text.delete("0.0", tk.END)
            msg.showinfo("Add", "Success!")

    def add_as_html(self):
        if not self.email:
            msg.showwarning("Not email", "You should create email first.")
            return
        if msg.askyesno("Sure?", "Sure to add html?"):
            self.email.add_html(self.text.get("0.0", tk.END))
            self.text.delete("0.0", tk.END)
            msg.showinfo("Add", "Success!")

    def add_html(self):
        if not self.email:
            msg.showwarning("Not email", "You should create email first.")
            return
        file = fd.askopenfilename(title="Loading HTML", filetypes=[("HTML", ".html"),
                                                                   ("TXT", ".txt"),
                                                                   ("*", "*")])
        if not file:
            return
        self.email.add_html_from_file(file)
        msg.showinfo("Add", "Success!")

    def add_text(self):
        if not self.email:
            msg.showwarning("Not email", "You should create email first.")
            return
        file = fd.askopenfilename(title="Loading TEXT", filetypes=[("TXT", ".txt"),
                                                                   ("*", "*")])
        if not file:
            return
        self.email.add_text_from_file(file)
        msg.showinfo("Add", "Success!")

    def add_file(self):
        if not self.email:
            msg.showwarning("Not email", "You should create email first.")
            return
        file = fd.askopenfilename(title="Loading FILE", filetypes=[("*", "*")])
        if not file:
            return
        self.email.add_from_file(os.path.split(file)[1], file)
        msg.showinfo("Add", "Success!")

    def save_config(self):
        file = None
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
        except smtplib.SMTPAuthenticationError:
            msg.showerror("Load config", "Sorry, SMTP Authentication error. Please check your user and password.")
        except smtplib.SMTPException:
            msg.showerror("Load config", "Sorry, SMTP Error.")
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

    def send_mail(self):
        if not self.sender:
            msg.showwarning("Not login", "You should login first.")
            return

        if not self.email:
            msg.showwarning("Not email", "You should create email first.")
            return

        try:
            self.sender.send(self.email)
            msg.showinfo("Send email", "Success!")
        except smtplib.SMTPException:
            msg.showerror("Send fail", "SMTP error.")


if __name__ == '__main__':
    window = SenderGUI()
    window.mainloop()
