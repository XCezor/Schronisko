from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from app import app, datetime, UserMixin, generate_password_hash, check_password_hash

db = SQLAlchemy(app)

class Users(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    add_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    password_hash = db.Column(db.Text, nullable=False)

    def get_id(self):
        return str(self.user_id)

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class Animals(db.Model):
    animal_id = db.Column(db.Integer, primary_key=True)
    type_id = db.Column(db.Integer, db.ForeignKey('types.type_id')) 
    category = db.Column(db.String(10), nullable=False)
    in_shelter = db.Column(db.Boolean, nullable=False, server_default="true")
    name = db.Column(db.String(30))
    breed = db.Column(db.String(30))
    date_of_birth = db.Column(db.TIMESTAMP)
    age = db.Column(db.Integer)
    sex = db.Column(db.String(6), nullable=False)
    weight = db.Column(db.Integer)
    number = db.Column(db.String(15))
    box = db.Column(db.String(20))
    description = db.Column(db.Text)
    title_img_name = db.Column(db.String(255))
    date_add = db.Column(db.TIMESTAMP, default=datetime.now)
    date_on = db.Column(db.TIMESTAMP, default=datetime.now)
    date_off = db.Column(db.TIMESTAMP)

    type = db.relationship('Types', backref='Animals', lazy=True)

class Types(db.Model):
    type_id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(20))

class Posts(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    description = db.Column(db.Text, nullable=False)
    title_img_name = db.Column(db.String(255))
    post_datetime = db.Column(db.DateTime, default=datetime.now)
    last_edit_datetime = db.Column(db.DateTime, default=None)
    is_deleted = db.Column(db.Boolean, server_default="false")

    author = db.relationship('Users', backref='Posts', lazy=True)

class Pages(db.Model):
    page_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    title_img_name = db.Column(db.String(255))
    last_edit_datetime = db.Column(db.DateTime, default=None)