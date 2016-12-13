# -*- coding:utf-8 -*-

from flask_script import Command, Option


class CreateDB(Command):
    """
    Creates database using SQLAlchemy
    """

    def run(self):
        from database import create_all

        create_all()


class DropDB(Command):
    """
    Drops database using SQLAlchemy
    """

    def run(self):
        from database import drop_all

        drop_all()


class Test(Command):
    """Run tests."""

    start_discovery_dir = "tests"

    def get_options(self):
        return [
            Option('--start_discover', '-s', dest='start_discovery',
                   help='Pattern to search for features',
                   default=self.start_discovery_dir),
        ]

    def run(self):
        import unittest
        from tests import BlueprintTesting

        unittest.TextTestRunner(verbosity=2).run(BlueprintTesting().suite())
