# coding:utf-8

from flask import current_app

from boto.s3.connection import S3Connection
from boto.s3.key import Key

import os

class AmazonS3(object):
    def __init__(self):
        self.conn = S3Connection(current_app.config['AWS_ACCESS_KEY'], current_app.config['AWS_SECRET_KEY'])

    def _get_bucket(self):
        return self.conn.get_bucket(current_app.config['AWS_BUCKET'], validate=False)

    def get_file(self, file):
        return Key(bucket=self._get_bucket(), name=file)
