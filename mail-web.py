from web import HuamMailFlask
from web.configure import configure

import os
import logging

env_dict = os.environ
huan_mail_conf = env_dict.get("HUAN_MAIL_CONF")
if huan_mail_conf is None:
    logging.info("Configure file ./etc/conf.json")
    configure("./etc/conf.json")
else:
    logging.info(f"Configure file {huan_mail_conf}")
    configure(huan_mail_conf)

app = HuamMailFlask(__name__)
