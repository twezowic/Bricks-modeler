# Program CAD do projektowania z klocków
W ramach tematu należy zbudować aplikację webową, która będzie umożliwiać budowanie z klocków LEGO.
Aplikacja powinna umożliwiać dodawanie nowych modeli, śledzenie postępu układania oraz korzystać z ogólnodostępnej
bazy klocków. Każda instrukcja powinna być przetwarzana w celu automatycznego doboru klocków jeżeli są dostępne
w bazie danych.
Jak każda aplikacja ze śledzeniem postępu powinno być możliwe logowanie oraz kontynuowanie
pracy nad wybranym modelem.
Wyświetlanie powinno być zrealizowane z wykorzystaniem OpenGL.

### Wykorzystywane techonlogie:
- React.js
- Wykorzystanie biblioteki fiber/three.js
- FAST API w pythonie do komunikacji z bazą danych
- Python + Blender do wstępnego przetworzenia plików graficznych
- Baza danych MongoDB
- auth0 do autoryzacji użytkowników

### Wymagania:
- rejestracja/logowania do aplikacji
- zapis postępu w modelowaniu
- udostępnianie swoich modeli wraz z instrukcją
- wyświetlanie instrukcji na stronie
- system posiada 2 tryby:
    - odtwarzanie modeli: w eksploratorze znajdują się tylko elementy niezbędne
    - tworzenie własnych: w eksploratorze znajdują się wszystkie elementy z możliwością filtrowania
- możliwość nakładania materiału (koloru) na elementy
- możliwość budowania w formie edytora:
    - przez przeciąganie elementów z eksploratora do edytora
    - udostępnienie w edytorze translacji w odpowiednich interwałach oraz rotacji o 90 stopni w płaszczyźnie
- dostęp do elementów z ogólnodostępnej bazy klocków
- możliwość komentowania modeli innych użytkowników


### Dostępne strony:
- Builder - główna część aplikacji, budowanie
- Browse - przeglądanie zestawów użytkowników z możliwością wybrania ich do zbudowania
- Your sets - strona z zapisanymi postępami, [dostępne po zalogowaniu]
- Account - własne informacje + komentarze do swoich zestawów, [dostępne po zalogowaniu]
- Strona logowania - zewnętrzna strona od 0Auth


# Instalacja
## Frontend
Zainstalować node.js: https://nodejs.org/en/download
```
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash

nvm install 22

node -v # Should print "v22.13.1".
nvm current # Should print "v22.13.1".

npm -v # Should print "10.9.2".

cd frontend/

npm install
```
## Baza danych


Zainstalować mongodb community edition: https://www.mongodb.com/docs/manual/installation/
```
sudo apt-get install gnupg curl

curl -fsSL https://www.mongodb.org/static/pgp/server-8.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-8.0.gpg \
   --dearmor

echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] https://repo.mongodb.org/apt/ubuntu noble/mongodb-org/8.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-8.0.list

sudo apt-get update

sudo apt-get install -y mongodb-org
```
## API

Zainstalować python: https://www.python.org/downloads/
```
sudo apt install -y python3 python3-pip python3-venv

cd api/

python3 -m venv pyvenv

source pyvenv/bin/activate

pip install -r requirements.txt

cd database/

# Utworzenie listy dostępnych plików, w tej wersji jest ich 96
python3 filter_data.py              

# Dodanie modeli klocków do bazy danych
python3 mongodb.py
```

# Uruchomienie

## Frontend
```
cd frontend/

npm start
```
## API + Baza danych
```
sudo systemctl start mongod

cd api/

source pyvenv/bin/activate

uvicorn api:app --reload
```

### Dane do przykładowego konta użytkownika:

mail: jokixo9944@rowplant.com

hasło: bp+w5$88qX4$xgh
