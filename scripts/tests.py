# -*- coding:utf-8 -*-

from flask_script import Command, Option


class Tests(Command):
    """Run tests."""

    name = "test"  # By default, will use the name of the class
    start_discovery_dir = "test"

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
