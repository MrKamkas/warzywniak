import sqlite3
from tabulate import tabulate


# Funkcja do wyświetlania produktów
def show_products():
    conn = sqlite3.connect('warzywniak_sklep.db')
    cur = conn.cursor()

    query = "SELECT * FROM Lista_produktow"
    cur.execute(query)

    rows = cur.fetchall()
    conn.close()

    if rows:
        headers = ["ID_produktu", "Nazwa_produktu", "Ilość", "Cena", "ID_Dostawcy", "ID_Opis"]
        print(tabulate(rows, headers, tablefmt="psql"))
    else:
        print("Brak produktów w bazie danych.")


def shopping():
    conn = sqlite3.connect('warzywniak_sklep.db')
    cur = conn.cursor()

    user_id = input("Podaj swoje ID_user (np. 001): ")

    # Sprawdzanie, czy ID użytkownika istnieje
    cur.execute("SELECT * FROM Users WHERE ID_user = ?", (user_id,))
    user = cur.fetchone()

    if not user:
        print("Nie znaleziono takiego użytkownika.")
        return

    print(f"Zapraszamy na zakupy, {user[1]} {user[2]}!")

    total_cost = 0
    purchased_items = []

    while True:
        # Wyświetlanie dostępnych produktów
        show_products()

        # Klient wybiera produkt i ilość
        product_id = input("Podaj ID produktu, który chcesz kupić: ")
        quantity = int(input("Podaj ilość: "))

        # Sprawdzanie, czy produkt istnieje i jest dostępny w odpowiedniej ilości
        cur.execute("SELECT * FROM Lista_produktow WHERE ID_produktu = ?", (product_id,))
        product = cur.fetchone()

        if not product:
            print("Nie znaleziono takiego produktu.")
            continue

        available_quantity = product[2]  # Ilość produktu
        product_price = product[3]  # Cena produktu

        if quantity > available_quantity:
            print(f"Przepraszamy, mamy tylko {available_quantity} sztuk tego produktu.")
            continue

        # Aktualizacja ilości w magazynie
        new_quantity = available_quantity - quantity
        cur.execute("UPDATE Lista_produktow SET ilosc_produktu = ? WHERE ID_produktu = ?", (new_quantity, product_id))

        # Dodanie zamówienia do tabeli Zamowienia
        cur.execute("""
            INSERT INTO Zamowienia (ID_klienta, ID_towaru, Data_zamowienia, Status_zamowienia) 
            VALUES (?, ?, DATE('now'), 'Wysłane')
        """, (user_id, product_id))

        # Dodanie do podsumowania zakupów
        total_cost += product_price * quantity
        purchased_items.append((product[1], quantity, product_price * quantity))

        # Pytanie, czy to wszystko
        another = input("Czy to wszystko? (Tak/Nie): ").strip().lower()
        if another == "tak":
            break

    conn.commit()  # Zapisanie zmian do bazy danych
    conn.close()

    # Podsumowanie zakupów
    print("\nPodsumowanie zakupów:")
    for item in purchased_items:
        print(f"Produkt: {item[0]}, Ilość: {item[1]}, Koszt: {item[2]:.2f} PLN")
    print(f"Łączny koszt: {total_cost:.2f} PLN")


# Funkcje dla administracji (zarządzanie klientami)
def show_customers():
    conn = sqlite3.connect('warzywniak_sklep.db')
    cur = conn.cursor()

    query = "SELECT * FROM Users"
    cur.execute(query)

    rows = cur.fetchall()
    conn.close()

    if rows:
        headers = ["ID_user", "P_Imie", "P_Nazwisko", "P_Adres", "P_Telefon"]
        print(tabulate(rows, headers, tablefmt="psql"))
    else:
        print("Brak klientów w bazie danych.")


def add_customer():
    conn = sqlite3.connect('warzywniak_sklep.db')
    cur = conn.cursor()

    # Pobierz ostatni największy ID_user i zwiększ go o 1
    cur.execute("SELECT MAX(CAST(SUBSTR(ID_user, 1, 3) AS INTEGER)) FROM Users")
    max_id = cur.fetchone()[0]

    if max_id is None:
        new_id = '001'
    else:
        new_id = str(max_id + 1).zfill(3)

    name = input("Wprowadź imię: ")
    surname = input("Wprowadź nazwisko: ")
    address = input("Wprowadź adres: ")
    phone = input("Wprowadź numer telefonu: ")

    query = "INSERT INTO Users (ID_user, P_Imie, P_Nazwisko, P_Adres, P_Telefon) VALUES (?, ?, ?, ?, ?)"
    cur.execute(query, (new_id, name, surname, address, phone))

    conn.commit()
    conn.close()
    print(f"Klient {name} {surname} został dodany pomyślnie z ID {new_id}.")


