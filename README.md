# Poradnik - jak uruchomić stronę?

## Potrzebne na start:

### Baza danych PostgreSQL:

- baza o nazwie `html` (nazwa tymczasowa!)

```sql
CREATE DATABASE html;

\c html
```

- tabele `pets` i `types` 

```sql
CREATE TABLE types (
    type_id SERIAL PRIMARY KEY,
    name VARCHAR(50)
);

CREATE TABLE pets (
    pet_id SERIAL PRIMARY KEY,
    type_id INT REFERENCES types(type_id),
    name VARCHAR(30),
    breed VARCHAR(30),
    age INT,
    description VARCHAR(1000),
    date_add TIMESTAMP DEFAULT TIMESTAMP,
    date_on TIMESTAMP DEFAULT TIMESTAMP,
    date_off TIMESTAMP DEFAULT TIMESTAMP
);
```

- rola (użytkownik) `admin` z hasłem `admin` z uprawnieniami do bazy, tabel

```sql
CREATE ROLE admin WITH LOGIN PASSWORD 'admin';

GRANT ALL PRIVILEGES ON DATABASE html TO admin;

GRANT ALL PRIVILEGES ON SCHEMA public TO admin;
```

### Virtual Environment:

- w terminalu: `pip3 install virtualenv` 
- lub (jeśli nie działa wcześniejsze) `sudo apt install python3-virtualenv`

### Python 3

### Git

## Przygotowanie środowiska

- Utwórz katalog `Schronisko`, w terminalu wejdź do niego i wpisz `git clone https://github.com/Kamil-Dolkowski/Schronisko.git`

- Następnie wpisz w terminalu `virtualenv env`, by utworzyć virtual environment.

- Włącz env, wpisując `source env/bin/activate`.

- Następnie wpisz `pip3 install flask flask-sqlalchemy` i `pip install psycopg2-binary`, by pobrać potrzebne biblioteki.

- Wyjdź z env poleceniem `deactivate`.

## Do uruchomienia strony:

- W terminalu (będąc w katalogu repozytorium) wpisz `source env/bin/activate`, to polecenie aktywuje wirtualne środowisko (virtual environment).

- Następnie trzeba uruchomić program app.py, by to zrobić wpisz w terminalu `FLASK_APP=app.py flask run`. Strona internetowa powinna już działać! :D

## Jak zobaczyć stronę?

- By zobaczyć stronę, wpisz do paska wyszukiwania w przeglądarce `localhost:5000` lub `127.0.0.1:5000`. Strona powinna się wyświetlić.

## Co jak chcę wprowadzić zmianę w stronie?

- Aby wprowadzić zmiany do (aktywnej) strony należy najpierw wyłączyć aplikację app.py, by to zrobić, wpisz w terminalu `CTRL+C`.

- Teraz możesz dokonać zmian w plikach. Żeby po zmianach z powrotem zobaczyć efekt, wpisz do terminala `FLASK_APP=app.py flask run`.

## Jak wyłączyć env?

- Po wyłączeniu strony (CTRL+C), wpisz do terminala `deactivate`.

&nbsp;

&nbsp;

# Polecenia w skrócie

### W terminalu:

`source env/bin/activate` - włączenie wirtualnego środowiska (env)

`deactivate` - wyłączenie wirtualnego środowiska (env)

`FLASK_APP=app.py flask run` - uruchomienie app.py (uruchomienie strony)

`CTRL+C` - by wyłączyć app.py

### W pasku wyszukiwania:

`127.0.0.1:5000` lub `localhost:5000` - "domena"
 strony