from flask import Flask


class HuamMailFlask(Flask):
    def __init__(self, import_name):
        super(HuamMailFlask, self).__init__(import_name)
