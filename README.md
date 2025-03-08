[PL]
# Program CAD do projektowania z klocków
W ramach tematu została stworzona aplikacja webowa, która umożliwia budowanie z klocków wykorzystując do tego źródła ![LDraw][https://www.ldraw.org/] oraz ![Rebrickable][https://rebrickable.com/].

![page](https://github.com/user-attachments/assets/5a89b93d-b991-405c-96eb-043f05057b95)

### Wykorzystywane techonlogie:
- React.js
- Wykorzystanie biblioteki fiber/three.js
- FAST API w pythonie do komunikacji z bazą danych
- Python + Blender do wstępnego przetworzenia plików graficznych
- Baza danych MongoDB
- auth0 do autoryzacji użytkowników

### Funkcje:
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
- możliwość komentowania modeli innych użytkowników


### Dostępne strony:
- Builder - główna część aplikacji, budowanie
- Browse - przeglądanie zestawów użytkowników z możliwością wybrania ich do zbudowania
- Your sets - strona z zapisanymi postępami, [dostępne po zalogowaniu]
- Account - własne informacje + komentarze do swoich zestawów, [dostępne po zalogowaniu]
- Strona logowania - zewnętrzna strona od 0Auth



https://github.com/user-attachments/assets/429fcc6e-3df5-4367-aee4-65b013d832b8


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


[ENG]
# CAD software for designing models from bricks
As part of the project, a web application was created that allows building with blocks using the ![LDraw][https://www.ldraw.org/] and ![Rebrickable][https://rebrickable.com/] sources.

![page](https://github.com/user-attachments/assets/5a89b93d-b991-405c-96eb-043f05057b95)

### Techonlogies used:
- React.js
- Use of fiber/three.js library
- FAST API in python for communication with the database
- Python + Blender for preprocessing image files
- MongoDB database
- auth0 for user authentication

### Functions:
- signing-up/signing-in to the application
- saving modelling progress
- sharing your models with instructions
- displaying instructions on the website
- the system has 2 modes:
    - models reconstruction: the explorer contains only the necessary elements
    - create your own models: the explorer contains all the elements with filtering
- applying material (colour) to elements
- building in the editor:
    - dragging elements from the explorer into the editor
    - moving in the appropriate intervals and 90-degree rotation
- commenting on other users' models


### Available pages:
- Builder - main part of the application, building
- Browse - browse user sets with option to select them for building
- Your sets - page with saved progress of user, [available after login].
- Account - user information + comments on users sets, [available after login].
- Login page - external page from 0Auth

https://github.com/user-attachments/assets/429fcc6e-3df5-4367-aee4-65b013d832b8

# Instalation
## Frontend
Install node.js: https://nodejs.org/en/download
```
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash

nvm install 22

node -v # Should print "v22.13.1".
nvm current # Should print "v22.13.1".

npm -v # Should print "10.9.2".

cd frontend/

npm install
```
## Database


Install mongodb community edition: https://www.mongodb.com/docs/manual/installation/
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

Install python: https://www.python.org/downloads/
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

# Running

## Frontend
```
cd frontend/

npm start
```
## API + Database
```
sudo systemctl start mongod

cd api/

source pyvenv/bin/activate

uvicorn api:app --reload
```
