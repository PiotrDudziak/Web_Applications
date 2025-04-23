# Editor Tras

Projekt to aplikacja Django umożliwiająca tworzenie i edycję tras, w której użytkownik może wybrać tło oraz dodawać i edytować punkty trasy. W projekcie wykorzystane są technologie:
- Python
- Django
- Django REST Framework
- Pillow

## Wymagania

- Python 3.x
- Django (np. wersja >=3.2, <4.0)
- Django REST Framework (np. wersja >=3.11.0)
- Pillow (np. wersja >=8.0.0)

## Instalacja

1. Sklonuj repozytorium i pobierz tylko folder `trasy` przy użyciu sparse-checkout:
   ```bash
   git clone --filter=blob:none --no-checkout https://github.com/PiotrDudziak/Web_Applications.git
   cd Web_Applications
   git sparse-checkout init --cone
   git sparse-checkout set trasy
   git checkout main
2. Utwórz i aktywuj wirtualne środowisko:
    python3 -m venv venv source venv/bin/activate
3. Zainstaluj zależności:
   pip install -r requirements.txt
4. Wykonaj migracje:
    python manage.py migrate
5. Utwórz początkowy plik migracji dla aplikacji editor:
    python manage.py makemigrations editor
6. Zastosuje migracje do bazy danych:
    python manage.py migrate editor
7. Uruchom serwer developerski:
    python manage.py runserver

## Uruchamianie testów

Testy jednostkowe można uruchomić poleceniem:
    python manage.py test

## Struktura projektu

- `manage.py` – Główny plik uruchomieniowy Django.
- Foldery głównych aplikacji, np. `editor`, `tests` oraz folder zawierający trasę.
- Pliki konfiguracyjne, np. `settings.py` oraz `requirements.txt`.
- Foldery zawierające szablony (templates) i pliki statyczne (static).

## Konfiguracja

Przed publikacją projektu usuń lub zastąp dane wrażliwe, takie jak klucz tajny (`SECRET_KEY`) czy dane dostępu do bazy danych.
W przypadku aplikacji Django możesz pominąć folder `migrations`, aby migracje były generowane ponownie na podstawie modeli.

## Dodatkowe informacje

Projekt umożliwia tworzenie tras za pomocą formularza, podgląd wybranego tła oraz zarządzanie punktami trasy przy pomocy AJAX. 
Plik README zawiera niezbędne informacje, aby uruchomić projekt lokalnie i zrozumieć jego strukturę.
