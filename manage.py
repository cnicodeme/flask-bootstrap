# -*- coding:utf-8 -*-

from main import app_factory
import flask_script, os
from flask_migrate import MigrateCommand
from werkzeug.utils import import_string


def load_commands(manager):
    # Loading commands
    crons = os.path.join(os.path.dirname(__file__), "crons")
    for file in os.listdir(crons):
        if not os.path.isfile(os.path.join(crons, file)):
            continue

        if file == '__init__.py':
            continue

        if file[-3:] != '.py':
            continue

        filename = file[:-3]
        objectname = ''.join([x.capitalize() for x in filename.split('_')])

        command = import_string('crons.{0}.{1}'.format(filename, objectname))
        command_name = getattr(command, "name", None)
        if command_name is None:
            command_name = filename

        manager.add_command(command_name, command())


if __name__ == "__main__":
    manager = flask_script.Manager(app_factory)
    manager.add_command('db', MigrateCommand)

    load_commands(manager)

    manager.run()
