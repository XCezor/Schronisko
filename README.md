# Poradnik - jak uruchomić stronę?

## Potrzebne na start:

### Baza danych:

- baza o nazwie `html` (w PostgreSQL)

- rola (użytkownik) `admin` z hasłem `admin` z uprawnieniami do bazy, tabel

### Virtual Environment:

- w terminalu: `pip3 install virtualenv`

## Do uruchomienia strony:

- W terminalu (będąc w katalogu repozytorium) wpisz `source env/bin/activate`, to polecenie aktywuje wirtualne środowisko (virtual environment).

- Następnie trzeba uruchomić program app.py, by to zrobić wpisz w terminalu `FLASK_APP=app.py flask run`. Strona internetowa powinna już działać! :D

## Jak zobaczyć stronę?

- By zobaczyć stronę, wpisz do paska wyszukiwania w przeglądarce `127.0.0.1:5000` lub `localhost:5000`. Strona powinna się wyświetlić.

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