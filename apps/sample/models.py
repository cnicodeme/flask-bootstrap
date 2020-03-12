# -*- coding:utf-8 -*-

from database import db
from sqlalchemy.orm import relationship, backref
from utils.models import ORModel, JsonSerializable
import datetime


class Sample(db.Model, ORModel, JsonSerializable):
    __tablename__     = 'samples'
    __jsonserialize__ = ['name', 'email', 'created']

    id               = db.Column(db.Integer, primary_key=True)

    name             = db.Column(db.String(250), nullable=True, default=None)
    email            = db.Column(db.String(250), nullable=False, index=True, unique=True)

    created          = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    removed          = db.Column(db.DateTime, nullable=True, default=None)

    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    account    = relationship('Account', backref=backref('samples'))

    def __repr__(self):
        return self.name

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter(cls.email == email).first()
