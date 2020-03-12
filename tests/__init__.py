# coding:utf-8

from werkzeug.utils import import_string
from flask import current_app
from unittest import TestCase
import os, unittest


class BlueprintTesting():
    def __init__(self, blueprint=None, tests=None):
        self.blueprint = blueprint
        self.tests = tests

    def suite(self):
        # Must return a suite of objects
        suite = unittest.TestSuite()

        if 'BLUEPRINTS' in current_app.config:
            for blueprint in current_app.config['BLUEPRINTS']:
                if isinstance(blueprint, str):
                    package = blueprint
                else:
                    package = blueprint[0]

                if self.blueprint and package != self.blueprint:
                    continue

                self._fetch_directory('apps/%s/tests' % package, suite)

            return suite

    def _fetch_directory(self, directory, suite):
        """
        Fetching for test files recursively
        """
        if os.path.isdir(directory):
            for file in os.listdir(directory):
                new_path = '%s/%s' % (directory, file)
                if os.path.isdir(new_path):
                    self._fetch_directory(new_path, suite)
                else:
                    if file.startswith('__init__'):
                        continue
                    elif not file.endswith('.py'):
                        continue
                    elif self.tests and file[0:-3] != self.tests:
                        continue

                    self._load_suite(new_path, suite)

    def _load_suite(self, file, suite):
        # We remove the "apps." at first, and then the ".py" ending
        package = file.replace('/', '.')[5:-3]
        module = import_string(package)
        suite.addTest(unittest.findTestCases(module))


class BaseTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        print("")
        print(cls.__display__)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass
