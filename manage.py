# -*- coding:utf-8 -*-

import flask_script
from main import app_factory
import commands, config

from flask_migrate import MigrateCommand

manager = flask_script.Manager(app_factory)
manager.add_option("-c", "--config", dest="config", required=False, default=config.Dev)

manager.add_command("test", commands.Test())
manager.add_command("create_db", commands.CreateDB())
manager.add_command("drop_db", commands.DropDB())
manager.add_command('db', MigrateCommand)

if __name__ == "__main__":
    manager.run()
