# coding:utf-8

from tests import BaseTestCase


class TestCreate(BaseTestCase):
    __display__ = "Example > Create"

    def test_create(self):
        """ Test creation """
        self.assertEqual(int('201'), 201)

    def test_create_that_fails(self):
        """ Test creation that will fail"""
        self.assertEqual(int('204'), 201)
