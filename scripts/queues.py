# -*- coding:utf-8 -*-

from flask_script import Command, Option
from werkzeug import import_string
from utils.queue import redis_queue
from utils.signals import GracefulInterruptHandler

from flask.current_app import logger


class Queues(Command):
    option_list = (
        Option('--name', '-n', dest='name', required=True),
    )

    """
    Execute a given queue
    """
    def run(self, name):
        method = import_string('queues.{0}.process'.format(name, ))
        logger.info("Loading queue {0}".format(name))
        with GracefulInterruptHandler() as h:
            while True:
                if h.interrupted:
                    return None

                params = redis_queue.get(name)
                if params is None:
                    continue

                logger.info("Got event :")
                logger.info(params)

                try:
                    method(**params)
                except:
                    logger.exception('Exception in queue {0}'.format(name))
