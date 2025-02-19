# Poradnik - jak uruchomić stronę?

## Potrzebne na start:

### Baza danych PostgreSQL:

- baza o nazwie `schronisko`

```sql
CREATE DATABASE schronisko;
```

- należy przełączyć się na bazę `schronisko` [WAŻNE!!]

```
\c schronisko
```

- rola (użytkownik) `application` z hasłem `Ad0ptujPs4LubK0t4` z uprawnieniami do bazy, schematu 'public'

```sql
CREATE ROLE application WITH LOGIN PASSWORD 'Ad0ptujPs4LubK0t4';

GRANT ALL PRIVILEGES ON DATABASE schronisko TO application;

GRANT ALL PRIVILEGES ON SCHEMA public TO application;
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

- Następnie wpisz `pip install -r requirements.txt`, aby pobrać wszystkie potrzebne biblioteki.

- Aby utworzyć tabele w bazie danych, trzeba najpierw zainicjować migracje bazy. Wpisz w terminalu `flask db init`, by zainicjować migracje. Następnie wpisz `flask db migrate -m 'init tables'` i `flask db upgrade`. Te 2 ostatnie polecenia utworzą brakujące tabele w Twojej bazie `schronisko`.

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

`CTRL+C` - by wyłączyć flaska

`flask db init` - zainicjalizowanie migracji bazy (tylko raz, na początku)

`flask db migrate -m 'nazwa commitu/migracji'` oraz `flask db upgrade` - by dodać brakujące elementy w bazie (na podstawie klas utworzonych w models.py)

### W pasku wyszukiwania:

`127.0.0.1:5000` lub `localhost:5000` - "domena"
 strony

### Polecenia dla ekspertów: ;)

`export FLASK_DEBUG=1` - włączenie trybu debugowania (serwer sam się zresetuje po zapisanych zmianach w plikach)

`export FLASK_APP=app.py` - ustawienie zmiennej środowiskowej FLASK_APP na app.py, dzięki czemu nie trzeba pisać jej za każdym razem (do uruchomienia strony wystarczy napisać `flask run`)