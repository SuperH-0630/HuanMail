from flask import Blueprint, render_template, request, flash, abort
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, SubmitField
from wtforms.validators import DataRequired
from time import strftime, strptime, mktime, localtime
from typing import List

from mailbox.email import Mail, HTML, PLAIN
from .page import get_page, get_max_page
from .logger import Logger


mailbox = Blueprint("mailbox", __name__)


class ToMailboxForm(FlaskForm):
    date = DateField("发信时间", description="信件发送时间", validators=[DataRequired("必须选择时间")])
    select = SelectField("文件夹", description="INBOX或其他文件夹", validators=[DataRequired("必须选择文件夹")])
    submit = SubmitField("查询")

    def __init__(self, select: list):
        super(ToMailboxForm, self).__init__()

        try:
            del select[select.index("INBOX")]
            select = ["INBOX"] + select
        except ValueError:
            pass


        self.select.choices = select
        self.select.coerce = str
        self.select.default = "INBOX"


def __load_mailbox_page(mail_list, page, to_mail=None, date=None, select=None, next_date=None, last_date=None):
    if not to_mail:
        to_mail = ToMailboxForm(current_user.get_inbox_list())

    max_page = get_max_page(len(mail_list), 10)
    page_list = get_page("mailbox.mail_list_page", page, max_page, date=date, select=select)
    page_mail_list: List[Mail] = mail_list[(page - 1) * 10: page * 10]

    return render_template("mailbox/mailbox.html",
                           to_mail=to_mail,
                           date=date,
                           select=select,
                           page_list=page_list,
                           page=page,
                           mail_list=page_mail_list,
                           max_page=max_page,
                           empty=(len(page_mail_list) == 0),
                           next_date=next_date,
                           last_date=last_date)


@mailbox.route("/")
@login_required
def mail_list_page():
    date = request.args.get("date", None, type=str)
    select = request.args.get("select", "INBOX", type=str)
    page = request.args.get("page", 1, type=int)

    if date:
        date_obj = strptime(date, "%Y-%m-%d")
        mail_list, download = current_user.get_mail_list(select, strftime('%d-%b-%Y', date_obj))
        if mail_list is None and not download:
            flash("旧任务未完成，正在下载邮件，请稍后")
            mail_list = []
        elif download:
            flash("启动新任务下载邮件，请稍后")
            mail_list = []

        next_date = strftime("%Y-%m-%d", localtime(mktime(date_obj) + 24 * 60 * 60))
        last_date = strftime("%Y-%m-%d", localtime(mktime(date_obj) - 24 * 60 * 60))
    else:
        mail_list = []
        next_date = None
        last_date = None

    Logger.print_load_page_log("mail list")
    return __load_mailbox_page(mail_list,
                               page,
                               date=date,
                               select=select,
                               next_date=next_date,
                               last_date=last_date)


def __get_mail() -> (Mail, str, str, int):
    mail_id = request.args.get("mail", None, type=int)
    date = request.args.get("date", None, type=str)
    select = request.args.get("select", None, type=str)
    if not mail_id or not date or not select:
        abort(404)

    date_obj = strftime('%d-%b-%Y', strptime(date, "%Y-%m-%d"))
    mail: Mail = current_user.get_mail(date_obj, select, mail_id)
    if not mail:
        abort(404)

    return mail, date, select, mail_id


@mailbox.route("/html")
@login_required
def html_page():
    html_id = request.args.get("id", 1, type=int)
    mail, *_ = __get_mail()

    count = 0
    for i in mail.body_list:
        count += 1
        if type(i) is HTML:
            if count == html_id:
                return i.body
    return abort(404)


@mailbox.route("/mail")
@login_required
def mail_page():
    mail, date, select, mail_id = __get_mail()

    count = 0
    html_id = []
    plain = []
    for i in mail.body_list:
        count += 1
        if type(i) is HTML:
            html_id.append(count)
        elif type(i) is PLAIN:
            plain.append(i)

    return render_template("mailbox/mail.html",
                           date=date,
                           select=select,
                           mail_id=mail_id,
                           mail=mail,
                           html_id=html_id,
                           plain=plain)
