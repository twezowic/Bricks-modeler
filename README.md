
W ramach tematu należy zbudować aplikację webową, która będzie umożliwiać budowanie z klocków LEGO.
Aplikacja powinna umożliwiać dodawanie nowych modeli, śledzenie postępu układania oraz korzystać z ogólnodostępnej
bazy klocków. Każda instrukcja powinna być przetwarzana w celu automatycznego doboru klocków jeżeli są dostępne
w bazie danych.
Jak każda aplikacja ze śledzeniem postępu powinno być możliwe logowanie oraz kontynuowanie
pracy nad wybranym modelem.
Wyświetlanie powinno być zrealizowane z wykorzystaniem OpenGL.

Wykorzystywane techonlogie:
- React.js
- Wykorzystanie biblioteki fiber/three.js
- FAST API w pythonie do komunikacji z bazą danych
- Python + Blender do wstępnego przetworzenia plików graficznych
- Baza danych MongoDB
- auth0 do autoryzacji użytkowników

Wymagania:
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


Dostępne strony:
- Builder - główna część aplikacji, budowanie
- Browse - przeglądanie zestawów użytkowników z możliwością wybrania ich do zbudowania
- Your sets - strona z zapisanymi postępami, [dostępne po zalogowaniu]
- Account - własne informacje + komentarze do swoich zestawów, [dostępne po zalogowaniu]
- strona logowania - zewnętrzna przez 0Auth


Baza danych mongo:

## Instalacja
### Frontend
Zainstalować node.js: https://nodejs.org/en/download

cd frontend/

npm install

### API + Baza danych

cd api/

SETUP MONGO

## Uruchomienie

### Frontend
cd fronted/

npm start

### API + Baza danych

./database/start.sh

uvicorn api:app --reload