def edit_customer():
    conn = sqlite3.connect('warzywniak_sklep.db')
    cur = conn.cursor()

    user_id = input("Podaj ID klienta do edycji: ")

    new_name = input("Wprowadź nowe imię: ")
    new_surname = input("Wprowadź nowe nazwisko: ")
    new_address = input("Wprowadź nowy adres: ")
    new_phone = input("Wprowadź nowy numer telefonu: ")

    query = "UPDATE Users SET P_Imie = ?, P_Nazwisko = ?, P_Adres = ?, P_Telefon = ? WHERE ID_user = ?"
    cur.execute(query, (new_name, new_surname, new_address, new_phone, user_id))

    conn.commit()
    conn.close()
    print(f"Dane klienta {user_id} zostały zaktualizowane.")


def delete_customer():
    conn = sqlite3.connect('warzywniak_sklep.db')
    cur = conn.cursor()

    user_id = input("Podaj ID klienta do usunięcia: ")

    query = "DELETE FROM Users WHERE ID_user = ?"
    cur.execute(query, (user_id,))

    conn.commit()
    conn.close()
    print(f"Klient {user_id} został usunięty.")

def pokaz_historie_zamowien():
    conn = sqlite3.connect('warzywniak_sklep.db')
    cur = conn.cursor()

    # Pobierz historię zamówień wraz z danymi klientów
    query = """
    SELECT Users.ID_user, Users.P_Imie, Users.P_Nazwisko, Zamowienia.ID_zam, Zamowienia.ID_towaru, Zamowienia.Data_zamowienia, Zamowienia.Status_zamowienia
    FROM Users
    JOIN Zamowienia ON Users.ID_user = Zamowienia.ID_klienta
    ORDER BY Users.ID_user
    """
    cur.execute(query)

    rows = cur.fetchall()
    conn.close()

    if rows:
        headers = ["ID_user", "P_Imie", "P_Nazwisko", "ID_zam", "ID_towaru", "Data_zamowienia", "Status_zamowienia"]
        print(tabulate(rows, headers, tablefmt="psql"))
    else:
        print("Brak zamówień w historii.")


# Funkcja do obsługi menu sklepu
def shop_menu():
    while True:
        print("\nSklep:")
        print("1. Wyświetl produkty")
        print("2. Zakupy")
        print("3. Wróć do strony głównej")
        print("4. Zakończ")

        choice = input("Wybierz opcję: ")

        if choice == "1":
            show_products()
        elif choice == "2":
            shopping()  # Nowa funkcja zakupów
        elif choice == "3":
            break
        elif choice == "4":
            exit()
        else:
            print("Nieprawidłowy wybór. Spróbuj ponownie.")


# Funkcja do obsługi administracji (wymaga hasła)
def admin_menu():
    password = "123"  # Ustawione hasło
    attempts = 0

    # Sprawdzenie hasła
    while attempts < 3:
        entered_password = input("Podaj hasło do administracji: ")
        if entered_password == password:
            print("Zalogowano pomyślnie!")
            while True:
                print("\nAdministracja:")
                print("1. Wyświetl klientów")
                print("2. Dodaj klienta")
                print("3. Edytuj klienta")
                print("4. Usuń klienta")
                print("5. Historia zamówień klientów")  # Nowa opcja
                print("6. Wróć do strony głównej")

                choice = input("Wybierz opcję: ")

                if choice == "1":
                    show_customers()
                elif choice == "2":
                    add_customer()
                elif choice == "3":
                    edit_customer()
                elif choice == "4":
                    delete_customer()
                elif choice == "5":
                    pokaz_historie_zamowien()  # Wywołanie funkcji z nową nazwą
                elif choice == "6":
                    break
                else:
                    print("Nieprawidłowy wybór. Spróbuj ponownie.")
            break
        else:
            attempts += 1
            print(f"Nieprawidłowe hasło. Próba {attempts} z 3.")
    else:
        print("Zbyt wiele nieudanych prób logowania. Wróć do strony głównej.")


# Główne menu programu
def main_menu():
    while True:
        print("\nWitaj! Wybierz działanie:")
        print("1. Sklep")
        print("2. Administracja")
        print("3. Zakończ")

        choice = input("Wybierz opcję: ")

        if choice == "1":
            shop_menu()
        elif choice == "2":
            admin_menu()
        elif choice == "3":
            break
        else:
            print("Nieprawidłowy wybór. Spróbuj ponownie.")


# Uruchomienie programu
if __name__ == "__main__":
    main_menu()
