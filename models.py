from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from flask_login import UserMixin


db = SQLAlchemy()


class ProspectModel(db.Model):
    __tablename__ = "prospects"

    prospect_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column(db.String)
    highschool_id = db.Column(db.Integer, db.ForeignKey('highschools.id'), index=True)
    highschool = db.relationship('HighSchoolModel', backref=db.backref('prospects', lazy=True))
    overall = db.Column(db.Integer, index= True)
    potential = db.Column(db.Integer, index= True)
    committed = db.Column(db.Integer, index= True)
    email = db.Column(db.String, index=True)


    def __init__(self,name,highschool_id, overall, potential):
        self.name = name
        self.highschool_id = highschool_id
        self.overall = overall
        self.potential = potential


class HighSchoolModel(db.Model):
    __tablename__ = "highschools"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True,index=True)
    name = db.Column(db.String)


class RecruitModel(db.Model):
    __tablename__ = "recruits"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    prospect_id = db.Column(db.Integer, index = True)
    college_id = db.Column(db.Integer, index=True)

    def __init__(self, prospect_id, college_id):
        self.prospect_id = prospect_id
        self.college_id = college_id

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Watchlist(db.Model):
    __tablename__ = 'watchlist'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    prospect_id = db.Column(db.Integer, db.ForeignKey('prospects.prospect_id'))

    user = db.relationship('User', backref=db.backref('watchlisted_prospects', lazy='dynamic'))
    prospect = db.relationship('ProspectModel', backref='watchlist_users')


