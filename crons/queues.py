# -*- coding:utf-8 -*-

from flask import current_app
from flask_script import Command, Option
from werkzeug.utils import import_string
from utils.signals import GracefulInterruptHandler


class Queues(Command):
    option_list = (
        Option('--name', '-n', dest='name', required=True),
    )

    """
    Execute a given queue
    """
    def run(self, name):
        method = import_string('queues.{0}.process'.format(name, ))
        current_app.logger.info("Loading queue {0}".format(name))
        with GracefulInterruptHandler() as h:
            while True:
                if h.interrupted:
                    return None

                params = current_app.redis_queue.get(name)
                if params is None:
                    continue

                current_app.logger.info("Got event :")
                current_app.logger.info(params)

                try:
                    method(**params)
                except Exception:
                    current_app.logger.exception('Exception in queue {0}'.format(name))
