# -*- coding:utf-8 -*-

from main import app_factory
import commands, config, flask_script
from flask_migrate import MigrateCommand

manager = flask_script.Manager(app_factory)
manager.add_option("-c", "--config", dest="config", required=False, default=config.Config)

manager.add_command('db', MigrateCommand)

for command_str in dir(commands):
    if command_str in ('Command', 'Option'):
        continue
    if command_str[0:2] == '__':
        continue

    command = getattr(commands, command_str)
    command_name = getattr(command, 'name', None)
    if command_name is None:
        command_name = command_str.lower()

    manager.add_command(command_name, command())

if __name__ == "__main__":
    manager.run()
