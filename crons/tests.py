# -*- coding:utf-8 -*-

from flask_script import Command, Option
from tests import BlueprintTesting
from main import app_factory
import config, unittest
from database import db


class Tests(Command):
    """Run tests."""
    option_list = (
        Option('--suite', '-s', dest='suite', required=False, default=None),  # Blueprint.suite_name
    )

    def run(self, suite=None):
        blueprint = None
        tests = None

        if suite:
            if suite.find('.'):
                blueprint, tests = suite.split('.', 1)
            else:
                blueprint = suite

        app = app_factory(config=config.Testing)
        client = app.test_client()
        with app.app_context():
            db.drop_all()
            db.create_all()
            db.engine.execute('SET foreign_key_checks=0')  # We don't need foreign key checks on tests
            unittest.TextTestRunner(verbosity=2).run(BlueprintTesting(blueprint, tests).suite())
            db.drop_all()
