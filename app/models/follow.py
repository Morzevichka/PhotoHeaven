from app import db
from sqlalchemy import ForeignKey

class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follow_username = db.Column(db.String(64))
    user_id = db.Column(db.Integer, ForeignKey('user.id'))

    def find_following(username, id):
        return Follow.query.filter_by(follow_username=username, user_id=id).first()