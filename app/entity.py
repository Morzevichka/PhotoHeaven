from app import db

from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from app import login

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    status = db.Column(db.Enum("ACTIVE", "DEACTIVATED", "BANNED", 
                               name="status"), default="ACTIVE")
    role = db.Column(db.Enum("USER", "ROOT", 
                               name="role"), default="USER")
    password_hash = db.Column(db.String(256))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
