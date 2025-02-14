from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_migrate import Migrate
import psycopg2
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditor
from flask_ckeditor import CKEditorField
from werkzeug.security import generate_password_hash, check_password_hash
import bleach
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)
ckeditor = CKEditor(app)
app.config['SECRET_KEY'] = "Ad0ptujPs4LubK0t4"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://application:Ad0ptujPs4LubK0t4@localhost/schronisko'

# Baza danych

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    add_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    password_hash = db.Column(db.String(128), nullable=False)

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class Pets(db.Model):
    pet_id = db.Column(db.Integer, primary_key=True)
    type_id = db.Column(db.Integer, db.ForeignKey('types.type_id')) 
    name = db.Column(db.String(30))
    breed = db.Column(db.String(30))
    age = db.Column(db.Integer)
    description = db.Column(db.Text)
    date_add = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    date_on = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    date_off = db.Column(db.TIMESTAMP, default=datetime.utcnow)

    type = db.relationship('Types', backref='pets', lazy=True)

class Types(db.Model):
    type_id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(20))

class Posts(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(50), server_default='Brak')
    description = db.Column(db.Text, nullable=False)
    post_datetime = db.Column(db.DateTime, default=datetime.utcnow)
    last_edit_datetime = db.Column(db.DateTime, default=None)
    is_deleted = db.Column(db.Boolean, server_default="false")

# Formularze

class PostForm(FlaskForm):
    title = StringField("Tytuł", validators=[DataRequired()])
    author = StringField("Autor (opcjonalne):")
    description = CKEditorField("Opis", validators=[DataRequired()])
    submit = SubmitField("Dodaj")

# Strona główna

@app.route("/")
def home():
    return render_template("home.html")

# Aktualności - posty

# Wyświetlanie wszystkich postów
@app.route("/aktualnosci")
def posts():
    posts = Posts.query.order_by(Posts.post_datetime.desc()).filter(Posts.is_deleted == 'FALSE')
    for post in posts:
        # ucinanie opisu posta do 300 znaków i dopisywanie brakujących tagów html
        
        original_length = len(bleach.clean(post.description))
        soup = BeautifulSoup(post.description, 'html.parser')
        paragraphs = soup.find_all('p')
        first_two_paragraphs = paragraphs[:2]

        post.description = ''
        number_of_chars = 0
        for p in first_two_paragraphs:
            if len(post.description + str(p)) > 300:
                post.description += str(p)[:300-number_of_chars]
                break
            post.description += str(p)
            number_of_chars += len(post.description)

        exit_length = len(bleach.clean(post.description))

        if original_length != exit_length + 1:
            print(original_length)
            print(exit_length)
            post.description = post.description[0:-4] + " ...</p>"
        
        post.description = bleach.clean(post.description, tags={'p','strong','em','s'}, strip=True)
        
        # -------------------------------------------------

        # post.description = bleach.clean(post.description, tags={'p','strong','em','table','tbody','tr','td','ol','ul','li'}, strip=True)

        # soup = BeautifulSoup(post.description[:300], 'html.parser')
        # table_all = soup.find_all('table')
        # [table.decompose() for table in table_all]

        # post.description = soup.prettify()
        # if len(post.description) > 300:
        #     post.description = post.description[0:-9] + " ...</p>"
    return render_template("posts.html", posts=posts)

# Wyświetlenie szczegółów posta
@app.route("/aktualnosci/<int:id>")
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template("post.html", post=post)

# Dodawanie nowego posta
@app.route("/aktualnosci/dodaj-post", methods=['GET', 'POST'])
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Posts(
            title = form.title.data, 
            author = form.author.data or 'Brak',
            description = form.description.data
            )
        
        form.title.data = ''
        form.author.data = ''
        form.description.data = ''

        db.session.add(post)
        db.session.commit()
        flash("Dodano post!")

    return render_template("add_post.html", form=form)

# Edycja posta
@app.route("/aktualnosci/edytuj-post/<int:id>", methods=['GET', 'POST'])
def edit_post(id):
    post = Posts.query.get_or_404(id)

    form = PostForm()

    if form.validate_on_submit():
        
        post.title = form.title.data, 
        post.author = form.author.data or 'Brak',
        post.description = form.description.data
        
        form.title.data = ''
        form.author.data = ''
        form.description.data = ''

        db.session.add(post)
        db.session.commit()
        flash("Zapisano zmiany!")

        return redirect(url_for('post', id=post.post_id))
    
    form.title.data = post.title
    form.author.data = post.author
    form.description.data = post.description
    return render_template('edit_post.html', form=form)

# Usuwanie posta
@app.route("/aktualnosci/usuwanie-posta/<int:id>")
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)

    post_to_delete.is_deleted = True

    db.session.add(post_to_delete)
    db.session.commit()
    flash("Usunięto post.")

    return redirect(url_for('posts'))

    



# ????

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
