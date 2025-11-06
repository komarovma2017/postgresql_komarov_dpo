"""Главный модуль приложения для управления турами.
Комаров М.А. DPO 17 Варинат города и экскурсии.
"""
import sys

sys.path.append("tables")

from project_config import ProjectConfig
from dbconnection import DbConnection
from city_table import CityTable
from route_table import RouteTable
from dbtable import DbTable


class Main:
    """Главный класс приложения."""

    config = ProjectConfig()
    connection = DbConnection(config)
    PAGE_SIZE = 10

    def __init__(self):
        """Инициализация приложения."""
        DbTable.dbconn = self.connection
        self.city_id = -1
        self.city_name = ""

    def db_init(self):
        """Инициализация таблиц."""
        ct = CityTable()
        rt = RouteTable()
        ct.create()
        rt.create()

    def db_insert_sample_data(self):
        """Вставка тестовых данных."""
        ct = CityTable()
        rt = RouteTable()

        ct.insert_one(["Москва"])
        ct.insert_one(["Санкт-Петербург"])
        ct.insert_one(["Казань"])
        ct.insert_one(["Сочи"])

        rt.insert_one([
            "Золотое кольцо",
            1,
            "Классический маршрут по древним городам России",
            15000.00,
        ])
        rt.insert_one([
            "Москва - Питер",
            1,
            "Две столицы за одну поездку",
            12000.00,
        ])
        rt.insert_one([
            "Белые ночи",
            2,
            "Романтический тур в период белых ночей",
            18000.00,
        ])
        rt.insert_one([
            "Казанский кремль",
            3,
            "Исторический центр Татарстана",
            8000.00,
        ])
        rt.insert_one([
            "Олимпийский Сочи",
            4,
            "Посещение олимпийских объектов",
            20000.00,
        ])

    def db_drop(self):
        """Удаление таблиц."""
        rt = RouteTable()
        ct = CityTable()
        rt.drop()
        ct.drop()

    def show_main_menu(self):
        """Отображение главного меню."""
        menu = """
╔════════════════════════════════════════════════════╗
║   СИСТЕМА УПРАВЛЕНИЯ ЭКСКУРСИОННЫМИ ТУРАМИ         ║
╚════════════════════════════════════════════════════╝

Основное меню:
  1 - Просмотр городов
  2 - Сброс и инициализация таблиц
  9 - Выход
"""
        print(menu)

    def read_next_step(self):
        """Чтение выбора пользователя."""
        return input("=> ").strip()

    def after_main_menu(self, next_step):
        """Обработка выбора в главном меню."""
        if next_step == "2":
            confirm = input(
                "Вы уверены? Все данные будут удалены! (да/нет): "
            ).strip().lower()
            if confirm in ("да", "yes"):
                self.db_drop()
                self.db_init()
                self.db_insert_sample_data()
                print("\n✓ Таблицы созданы заново с тестовыми данными!\n")
            else:
                print("Операция отменена.")
            return "0"
        elif next_step not in ("1", "9"):
            print("\n✗ Выбрано неверное число! Повторите ввод!\n")
            return "0"
        return next_step

    def show_cities(self, page=1):
        """Просмотр списка городов с пагинацией."""
        ct = CityTable()
        total_count = ct.count()
        total_pages = max(
            1, (total_count + self.PAGE_SIZE - 1) // self.PAGE_SIZE
        )

        page = max(1, min(page, total_pages))
        offset = (page - 1) * self.PAGE_SIZE

        print("\n" + "=" * 60)
        print("СПИСОК ГОРОДОВ")
        print("=" * 60)
        print(f"Страница {page} из {total_pages} | Всего: {total_count}")
        print("-" * 60)
        print(f"{'№':>3} | {'Название города':<50}")
        print("-" * 60)

        lst = ct.all(limit=self.PAGE_SIZE, offset=offset)
        for idx, city in enumerate(lst, start=1):
            print(f"{idx:>3} | {city[1]:<50}")

        print("-" * 60)

        menu = """
Операции:
  0 - Возврат в главное меню
  3 - Добавить новый город
  4 - Редактировать город
  5 - Удалить город
  6 - Просмотреть маршруты города"""

        if total_pages > 1:
            menu += "\n  [ - Предыдущая страница"
            menu += "\n  ] - Следующая страница"

        menu += "\n  9 - Выход\n"
        print(menu)

        return page, total_pages

    def after_show_cities(self, next_step, page, total_pages):
        """Обработка выбора в меню городов."""
        if next_step == "3":
            self.show_add_city()
            return "1", 1
        elif next_step == "4":
            self.show_edit_city()
            return "1", page
        elif next_step == "5":
            self.show_delete_city()
            return "1", page
        elif next_step == "6":
            next_step = self.show_routes_by_city()
            if next_step == "1":
                return "1", page
            elif next_step == "0":
                return "0", 1
            elif next_step == "9":
                return "9", 1
        elif next_step == "[" and page > 1:
            return "1", page - 1
        elif next_step == "]" and page < total_pages:
            return "1", page + 1
        elif next_step not in ("0", "9"):
            print("\n✗ Выбрано неверное действие! Повторите ввод!\n")
            return "1", page
        return next_step, 1

    def show_add_city(self):
        """Добавление нового города."""
        print("\n--- ДОБАВЛЕНИЕ НОВОГО ГОРОДА ---")
        name = input("Введите название города (0 - отмена): ").strip()

        if name == "0":
            print("Операция отменена.")
            return

        while len(name) == 0:
            name = input(
                "Название не может быть пустым! "
                "Введите название (0 - отмена): "
            ).strip()
            if name == "0":
                print("Операция отменена.")
                return

        ct = CityTable()
        if ct.insert_one([name]):
            print(f"\n✓ Город '{name}' успешно добавлен!\n")

    def show_edit_city(self):
        """Редактирование города."""
        print("\n--- РЕДАКТИРОВАНИЕ ГОРОДА ---")
        num = input(
            "Укажите номер строки города для редактирования "
            "(0 - отмена): "
        ).strip()

        if num == "0":
            print("Операция отменена.")
            return

        try:
            num = int(num)
        except ValueError:
            print("✗ Введено некорректное число!")
            return

        ct = CityTable()
        city = ct.find_by_position(num)

        if not city:
            print("✗ Город с таким номером не найден!")
            return

        print(f"\nТекущее название: {city[1]}")
        new_name = input(
            "Введите новое название "
            "(0 - отмена, Enter - оставить без изменений): "
        ).strip()

        if new_name == "0":
            print("Операция отменена.")
            return

        if new_name == "":
            new_name = city[1]

        if ct.update_by_id(city[0], [new_name]):
            print("\n✓ Город успешно обновлен!\n")

    def show_delete_city(self):
        """Удаление города."""
        print("\n--- УДАЛЕНИЕ ГОРОДА ---")
        num = input(
            "Укажите номер строки города для удаления (0 - отмена): "
        ).strip()

        if num == "0":
            print("Операция отменена.")
            return

        try:
            num = int(num)
        except ValueError:
            print("✗ Введено некорректное число!")
            return

        ct = CityTable()
        city = ct.find_by_position(num)

        if not city:
            print("✗ Город с таким номером не найден!")
            return

        print(f"\nВы действительно хотите удалить город '{city[1]}'?")
        confirm = input(
            "Подтвердите удаление (да/нет): "
        ).strip().lower()

        if confirm in ("да", "yes"):
            if ct.delete_by_id(city[0]):
                print(f"\n✓ Город '{city[1]}' успешно удален!\n")
        else:
            print("Удаление отменено.")

    def show_routes_by_city(self, page=1):
        """Просмотр маршрутов для выбранного города."""
        if self.city_id == -1:
            num = input(
                "\nУкажите номер строки города (0 - отмена): "
            ).strip()

            if num == "0":
                return "1"

            try:
                num = int(num)
            except ValueError:
                print("✗ Введено некорректное число!")
                return "1"

            ct = CityTable()
            city = ct.find_by_position(num)

            if not city:
                print("✗ Город с таким номером не найден!")
                return "1"

            self.city_id = city[0]
            self.city_name = city[1]

        rt = RouteTable()
        total_count = rt.count_by_city_id(self.city_id)
        total_pages = max(
            1, (total_count + self.PAGE_SIZE - 1) // self.PAGE_SIZE
        )

        page = max(1, min(page, total_pages))
        offset = (page - 1) * self.PAGE_SIZE

        print("\n" + "=" * 80)
        print(f"МАРШРУТЫ ИЗ ГОРОДА: {self.city_name}")
        print("=" * 80)
        print(f"Страница {page} из {total_pages} | Всего: {total_count}")
        print("-" * 80)
        print(
            f"{'№':>3} | {'Название':<30} | "
            f"{'Описание':<30} | {'Цена (руб.)':<10}"
        )
        print("-" * 80)

        routes = rt.all_by_city_id(
            self.city_id, limit=self.PAGE_SIZE, offset=offset
        )

        if not routes:
            print("  Маршруты для этого города отсутствуют.")
        else:
            for idx, route in enumerate(routes, start=1):
                desc = route[3] if route[3] else "Нет описания"
                if len(desc) > 30:
                    desc = desc[:27] + "..."
                price = float(route[4])
                print(
                    f"{idx:>3} | {route[1]:<30} | "
                    f"{desc:<30} | {price:>10.2f}"
                )

        print("-" * 80)

        menu = """
Операции:
  0 - Возврат в главное меню
  1 - Возврат к списку городов
  7 - Добавить новый маршрут
  8 - Редактировать маршрут
  9 - Удалить маршрут"""

        if total_pages > 1:
            menu += "\n  [ - Предыдущая страница"
            menu += "\n  ] - Следующая страница"

        menu += "\n"
        print(menu)

        while True:
            next_step = self.read_next_step()

            if next_step == "7":
                self.show_add_route()
                return self.show_routes_by_city(page)
            elif next_step == "8":
                self.show_edit_route()
                return self.show_routes_by_city(page)
            elif next_step == "9":
                self.show_delete_route()
                return self.show_routes_by_city(page)
            elif next_step == "[" and page > 1:
                return self.show_routes_by_city(page - 1)
            elif next_step == "]" and page < total_pages:
                return self.show_routes_by_city(page + 1)
            elif next_step == "1":
                self.city_id = -1
                return "1"
            elif next_step == "0":
                self.city_id = -1
                return "0"
            elif next_step == "exit":
                self.city_id = -1
                return "9"
            else:
                print("✗ Выбрано неверное действие! Повторите ввод!")

    def show_add_route(self):
        """Добавление нового маршрута."""
        print("\n--- ДОБАВЛЕНИЕ НОВОГО МАРШРУТА ---")

        name = input("Введите название маршрута (0 - отмена): ").strip()
        if name == "0":
            print("Операция отменена.")
            return

        while len(name) == 0:
            name = input(
                "Название не может быть пустым! "
                "Повторите ввод (0 - отмена): "
            ).strip()
            if name == "0":
                print("Операция отменена.")
                return

        description = input(
            "Введите описание маршрута (необязательно, 0 - отмена): "
        ).strip()
        if description == "0":
            print("Операция отменена.")
            return

        base_price = input(
            "Введите базовую цену в рублях (0 - отмена): "
        ).strip()
        if base_price == "0":
            print("Операция отменена.")
            return

        try:
            base_price = float(base_price)
            if base_price < 0:
                print("✗ Цена не может быть отрицательной!")
                return
        except ValueError:
            print("✗ Некорректное значение цены!")
            return

        rt = RouteTable()
        route_data = [
            name,
            self.city_id,
            description if description else None,
            base_price,
        ]
        if rt.insert_one(route_data):
            print(f"\n✓ Маршрут '{name}' успешно добавлен!\n")

    def show_edit_route(self):
        """Редактирование маршрута."""
        print("\n--- РЕДАКТИРОВАНИЕ МАРШРУТА ---")
        num = input(
            "Укажите номер строки маршрута для редактирования "
            "(0 - отмена): "
        ).strip()

        if num == "0":
            print("Операция отменена.")
            return

        try:
            num = int(num)
        except ValueError:
            print("✗ Введено некорректное число!")
            return

        rt = RouteTable()
        route = rt.find_route_by_position_and_city(self.city_id, num)

        if not route:
            print("✗ Маршрут с таким номером не найден!")
            return

        print(f"\nТекущее название: {route[1]}")
        new_name = input(
            "Введите новое название "
            "(Enter - без изменений, 0 - отмена): "
        ).strip()
        if new_name == "0":
            print("Операция отменена.")
            return
        if new_name == "":
            new_name = route[1]

        print(f"\nТекущее описание: {route[3] if route[3] else 'Нет'}")
        new_description = input(
            "Введите новое описание "
            "(Enter - без изменений, 0 - отмена): "
        ).strip()
        if new_description == "0":
            print("Операция отменена.")
            return
        if new_description == "":
            new_description = route[3]

        print(f"\nТекущая цена: {float(route[4]):.2f} руб.")
        new_price = input(
            "Введите новую цену "
            "(Enter - без изменений, 0 - отмена): "
        ).strip()
        if new_price == "0":
            print("Операция отменена.")
            return
        if new_price == "":
            new_price = float(route[4])
        else:
            try:
                new_price = float(new_price)
                if new_price < 0:
                    print("✗ Цена не может быть отрицательной!")
                    return
            except ValueError:
                print("✗ Некорректное значение цены!")
                return

        route_data = [new_name, self.city_id, new_description, new_price]
        if rt.update_by_id(route[0], route_data):
            print("\n✓ Маршрут успешно обновлен!\n")

    def show_delete_route(self):
        """Удаление маршрута."""
        print("\n--- УДАЛЕНИЕ МАРШРУТА ---")
        num = input(
            "Укажите номер строки маршрута для удаления (0 - отмена): "
        ).strip()

        if num == "0":
            print("Операция отменена.")
            return

        try:
            num = int(num)
        except ValueError:
            print("✗ Введено некорректное число!")
            return

        rt = RouteTable()
        route = rt.find_route_by_position_and_city(self.city_id, num)

        if not route:
            print("✗ Маршрут с таким номером не найден!")
            return

        print(f"\nВы действительно хотите удалить маршрут '{route[1]}'?")
        confirm = input(
            "Подтвердите удаление (да/нет): "
        ).strip().lower()

        if confirm in ("да", "yes"):
            if rt.delete_by_id(route[0]):
                print(f"\n✓ Маршрут '{route[1]}' успешно удален!\n")
        else:
            print("Удаление отменено.")

    def main_cycle(self):
        """Основной цикл программы."""
        current_menu = "0"
        next_step = None
        current_page = 1

        while current_menu != "9":
            if current_menu == "0":
                self.show_main_menu()
                next_step = self.read_next_step()
                current_menu, current_page = (
                    self.after_main_menu(next_step),
                    1,
                )
            elif current_menu == "1":
                current_page, total_pages = self.show_cities(current_page)
                next_step = self.read_next_step()
                current_menu, current_page = self.after_show_cities(
                    next_step, current_page, total_pages
                )

        print("\n" + "=" * 60)
        print("До свидания! Спасибо за использование системы!")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    m = Main()
    m.main_cycle()
