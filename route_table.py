"""Модуль для работы с таблицей маршрутов."""
from dbtable import DbTable


class RouteTable(DbTable):
    """Класс для работы с таблицей маршрутов."""

    def table_name(self):
        """Получение имени таблицы маршрутов."""
        return self.dbconn.prefix + "route"

    def columns(self):
        """Структура таблицы маршрутов."""
        return {
            "id": ["SERIAL", "PRIMARY KEY"],
            "name": ["VARCHAR(255)", "NOT NULL"],
            "departure_city_id": [
                "INT",
                "NOT NULL",
                "REFERENCES city(id)",
            ],
            "description": ["TEXT"],
            "base_price": [
                "NUMERIC(10, 2)",
                "NOT NULL",
                "CHECK (base_price >= 0)",
            ],
        }

    def validate_route_data(self, vals):
        """Валидация данных маршрута."""
        name, city_id, description, base_price = vals

        if not name or len(name.strip()) == 0:
            return False, "Название маршрута не может быть пустым!"
        if len(name) > 255:
            return False, "Название слишком длинное (максимум 255)!"

        if not isinstance(city_id, int) or city_id <= 0:
            return False, "Некорректный ID города!"

        sql = f"SELECT COUNT(*) FROM {self.dbconn.prefix}city WHERE id = %s"
        cur = self.dbconn.conn.cursor()
        cur.execute(sql, (city_id,))
        if cur.fetchone()[0] == 0:
            return False, "Указанный город не существует!"

        if description and len(description) > 5000:
            return False, "Описание слишком длинное (максимум 5000)!"

        try:
            price = float(base_price)
            if price < 0:
                return False, "Цена не может быть отрицательной!"
        except (ValueError, TypeError):
            return False, "Некорректное значение цены!"

        return True, ""

    def insert_one(self, vals):
        """Вставка маршрута с валидацией."""
        valid, error = self.validate_route_data(vals)
        if not valid:
            print(error)
            return False
        return super().insert_one(vals)

    def update_by_id(self, id_val, vals):
        """Обновление маршрута с валидацией."""
        valid, error = self.validate_route_data(vals)
        if not valid:
            print(error)
            return False
        return super().update_by_id(id_val, vals)

    def all_by_city_id(self, city_id, limit=None, offset=None):
        """Получение маршрутов для города."""
        sql = (
            f"SELECT r.*, c.name as city_name "
            f"FROM {self.table_name()} r "
            f"JOIN {self.dbconn.prefix}city c "
            "ON r.departure_city_id = c.id "
            "WHERE r.departure_city_id = %s "
            "ORDER BY r.id"
        )
        params = [city_id]
        if limit is not None:
            sql += " LIMIT %s"
            params.append(limit)
            if offset is not None:
                sql += " OFFSET %s"
                params.append(offset)

        cur = self.dbconn.conn.cursor()
        try:
            cur.execute(sql, params)
            return cur.fetchall()
        except Exception as e:
            print(f"Ошибка получения маршрутов: {e}")
            return []

    def count_by_city_id(self, city_id):
        """Подсчет маршрутов для города."""
        sql = (
            f"SELECT COUNT(*) FROM {self.table_name()} "
            "WHERE departure_city_id = %s"
        )
        cur = self.dbconn.conn.cursor()
        cur.execute(sql, (city_id,))
        result = cur.fetchone()
        return result[0] if result else 0

    def find_route_by_position_and_city(self, city_id, position):
        """Получение маршрута по позиции для города."""
        sql = (
            f"SELECT r.*, c.name as city_name "
            f"FROM {self.table_name()} r "
            f"JOIN {self.dbconn.prefix}city c "
            "ON r.departure_city_id = c.id "
            "WHERE r.departure_city_id = %s "
            "ORDER BY r.id "
            "LIMIT 1 OFFSET %s"
        )
        cur = self.dbconn.conn.cursor()
        try:
            cur.execute(sql, (city_id, position - 1))
            return cur.fetchone()
        except Exception as e:
            print(f"Ошибка получения маршрута: {e}")
            return None
