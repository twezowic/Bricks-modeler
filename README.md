
W ramach tematu należy zbudować aplikację webową, która będzie umożliwiać budowanie z klocków LEGO.
Aplikacja powinna umożliwiać dodawanie nowych modeli, śledzenie postępu układania oraz korzystać z ogólnodostępnej
bazy klocków. Każda instrukcja powinna być przetwarzana w celu automatycznego doboru klocków jeżeli są dostępne
w bazie danych.
Jak każda aplikacja ze śledzeniem postępu powinno być możliwe logowanie oraz kontynuowanie
pracy nad wybranym modelem.
Wyświetlanie powinno być zrealizowane z wykorzystaniem OpenGL.

Wykorzystywane techonlogie:
    - React.js
    - wykorzystanie biblioteki fiber/three.js
    - FAST API w pythonie do komunikacji z bazami danych
    - Python + Blender do wstępnego przetworzenia plików graficznych
    - Baza danych MySql i MongoDB

Wymagania:
Funkcjonalne:
    - rejestracja/logowania do aplikacji
    - zapis postępu w modelowaniu
    - możliwość posiadania kilku(?) zaczętych modeli
    - udostępnianie swoich modeli wraz z instrukcją (?)
    - wyświetlanie instrukcji na stronie
    - system posiada 2 tryby:
        - odtwarzanie modeli: w eksploratorze znajdują się tylko elementy niezbędne
        - tworzenie własnych: w eksploratorze znajdują się wszystkie elementy z możliwością filtrowania
    - możliwość nakładania materiału (koloru) na elementy
    - możliwość budowania w formie edytora:
        - przez przeciąganie elementów z eksploratora do edytora
        - udostępnienie w edytorze translacji w odpowiednich interwałach oraz rotacji o 90 stopni w każdym kierunku
        - udostępnienie skrótów klawiszowych do transalcji, rotacji, czy usuwanie elementów
    - dostęp do elementów z ogólnodostępnej bazy klocków
    - możliwość oceniania modeli innych użytkowników

Niefunkcjonalne:
    - nie musi być przystosowana do urządzeń mobilnych
    - umożliwienie edycji dużych modeli do x elementów



Baza danych mysql:
- parts (zawiera nazwy elementów do filtrowania)
- colors (oficjalne kolory)

----------------------------------------------
JEZELI BEDE KORZYSTAL Z OFICJALNYCH INSTRUKCJI
- inventory_parts
- sets
- thumbnails
----------------------------------------------

Baza danych mongo:

Użytkownik:
- id
- mail
- login
- password

Model:
- nazwa
- plik gltf

Postęp:
- id
- user_id
- thumbnail
- postęp w postaci pliku json:
- ewentualne podpięcie do modelu który się odtwarza

każdy wiersz jego posiada: id, model, pozycję, rotację, kolor

Dodatkowo potrzebuję jakoś tabelę do odtwarzania modeli zawierająca:
- id
- nazwa
- user_id = None
- lista postępów czyli tabela pośrednia


i jakaś tabela Review zawierająca:
- model_id
- user_id
- rating
- comment

W odtwarzaniu modelu:
porównywanie postępu w plikach json i sprawdzanie różnic pomiędzy
względnym położeniem (relative location) obiektów w scenie oraz ich rotacji.
