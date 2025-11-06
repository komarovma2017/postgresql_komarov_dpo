"""Модуль для работы с таблицей городов."""
from dbtable import DbTable


class CityTable(DbTable):
    """Класс для работы с таблицей городов."""

    def table_name(self):
        """Получение имени таблицы городов."""
        return self.dbconn.prefix + "city"

    def columns(self):
        """Структура таблицы городов."""
        return {
            "id": ["SERIAL", "PRIMARY KEY"],
            "name": ["VARCHAR(100)", "NOT NULL", "UNIQUE"],
        }

    def validate_city_name(self, name):
        """Валидация названия города."""
        if not name or len(name.strip()) == 0:
            return False, "Название города не может быть пустым!"
        if len(name) > 100:
            return False, "Название слишком длинное (максимум 100)!"
        return True, ""

    def check_city_exists(self, name):
        """Проверка существования города."""
        sql = f"SELECT COUNT(*) FROM {self.table_name()} WHERE name = %s"
        cur = self.dbconn.conn.cursor()
        cur.execute(sql, (name,))
        result = cur.fetchone()
        return result[0] > 0

    def insert_one(self, vals):
        """Вставка города с валидацией."""
        valid, error = self.validate_city_name(vals[0])
        if not valid:
            print(error)
            return False
        if self.check_city_exists(vals[0]):
            print("Город с таким названием уже существует!")
            return False
        return super().insert_one(vals)

    def update_by_id(self, id_val, vals):
        """Обновление города с валидацией."""
        valid, error = self.validate_city_name(vals[0])
        if not valid:
            print(error)
            return False
        sql = (
            f"SELECT COUNT(*) FROM {self.table_name()} "
            "WHERE name = %s AND id != %s"
        )
        cur = self.dbconn.conn.cursor()
        cur.execute(sql, (vals[0], id_val))
        if cur.fetchone()[0] > 0:
            print("Город с таким названием уже существует!")
            return False
        return super().update_by_id(id_val, vals)

    def delete_by_id(self, id_val):
        """Удаление города с проверкой связей."""
        sql = (
            f"SELECT COUNT(*) FROM {self.dbconn.prefix}route "
            "WHERE departure_city_id = %s"
        )
        cur = self.dbconn.conn.cursor()
        cur.execute(sql, (id_val,))
        count = cur.fetchone()[0]
        if count > 0:
            print(
                f"Невозможно удалить: существует {count} маршрут(ов)!"
            )
            print("Сначала удалите связанные маршруты.")
            return False
        return super().delete_by_id(id_val)
