from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_migrate import Migrate
import psycopg2
from flask_ckeditor import CKEditor
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
import bleach
from bs4 import BeautifulSoup
from datetime import datetime
from webforms import PostForm, UserForm, LoginForm, PagesForm, AnimalForm, AnimalMigrateForm
from werkzeug.utils import secure_filename
import uuid as uuid 
import os


app = Flask(__name__)
ckeditor = CKEditor(app)
app.config['SECRET_KEY'] = "Ad0ptujPs4LubK0t4"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://application:Ad0ptujPs4LubK0t4@localhost/schronisko'

UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 # Limit przesyłanych zdjęć: 5MB = 5 * 1024 * 1024

# Login Manager

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Baza danych

from models import db, Users, Animals, Types, Categories, Posts, Pages

migrate = Migrate(app, db)


#======================STRONA GLOWNA==========================

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

#=======================AKTUALNOSCI===========================

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
    return render_template("posts/posts.html", posts=posts)

# Wyświetlenie szczegółów posta
@app.route("/aktualnosci/<int:id>")
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template("posts/post.html", post=post)

# Dodawanie nowego posta
@app.route("/aktualnosci/dodaj-post", methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        if form.title_img.data:
            safe_filename = secure_filename(form.title_img.data.filename)
            title_img_name = str(uuid.uuid1()) + "_" + safe_filename
        else:
            title_img_name = None

        new_post = Posts(
            title = form.title.data, 
            author_id = current_user.user_id,
            description = form.description.data,
            title_img_name = title_img_name
            )

        db.session.add(new_post)
        db.session.commit()

        # Zapisywanie plików
        if form.title_img.data or any(file.filename for file in form.images.data):
            catalog_path = os.path.join(app.config['UPLOAD_FOLDER'], 'posts', str(new_post.post_id))
            os.makedirs(catalog_path, exist_ok=True)

            if form.title_img.data:
                file_path = os.path.join(catalog_path, title_img_name)
                form.title_img.data.save(file_path)

            if any(file.filename for file in form.images.data):
                for file in form.images.data:
                    safe_filename = secure_filename(file.filename)
                    img_name = str(uuid.uuid1()) + "_" + safe_filename

                    file_path = os.path.join(catalog_path, img_name)
                    file.save(file_path)

        flash("Dodano post!")

    return render_template("posts/add_post.html", form=form)

# Edycja posta
@app.route("/aktualnosci/edytuj-post/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)

    form = PostForm()

    if form.validate_on_submit():
        
        post.title = form.title.data, 
        post.author_id = current_user.user_id,
        post.description = form.description.data
        
        form.title.data = ''
        form.description.data = ''

        db.session.add(post)
        db.session.commit()
        flash("Zapisano zmiany!")

        return redirect(url_for('post', id=post.post_id))
    
    form.title.data = post.title
    form.description.data = post.description
    return render_template('posts/edit_post.html', form=form)

# Usuwanie posta
@app.route("/aktualnosci/usuwanie-posta/<int:id>")
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)

    post_to_delete.is_deleted = True

    db.session.add(post_to_delete)
    db.session.commit()
    flash("Usunięto post.")

    return redirect(url_for('posts'))

#=========================ZWIERZETA===========================

@app.route("/zwierzeta")
def animals():
    
    return render_template("animals/animals.html")

@app.route("/zwierzeta/usuniete")
@login_required
def deleted_animals():
    deleted_animals = db.session.query(
        Animals.animal_id,
        Animals.sex,
        Animals.age,
        Animals.weight,
        Animals.number,
        Animals.box,
        Animals.title_img_name
    ).filter(
        Animals.is_deleted == True
    ).all()
    
    return render_template("animals/deleted_animals.html", animals=deleted_animals)

@app.route("/zwierzeta/<int:id>", methods=['GET','POST'])
def animal(id):
    animal = Animals.query.get_or_404(id)

    if animal.is_deleted == True:
        abort(404)

    form = AnimalMigrateForm()

    if form.validate_on_submit():
        if form.recently_arrived.data:
            animal.category_id = 1
            animal.in_shelter = True
            flash("Zmieniono kategorię na: 'Niedawno trafiły'")
        if form.to_adoption.data:
            animal.category_id = 2
            animal.in_shelter = True
            flash("Zmieniono kategorię na: 'Do adopcji'")
        if form.found_home.data:
            animal.in_shelter = False
            flash("Zmieniono kategorię na: 'Znalazły dom'")

        db.session.add(animal)
        db.session.commit()

        return redirect(url_for('animal', id=animal.animal_id))

    path = app.config['UPLOAD_FOLDER'] + 'animals/' + str(id) + '/' 
    is_dir = os.path.isdir(path)

    if is_dir:
        all_files = os.listdir(path)
        images = [img for img in all_files if os.path.isfile(os.path.join(path, img))]
    else:
        images=None

    return render_template("animals/animal.html", animal=animal, images=images, form=form)

@app.route("/zwierzeta/usuniete/<int:id>", methods=['GET','POST'])
@login_required
def deleted_animal(id):
    animal = Animals.query.get_or_404(id)

    if animal.is_deleted == False:
        abort(404)

    path = app.config['UPLOAD_FOLDER'] + 'animals/' + str(id) + '/' 
    is_dir = os.path.isdir(path)

    if is_dir:
        all_files = os.listdir(path)
        images = [img for img in all_files if os.path.isfile(os.path.join(path, img))]
    else:
        images=None

    return render_template("animals/deleted_animal.html", animal=animal, images=images)

@app.route("/zwierzeta/niedawno-trafily")
def recently_arrived():
    animals = db.session.query(
        Animals.animal_id,
        Animals.sex,
        Animals.age,
        Animals.weight,
        Animals.number,
        Animals.box,
        Animals.title_img_name
    ).filter(
        Animals.category_id == 1,
        Animals.in_shelter == True,
        Animals.is_deleted == False
    ).all()
    return render_template("animals/recently_arrived.html", animals=animals)

@app.route("/zwierzeta/psy-do-adopcji")
def dogs_to_adoption():
    animals = db.session.query(
        Animals.animal_id,
        Animals.name,
        Animals.sex,
        Animals.age,
        Animals.weight,
        Animals.number,
        Animals.box,
        Animals.title_img_name
    ).filter(
        Animals.category_id == 2,
        Animals.type_id == 1,
        Animals.in_shelter == True,
        Animals.is_deleted == False
    ).all()
    return render_template("animals/dogs_to_adoption.html", animals=animals)

@app.route("/zwierzeta/koty-do-adopcji")
def cats_to_adoption():
    animals = db.session.query(
        Animals.animal_id,
        Animals.name,
        Animals.sex,
        Animals.age,
        Animals.weight,
        Animals.number, 
        Animals.box,
        Animals.title_img_name
    ).filter(
        Animals.category_id == 2,
        Animals.type_id == 2,
        Animals.in_shelter == True,
        Animals.is_deleted == False
    ).all()
    return render_template("animals/cats_to_adoption.html", animals=animals)

@app.route("/zwierzeta/znalazly-dom")
def found_home():
    animals = db.session.query(
        Animals.animal_id,
        Animals.name,
        Animals.sex,
        Animals.age,
        Animals.weight,
        Animals.number,
        Animals.box,
        Animals.title_img_name
    ).filter(
        Animals.in_shelter == False,
        Animals.is_deleted == False
    ).all()
    return render_template("animals/found_home.html", animals=animals)

@app.route("/zwierzeta/dodaj-zwierze", methods=['GET', 'POST'])
@login_required
def add_animal():
    form = AnimalForm()

    types = Types.query.all()
    type_choices = []
    for type in types:
        type_choices.append((type.type_id, type.name))
    form.type.choices = type_choices

    categories = Categories.query.all()
    category_choices = []
    for category in categories:
        category_choices.append((category.category_id, category.name))
    form.category.choices = category_choices
    
    if form.validate_on_submit():
        
        if form.title_img.data:
            safe_filename = secure_filename(form.title_img.data.filename)
            title_img_name = str(uuid.uuid1()) + "_" + safe_filename
        else:
            title_img_name = None

        new_animal = Animals(
            category_id = form.category.data,
            in_shelter = True,
            name = form.name.data,
            type_id = form.type.data, 
            sex = form.sex.data,
            castration_sterilization = form.castration_sterilization.data,
            age = form.age.data,
            fur = form.fur.data,
            weight = form.weight.data,
            number = form.number.data,
            box = form.box.data,
            attitude_to_dogs = form.attitude_to_dogs.data,
            attitude_to_cats = form.attitude_to_cats.data,
            attitude_to_people = form.attitude_to_people.data,
            character = form.character.data,
            description = form.description.data,
            title_img_name = title_img_name
        )

        db.session.add(new_animal)
        db.session.commit()

        # Zapisywanie plików 
        if form.title_img.data or any(img.filename for img in form.images.data):
            catalog_path = os.path.join(app.config['UPLOAD_FOLDER'], 'animals', str(new_animal.animal_id))
            os.makedirs(catalog_path, exist_ok=True)

            if form.title_img.data:
                file_path = os.path.join(catalog_path, title_img_name)
                form.title_img.data.save(file_path)

            if any(img.filename for img in form.images.data):
                for file in form.images.data:
                    safe_filename = secure_filename(file.filename)
                    img_name = str(uuid.uuid1()) + "_" + safe_filename

                    file_path = os.path.join(catalog_path, img_name)
                    file.save(file_path)

        flash("Dodano zwierzę.")

        return redirect(url_for('add_animal'))

    return render_template("animals/add_animal.html", form=form)

@app.route("/zwierzeta/edytuj-zwierze/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_animal(id):
    form = AnimalForm()

    animal = Animals.query.get_or_404(id)

    types = Types.query.all()
    type_choices = []
    for type in types:
        type_choices.append((type.type_id, type.name))
    form.type.choices = type_choices

    categories = Categories.query.all()
    category_choices = []
    for category in categories:
        category_choices.append((category.category_id, category.name))
    form.category.choices = category_choices

    if form.validate_on_submit():
        
        if form.title_img.data:
            safe_filename = secure_filename(form.title_img.data.filename)
            title_img_name = str(uuid.uuid1()) + "_" + safe_filename
        else:
            title_img_name = None
        
        animal.category_id = form.category.data,
        animal.in_shelter = True,
        animal.name = form.name.data,
        animal.type_id = form.type.data, 
        animal.sex = form.sex.data,
        animal.castration_sterilization = form.castration_sterilization.data,
        animal.age = form.age.data,
        animal.fur = form.fur.data,
        animal.weight = form.weight.data,
        animal.number = form.number.data,
        animal.box = form.box.data,
        animal.attitude_to_dogs = form.attitude_to_dogs.data,
        animal.attitude_to_cats = form.attitude_to_cats.data,
        animal.attitude_to_people = form.attitude_to_people.data,
        animal.character = form.character.data,
        animal.description = form.description.data,
        animal.title_img_name = title_img_name

        db.session.add(animal)
        db.session.commit()

        # Zapisywanie plików 
        if form.title_img.data or any(img.filename for img in form.images.data):
            catalog_path = os.path.join(app.config['UPLOAD_FOLDER'], 'animals', str(animal.animal_id))
            os.makedirs(catalog_path, exist_ok=True)

            if form.title_img.data:
                file_path = os.path.join(catalog_path, title_img_name)
                form.title_img.data.save(file_path)

            if any(img.filename for img in form.images.data):
                for file in form.images.data:
                    safe_filename = secure_filename(file.filename)
                    img_name = str(uuid.uuid1()) + "_" + safe_filename

                    file_path = os.path.join(catalog_path, img_name)
                    file.save(file_path)

        flash("Zapisano zmiany!")

        return redirect(url_for('edit_animal'))

    form.type.data = animal.type_id
    form.category.data = animal.category_id
    form.name.data = animal.name
    form.age.data = animal.age
    form.sex.data = animal.sex
    form.castration_sterilization.data = animal.castration_sterilization
    form.weight.data = animal.weight
    form.fur.data = animal.fur
    form.number.data = animal.number
    form.box.data = animal.box
    form.attitude_to_dogs.data = animal.attitude_to_dogs
    form.attitude_to_cats.data = animal.attitude_to_cats
    form.attitude_to_people.data = animal.attitude_to_people
    form.character.data = animal.character
    form.description.data = animal.description

    form.submit.label.text = 'Zapisz'

    return render_template("animals/edit_animal.html", form=form)

@app.route("/zwierzeta/usun-zwierze/<int:id>", methods=['GET','POST'])
@login_required
def delete_animal(id):
    animal_to_delete = Animals.query.get_or_404(id)

    if animal_to_delete.is_deleted == True:
        abort(404)

    animal_to_delete.is_deleted = True

    db.session.add(animal_to_delete)
    db.session.commit()
    flash("Usunięto zwierzę.")

    return redirect(url_for('animals'))

@app.route("/zwierzeta/usuniete/przywroc-zwierze/<int:id>", methods=['GET','POST'])
@login_required
def restore_animal(id):
    animal_to_restore = Animals.query.get_or_404(id)

    if animal_to_restore.is_deleted == False:
        abort(404)
    
    animal_to_restore.is_deleted = False

    db.session.add(animal_to_restore)
    db.session.commit()
    flash("Przywrócono zwierzę.")

    return redirect(url_for('deleted_animals'))

#===========================INFO==============================



#==========================KONTAKT============================

# Kontakt - podglad tresci
@app.route("/kontakt")
def contact():
    contact = Pages.query.get_or_404(1)
    return render_template("contact/contact.html", contact=contact)

# Kontakt - edycja tresci
@app.route("/kontakt/edycja", methods=['GET', 'POST'])
@login_required
def edit_contact():

    entry = Pages.query.get(1)

    if entry is None:
        init_contact = Pages()
        init_contact.page_id = 1
        init_contact.title = 'Kontakt'
        init_contact.description = ''
        db.session.add(init_contact)
        db.session.commit()
        entry = Pages.query.get(1)

    form = PagesForm(obj=entry)

    if form.validate_on_submit():

        entry.title = 'Kontakt'
        entry.description = form.description.data

        db.session.add(entry)
        db.session.commit()
        flash("Zapisano zmiany!")

        return redirect(url_for('contact'))     
    
    form.description.data = entry.description    

    return render_template('contact/edit_contact.html', form=form)

#==========================LOGOWANIE==========================

#Info o adopcji - podglad tresci
@app.route("/info")
def pages():
    pages = Pages.query.order_by(Pages.page_id.desc())
    
    for page in pages:
        # ucinanie opisu posta do 300 znaków (wyświetla tylko 2 pierwsze paragrafy)
        # (dozwolone tagi: [p, strong, em, s]; dopisywanie brakujących tagów html)
        original_length = len(bleach.clean(page.description))

        soup = BeautifulSoup(page.description, 'html.parser')
        paragraphs = soup.find_all('p')
        first_two_paragraphs = paragraphs[:2]

        page.description = ''
        number_of_chars = 0

        for p in first_two_paragraphs:
            if len(page.description + str(p)) > 300:
                page.description += str(p)[:300-number_of_chars]
                break
            page.description += str(p)
            number_of_chars += len(page.description)

        exit_length = len(bleach.clean(page.description))

        if original_length != exit_length + 1:
            page.description = page.description[0:-4] + " ...</p>"
        
        page.description = bleach.clean(page.description, tags={'p','strong','em','s'}, strip=True)
    return render_template("pages.html", pages=pages)

#Info
@app.route("/info/<int:id>")
def page(id):
    page = Pages.query.get_or_404(id)
    return render_template("info.html", page=page)

#dodanie info
@app.route("/info/dodaj-info", methods=['GET', 'POST'])
@login_required
def add_page():
    form = PagesForm()
    if form.validate_on_submit():
        page = Pages(
            title = form.title.data, 
            description = form.description.data
            )
        
        form.title.data = ''
        form.description.data = ''

        db.session.add(page)
        db.session.commit()
        flash("Dodano info!")

    return render_template("add_info.html", form=form)

#Info o adopcji - edycja
@app.route("/info/edycja/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_page(id):

    page = Pages.query.get_or_404(id)

    form = PagesForm(obj=page)

    if form.validate_on_submit():
        
        page.title = form.title.data, 
        page.description = form.description.data
        
        form.title.data = ''
        form.description.data = ''

        db.session.add(page)
        db.session.commit()
        flash("Zapisano zmiany!")

        return redirect(url_for('page', id=page.page_id))  
      
    form.title.data = page.title
    form.description.data = page.description
    return render_template('edit_info.html', form=form)

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
    return render_template("login/login.html", form=form)

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
        return render_template("login/dashboard.html", form=form, user_to_update=user_to_update)

    form.username.data = user_to_update.username
    form.name.data = user_to_update.name
    form.surname.data = user_to_update.surname
    form.email.data = user_to_update.email
    
    return render_template("login/dashboard.html", form=form)

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
        return render_template("login/create_user.html", form=form)
    return render_template("login/create_user.html", form=form)

#=====================BLEDY 404 I 500=========================

@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html"), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template("errors/500.html"), 500
