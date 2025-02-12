from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import psycopg2
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:admin@localhost/html'

db = SQLAlchemy(app)

class Pets(db.Model):
    pet_id = db.Column(db.Integer, primary_key=True)
    type_id = db.Column(db.Integer, db.ForeignKey('types.type_id')) 
    name = db.Column(db.String(30))
    breed = db.Column(db.String(30))
    age = db.Column(db.Integer)
    description = db.Column(db.String(1000))
    date_add = db.Column(db.TIMESTAMP, default=datetime.utcnow())
    date_on = db.Column(db.TIMESTAMP, default=datetime.utcnow())
    date_off = db.Column(db.TIMESTAMP, default=datetime.utcnow())

    type = db.relationship('Types', backref='pets', lazy=True)

class Types(db.Model):
    type_id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(50))
    

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/aktualnosci")
def aktualnosci():
    return render_template("posts.html")


@app.route("/pets")
def pets():    
    pets = db.session.query(Pets.name, Pets.age, Types.name.label("type"), Pets.description).join(Types, Types.type_id == Pets.type_id).all()

    return render_template("index.html", animals=pets)

@app.route('/add', methods=['GET', 'POST'])
def add_animal():
    if request.method == 'POST':
        new_animal = Pets(name=request.form['name'], age=request.form['age'], type_id=request.form['type_id'], description=request.form['description'])
        db.session.add(new_animal)
        db.session.commit()

        return redirect("/")

    pets = Pets.query.all()
    return render_template("add.html", animals=pets)


    




@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500
