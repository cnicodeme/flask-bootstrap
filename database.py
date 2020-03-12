# -*- coding:utf-8 -*-

from flask_sqlalchemy import SQLAlchemy as SA


class SQLAlchemy(SA):
    def apply_pool_defaults(self, app, options):
        SA.apply_pool_defaults(self, app, options)
        options["pool_pre_ping"] = True  # ping ensure to not loose MySQL cnx
        options["pool_recycle"] = 3600  # Controls the maximum age of any connection
        options["pool_size"] = 100  # ping ensure to not loose MySQL cnx


db = SQLAlchemy(session_options={"autoflush": False})
