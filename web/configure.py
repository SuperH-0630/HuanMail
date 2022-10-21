import json
import logging
import os
from typing import Dict


conf: Dict[str, any] = {
    "SECRET_KEY": "HuanMail-R-Salt",
    "WEBSITE_NAME": "HuanMail",
    "WEBSITE_TITLE": "HuanMail-在线邮件系统",

    "IMAP_HOST": "localhost",
    "IMAP_PORT": 143,
    "IMAP_SSL": False,
    "IMAP_START_SSL": False,
    "IMAP_USERNAME": "{0}",
    "IMAP_PASSWD": "{0}",

    "SMTP_HOST": "localhost",
    "SMTP_PORT": 25,
    "SMTP_SSL": False,
    "SMTP_START_SSL": False,
    "SMTP_USERNAME": "{0}",
    "SMTP_PASSWD": "{0}",

    "REDIS_HOST": "localhost",
    "REDIS_PORT": 6379,
    "REDIS_NAME": "localhost",
    "REDIS_PASSWD": "123456",
    "REDIS_DATABASE": 0,

    "LOG_HOME": "",
    "LOG_FORMAT": "[%(levelname)s]:%(name)s:%(asctime)s "
                  "(%(filename)s:%(lineno)d %(funcName)s) "
                  "%(process)d %(thread)d "
                  "%(message)s",
    "LOG_LEVEL": logging.INFO,
    "LOG_STDERR": True,
    "DEBUG_PROFILE": False,

    "LOGO": "HuanMail.ico",
}



def configure(conf_file: str, encoding="utf-8"):
    """ 运行配置程序, 该函数需要在其他模块被执行前调用 """
    with open(conf_file, mode="r", encoding=encoding) as f:
        json_str = f.read()
        conf.update(json.loads(json_str))
    if type(conf["LOG_LEVEL"]) is str:
        conf["LOG_LEVEL"] = {"debug": logging.DEBUG,
                             "info": logging.INFO,
                             "warning": logging.WARNING,
                             "error": logging.ERROR}.get(conf["LOG_LEVEL"])
    if len(conf["LOG_HOME"]) > 0:
        os.makedirs(conf["LOG_HOME"], exist_ok=True)


env_dict = os.environ
huan_mail_conf = env_dict.get("HUAN_MAIL_CONF")
if huan_mail_conf is None:
    logging.info("Configure file ./etc/conf.json")
    configure("./etc/conf.json")
else:
    logging.info(f"Configure file {huan_mail_conf}")
    configure(huan_mail_conf)