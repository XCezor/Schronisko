from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_migrate import Migrate
import psycopg2
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, BooleanField, ValidationError, SelectField, IntegerField
from wtforms.validators import DataRequired, EqualTo, Length, Optional
from flask_ckeditor import CKEditor
from flask_ckeditor import CKEditorField
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
import bleach
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)
ckeditor = CKEditor(app)
app.config['SECRET_KEY'] = "Ad0ptujPs4LubK0t4"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://application:Ad0ptujPs4LubK0t4@localhost/schronisko'

# Login Manager

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Baza danych

db = SQLAlchemy(app)
migrate = Migrate(app, db)

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

class UserForm(FlaskForm):
    name = StringField("Imię", validators=[DataRequired()])
    surname = StringField("Nazwisko", validators=[DataRequired()])
    username = StringField("Nazwa użytkownika", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    password_hash = PasswordField("Hasło", validators=[DataRequired(), EqualTo('password_hash2', message='Podane hasła muszą być te same.')])
    password_hash2 = PasswordField("Potwierdź hasło", validators=[DataRequired()])
    submit = SubmitField("Utwórz")  

class LoginForm(FlaskForm):
    username = StringField("Login", validators=[DataRequired()])
    password = PasswordField("Hasło", validators=[DataRequired()])
    submit = SubmitField("Zaloguj")  

class AnimalForm(FlaskForm):
    category = SelectField("Kategoria", choices=[('adopcja','adopcja'), ('znalezione','znalezione')], validators=[DataRequired()])
    name = StringField("Imię", validators=[Optional()])
    type = SelectField("Gatunek", choices=[], validators=[DataRequired()])
    breed = StringField("Rasa", validators=[Optional()])
    sex = SelectField("Płeć", choices=[('samiec','samiec'), ('samica','samica')], validators=[DataRequired()])
    age = IntegerField("Wiek", validators=[Optional()])
    weight = IntegerField("Waga (kg)", validators=[Optional()])
    number = StringField("Numer", validators=[DataRequired()])
    box = StringField("Boks", validators=[DataRequired()])
    description = CKEditorField("Opis", validators=[DataRequired()])
    submit = SubmitField("Dodaj") 

# Strona główna

@app.route("/")
def home():
    three_latest_posts = Posts.query.order_by(Posts.post_datetime.desc()).filter(Posts.is_deleted == 'FALSE').limit(3)
    
    for post in three_latest_posts:
        # ucinanie opisu posta do 300 znaków (wyświetla tylko 2 pierwsze paragrafy)
        # (dozwolone tagi: [p, strong, em, s]; dopisywanie brakujących tagów html)
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
            post.description = post.description[0:-4] + " ...</p>"
        
        post.description = bleach.clean(post.description, tags={'p','strong','em','s'}, strip=True)
    return render_template("home.html", three_latest_posts=three_latest_posts)

# Aktualności - posty

# Wyświetlanie wszystkich postów
@app.route("/aktualnosci")
def posts():
    posts = Posts.query.order_by(Posts.post_datetime.desc()).filter(Posts.is_deleted == 'FALSE')
    
    for post in posts:
        # ucinanie opisu posta do 300 znaków (wyświetla tylko 2 pierwsze paragrafy)
        # (dozwolone tagi: [p, strong, em, s]; dopisywanie brakujących tagów html)
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
            post.description = post.description[0:-4] + " ...</p>"
        
        post.description = bleach.clean(post.description, tags={'p','strong','em','s'}, strip=True)
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

# Zwierzęta
@app.route("/zwierzeta")
def animals():
    animals = db.session.query(
        Animals.category, 
        Animals.name, 
        Animals.age, 
        Types.name.label("type"),
        Animals.number,
        Animals.box,
        Animals.description
        ).join(Types, Types.type_id == Animals.type_id).all()
    
    return render_template("animals.html", animals=animals)

@app.route("/zwierzeta/znalezione")
def found():
    animals = db.session.query(
        Animals.category, 
        Types.name.label("type"),
        Animals.number,
        Animals.box,
        Animals.description
        ).join(Types, Types.type_id == Animals.type_id).where(Animals.category == 'znalezione').all()
    return render_template("found.html", animals=animals)

@app.route("/zwierzeta/do-adopcji")
def to_adoption():
    animals = db.session.query(
        Animals.category, 
        Animals.name,
        Animals.breed,
        Animals.sex,
        Animals.age,
        Animals.weight,
        Types.name.label("type"),
        Animals.number,
        Animals.box,
        Animals.description
        ).join(Types, Types.type_id == Animals.type_id).where(Animals.category == 'adopcja').all()
    return render_template("to_adoption.html", animals=animals)

@app.route("/zwierzeta/znalazly-dom")
def found_home():
    return render_template("found_home.html")

@app.route("/zwierzeta/dodaj-zwierze", methods=['GET', 'POST'])
def add_animal():
    form = AnimalForm()

    types = Types.query.all()
    type_choices = []
    for type in types:
        type_choices.append((type.type_id, type.name))
    form.type.choices = type_choices
    
    if form.validate_on_submit():
        new_animal = Animals(
            category = form.category.data,
            in_shelter = True,
            name = form.name.data,
            type_id = form.type.data, 
            breed = form.breed.data,
            sex = form.sex.data,
            age = form.age.data,
            weight = form.weight.data,
            number = form.number.data,
            box = form.box.data,
            description = form.description.data
            )
        db.session.add(new_animal)
        db.session.commit()
        flash("Dodano zwierzę.")

        return redirect(url_for('add_animal'))

    return render_template("add_animal.html", form=form)

# Logowanie
@app.route("/logowanie", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Zalogowano.")
                return redirect(url_for('dashboard'))
            else:
                flash("Nieprawidłowe hasło. Spróbuj ponownie.")
        else:
            flash("Nieprawidłowa nazwa użytkownika. Spróbuj ponownie.")
    return render_template("login.html", form=form)

# Wylogowywanie
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Zostałeś wylogowany.")
    return redirect(url_for('login'))

# Dashboard
@app.route("/moje-konto", methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.user_id
    user_to_update = Users.query.get_or_404(id)
    
    form.submit.label.text = 'Zmień'

    if request.method == 'POST':
        user_to_update.username = request.form['username']
        user_to_update.name = request.form['name']
        user_to_update.surname = request.form['surname']
        user_to_update.email = request.form['email']

        try:
            db.session.commit()
            flash("Zapisano zmiany.")
        except:
            flash("Nie można zapisać zmian.")
        return render_template("dashboard.html", form=form, user_to_update=user_to_update)

    form.username.data = user_to_update.username
    form.name.data = user_to_update.name
    form.surname.data = user_to_update.surname
    form.email.data = user_to_update.email
    
    return render_template("dashboard.html", form=form)

# Tworzenie konta
@app.route("/utworz-konto", methods=['GET', 'POST'])
def create_user():
    form = UserForm()

    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            hashed_password = generate_password_hash(form.password_hash.data)
            user = Users(
                name = form.name.data,
                surname = form.surname.data,
                username = form.username.data,
                email = form.email.data,
                password_hash = hashed_password
                )
            db.session.add(user)
            db.session.commit()

        form.name.data = ''
        form.surname.data = ''
        form.username.data = ''
        form.email.data = ''
        form.password_hash.data = ''
        form.password_hash2.data = ''

        flash("Utworzono konto.")
        return render_template("create_user.html", form=form)
    return render_template("create_user.html", form=form)


# Błędy 404 i 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500
