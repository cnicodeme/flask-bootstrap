# -*- coding:utf-8 -*-
import json, logging

try:
    import redis

    class RedisQueue(object):
        """Simple Queue with Redis Backend"""
        def __init__(self, namespace, redis_url):
            self.redis_url = redis_url
            self.namespace = namespace
            self.__db = redis.from_url(redis_url)

        def put(self, queue, item):
            """ Put item into the queue """

            key = '{0}:{1}'.format(self.namespace, queue,)
            self.__db.rpush(key, json.dumps(item))

        def get(self, queue, timeout=None):
            """Remove and return an item from the queue."""
            keys = '{0}:{1}'.format(self.namespace, queue)
            item = self.__db.blpop(keys, timeout=timeout)

            if item is not None:
                try:
                    item = json.loads(item[1])
                except ValueError as e:
                    logging.exception("[ERROR JSON (in queue)] - {1} => {0}\n".format(str(e), str(item)))
                    return None

            return item

        def pipeline(self):
            return self.__db.pipeline()

except ImportError:
    class RedisQueue(object):
        def __init__(self, namespace, redis_url):
            raise ModuleNotFoundError('Module redis not found on the server ...')
