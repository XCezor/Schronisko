from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, BooleanField, ValidationError, SelectField, IntegerField, FileField, MultipleFileField
from wtforms.validators import DataRequired, EqualTo, Length, Optional
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_ckeditor import CKEditorField


class PostForm(FlaskForm):
    title = StringField("Tytuł", validators=[DataRequired()])
    description = CKEditorField("Opis", validators=[DataRequired()])
    title_img = FileField("Zdjęcie tytułowe", validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Obsługiwane rozszerzenia: png, jpg, jpeg')])
    images = MultipleFileField("Galeria zdjęć", validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Obsługiwane rozszerzenia: png, jpg, jpeg')])
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

class PagesForm(FlaskForm):
    title = StringField("Tytuł", validators=[DataRequired()])
    description = CKEditorField("Opis", validators=[DataRequired()])
    title_img = FileField("Zdjęcie tytułowe", validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Obsługiwane rozszerzenia: png, jpg, jpeg')])
    images = MultipleFileField("Galeria zdjęć", validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Obsługiwane rozszerzenia: png, jpg, jpeg')])
    submit = SubmitField("Zapisz")

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
    title_img = FileField("Zdjęcie tytułowe", validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Obsługiwane rozszerzenia: png, jpg, jpeg')])
    images = MultipleFileField("Galeria zdjęć", validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Obsługiwane rozszerzenia: png, jpg, jpeg')])
    submit = SubmitField("Dodaj") 