# coding:utf-8

from werkzeug.utils import import_string

from unittest import TestCase
import os, unittest, config

import json

class BlueprintTesting():
    def suite(self):
        # Must return a suite of objects
        suite = unittest.TestSuite()

        for blueprint in config.Testing.BLUEPRINTS:
            if isinstance(blueprint, basestring):
                package = blueprint
            else:
                package = blueprint[0]

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

                if not file.startswith('__init__') and file.endswith('.py'):
                    self._load_suite(new_path, suite)

    def _load_suite(self, file, suite):
        # We remove the "apps." at first, and then the ".py" ending
        package = file.replace('/', '.')[5:-3]
        module = import_string(package)
        suite.addTest(unittest.findTestCases(module))

class BaseTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        print ""
        print cls.__display__

        from main import app_factory
        from database import db, create_all, drop_all

        cls.app = app_factory(config.Testing)
        cls.client = cls.app.test_client()

        drop_all()
        create_all()

        #db.engine.execute('INSERT INTO ...') # Maybe some default datas ?

    @classmethod
    def tearDownClass(cls):
        from database import db, drop_all, remove_session

        drop_all()
        remove_session()


    def setUp(self):
        pass

    def tearDown(self):
        pass
