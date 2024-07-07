
W ramach tematu należy zbudować aplikację webową/mobilną, która będzie umożliwiać budowanie z klocków LEGO.
Aplikacja powinna umożliwiać dodawanie nowych modeli, śledzenie postępu układania oraz korzystać z ogólnodostępnej
bazy klocków. Każda instrukcja powinna być przetwarzana w celu automatycznego doboru klocków jeżeli są dostępne
w bazie danych.
Jak każda aplikacja ze śledzeniem postępu powinno być możliwe logowanie oraz kontynuowanie
pracy nad wybranym modelem.
Wyświetlanie powinno być zrealizowane z wykorzystaniem OpenGL.

Wykorzystywane techonlogie:
    - React.js
    - wykorzystanie biblioteki ...
    - API w pythonie do komunikacji z bazami danych
    - Python + Blender do wstępnego przetworzenia plików graficznych
    - Baza danych MySql i MongoDB

Wymagania:
Funkcjonalne:
    - rejestracja/logowania do aplikacji
    - zapis postępu w modelowaniu
    - możliwość posiadania kilku(?) zaczętych modeli
    - udostępnianie swoich modeli wraz z instrukcją (?)
    - wyświetlanie instrukcji na stronie
    - system posiada 2 tryby:Z
        - odtwarzanie modeli: w eksploratorze znajdują się tylko elementy niezbędne
        - tworzenie własnych: w eksploratorze znajdują się wszystkie elementy z możliwością filtrowania
    - możliwość nakładania materiału (koloru) na elementy
    - możliwość budowania w formie edytora:
        - przez przeciąganie elementów z eksploratora do edytora
        - translacje w edytorze w 2 wymiarach, 3 wymiar pionowy będzie wyrównywany elementów do najwyższego punktu od płaszczyzny (tzn. nie mogą unosić się elementy w powietrzu tylko muszą być albo na samym dole lub przyczepione do inngeo)
        - rotacja elementów w dwóch wymiarach (lewo/prawo i góra/dół)
        - udostępnienie skrótów klawiszowych do transalcji, rotacji, czy usuwanie elementów
    - dostęp do elementów z ogólnodostępnej bazy klocków
    - możliwość oceniania modeli innych użytkowników

Niefunkcjonalne:
    - nie musi być przystosowana do urządzeń mobilnych
    - umożliwienie edycji dużych modeli do x elementów


Database design:
- User{
    user_id
    login
    password
    mail
}

- Model{
    model_id
    inventory_id
    author_id(user)
    rating (0-5)
}

śledzenie postępu:

- przechowywania pozycji jednego z wierzchołków w przestrzeni xyz i rotacja, nie wiem czy mam dostępne w bazie wielkości elementów
- wskaźniki pomiędzy elementami połączonymi input/output


pliki gltf muszą się nazywać tak jak część


GLTF i Clone żeby nie wczytywać ten sam obiekt parę razy


- góra dół poprawnie przesuwanie
- czy da się wyrównywać żeby zaczynały się na płaszczyźnie
- ograniczyć kamerę żeby nie mogła iść pod spód
napotkane problemy:
- obrót jest w okół środka domyślny powinien być wokół wierzchowłka. Problemem jest że w okół środka jest obrót
- nie wszystkie modele mają te same położenie.
mam dostępne w pliku gltf współrzędne modelowaniu może na podstawie tego będę mógł wyrównwywać


zmienić id ustawiane bo przy usunięciu może się nadpisać

Zrobione:
-zapisywanie do pliku
- dodawanie obrotu do zapisu

Baza danych:

- zapisywanie postępu na podstawie pliku json:


Tabele:

Użytkownik:
- id
- mail
- login
- password

Model:
- id
- nazwa
- plik gltf
- link do podglądu obrazu

Postęp:
- id
- user_id
- thumbnail
- postęp w postaci pliku json:
każdy wiersz jego posiada: id, model, pozycję, rotację, kolor

W odtwarzaniu modelu:
porównywanie postępu w plikach json i sprawdzanie różnic pomiędzy
względnym położeniem (relative location) obiektów w scenie oraz ich rotacji.

Do logowania użytkowników gotowy komponent:
auth0 lub keycloak, userfront https://userfront.com/docs/toolkit/install/login-form-react

●	Elements lazy loading
●	we should stream elements when they are needed
wczytawanie określonej maksymalnej liczby elementów do wyboru z listy:
wczytanie modelu w momencie pierwszego dodawania do sceny w przypadku tworzenia modelu:
gdy odtwarzany model to wczytuje wszystkie elementy (może z ekranem loadingu), które mają zostać użyte.

ekran loadingu dodać na samym elemencie może

Zdockeryzować
elastic search
mongo zrobić lokalnie bo chmurowe jest za małe


Napotkange bugi:
z czasem program działa coraz wolniej, wyciek pamięci?
Problemy:
przy wczytaniu ma się dopasować do odpowieniego step

TODO w pythonie:


20 to przesunięcie poziome
8 to przesunięcie pionowe

aby obliczać położenie klocków:
z bazy danych bierzemy wymiary (dla pozostałych coś innego wymyślić)
dzielimy je na 2 i w ten sposób możemy obliczyć położenie każdej wypustki
potem sprawdzić czy pod nią jest jakiś element co będzie funkcją rekurencyjną na razie niech to koloruje elementy na inny kolor lub przezroczystość dodać

dodać do tego co znaczy dla tego obrót o 90 stopni



w mysqldb zostały utworzony plik csv z klockami które nie mają preview. Należy coś z nimi zrobić i pamiętać że zestawy pewnie z nich korzystają. Plik: without_thumbnail

ustawianie begin_position i modelu dwukrtonie odwołuje się do api