from flask import Blueprint, render_template, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import (StringField,
                     SubmitField,
                     TextAreaField,
                     ValidationError)
from wtforms.validators import DataRequired, Regexp
from flask_login import login_required, current_user
import re
import smtplib

from sender.email import Email

sender = Blueprint("sender", __name__)


class MailInputForm(FlaskForm):
    sender_name = StringField("发信人", description="发信人名称", validators=[DataRequired(f"必须填写发信人名称")])
    sender_address = StringField("发信地址",
                                 description="发信人邮件地址",
                                 validators=[
                                     DataRequired(f"必须填写发信人名称"),
                                     Regexp(
                                         r"^[a-zA-Z0-9_\.\-]+@[a-zA-Z0-9_\-]+(\.[a-zA-Z0-9_\.]+)+$",
                                         message=f"发信人邮件地址不满足正则表达式")])
    subject = StringField("标题", description="邮件标题", validators=[DataRequired(f"必须填写邮件标题")])

    rc = StringField("收件人", description="收件人")
    cc = StringField("抄送人", description="抄送人")
    bcc = StringField("密送人", description="密送人")

    content = TextAreaField("普通邮件正文", description="邮件正文")

    submit = SubmitField("发送")

    __email = re.compile(r"^[a-zA-Z0-9_.\-]+@[a-zA-Z0-9_\-]+(\.[a-zA-Z0-9_.]+)+$")

    def __init__(self):
        super(MailInputForm, self).__init__()
        self.sender_name.data = current_user.username
        self.sender_address.data = current_user.smtp_address

        self.rc_ = []
        self.cc_ = []
        self.bcc_ = []

    def validate_sender_address(self, field):
        if not MailInputForm.__email.match(field.data):
            raise ValidationError("邮件地址不合法")

    @staticmethod
    def __split_address(address: str):
        res = [i.strip() for i in address.split(" ") if len(i.strip()) > 0]
        res_len = len(res)

        if res_len != 1 and res_len != 2:
            return None
        elif res_len == 1:
            if not MailInputForm.__email.match(res[0]):
                raise ValidationError(f"收件地址 {res[0]} 不合法")
            name = res[0].split("@")[0]
            return name, res[0]
        else:
            if not MailInputForm.__email.match(res[1]):
                raise ValidationError(f"收件地址 {res[1]} 不合法")
            return tuple(res)

    def validate_rc(self, field):
        split = [i.strip() for i in field.data.split(";")]
        for i in split:
            res = self.__split_address(i)
            if res:
                self.rc_.append(res)

    def validate_cc(self, field):
        split = [i.strip() for i in field.data.split(";")]
        for i in split:
            res = self.__split_address(i)
            if res:
                self.cc_.append(res)

    def validate_bcc(self, field):
        split = [i.strip() for i in field.data.split(";")]
        for i in split:
            res = self.__split_address(i)
            if res:
                self.bcc_.append(res)


@sender.route("/", methods=["GET", "POST"])
@login_required
def send_page():
    form: MailInputForm = MailInputForm()
    if form.validate_on_submit():
        email = Email(from_addr=(form.sender_name.data, form.sender_address.data),
                      subject=form.subject.data,
                      to_addr=form.rc_,
                      cc_addr=form.cc_,
                      bcc_addr=form.bcc_)
        email.add_text(form.content.data)

        if len(form.rc_) + len(form.cc_) + len(form.bcc_) <= 0:
            flash("没有收件人")
        else:
            try:
                current_user.send(email)
            except smtplib.SMTPException:
                flash("发信失败")
            else:
                flash("发信成功")
        return redirect(url_for("sender.send_page"))
    return render_template("sender/sender.html", form=form)
