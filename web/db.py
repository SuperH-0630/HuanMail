from redis import StrictRedis
import logging
import logging.handlers
import os

from .configure import conf


class RedisDB(StrictRedis):
    def __init__(self, host, port, username, passwd, db):
        super().__init__(host=host, port=port, username=username, password=passwd, db=db, decode_responses=True)

        # redis是线程安全的

        self.logger = logging.getLogger("main.database")
        self.logger.setLevel(conf["LOG_LEVEL"])
        if len(conf["LOG_HOME"]) > 0:
            handle = logging.handlers.TimedRotatingFileHandler(
                os.path.join(conf["LOG_HOME"], f"redis-{username}@{host}.log"), backupCount=10)
            handle.setFormatter(logging.Formatter(conf["LOG_FORMAT"]))
            self.logger.addHandler(handle)


redis = RedisDB(host=conf["REDIS_HOST"],
                port=conf["REDIS_PORT"],
                username=conf["REDIS_NAME"],
                passwd=conf["REDIS_PASSWD"],
                db=conf["REDIS_DATABASE"])
