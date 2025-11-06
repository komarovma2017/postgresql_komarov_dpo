"""Базовый класс для работы с таблицами базы данных."""
from dbconnection import DbConnection


class DbTable:
    """Базовый класс для операций с таблицами БД."""

    dbconn: DbConnection | None = None

    def __init__(self):
        """Инициализация объекта таблицы."""

    def table_name(self):
        """Получение имени таблицы."""
        return self.dbconn.prefix + "table"

    def columns(self):
        """Определение структуры колонок таблицы."""
        return {"test": ["integer", "PRIMARY KEY"]}

    def column_names(self):
        """Получение списка имен всех колонок."""
        return sorted(self.columns().keys())

    def primary_key(self):
        """Получение списка колонок первичного ключа."""
        return ["id"]

    def column_names_without_id(self):
        """Получение списка колонок без ID."""
        res = sorted(self.columns().keys())
        if "id" in res:
            res.remove("id")
        return res

    def table_constraints(self):
        """Получение дополнительных ограничений таблицы."""
        return []

    def create(self):
        """Создание таблицы в базе данных."""
        sql = "CREATE TABLE IF NOT EXISTS " + self.table_name() + "("
        arr = [
            k + " " + " ".join(v)
            for k, v in sorted(self.columns().items())
        ]
        sql += ", ".join(arr + self.table_constraints())
        sql += ")"
        cur = self.dbconn.conn.cursor()
        try:
            cur.execute(sql)
            self.dbconn.conn.commit()
        except Exception as e:
            self.dbconn.conn.rollback()
            print(f"Ошибка создания таблицы: {e}")

    def drop(self):
        """Удаление таблицы из базы данных."""
        sql = f"DROP TABLE IF EXISTS {self.table_name()} CASCADE"
        cur = self.dbconn.conn.cursor()
        try:
            cur.execute(sql)
            self.dbconn.conn.commit()
        except Exception as e:
            self.dbconn.conn.rollback()
            print(f"Ошибка удаления таблицы: {e}")

    def insert_one(self, vals):
        """Вставка одной записи в таблицу."""
        cols = self.column_names_without_id()
        placeholders = ", ".join(["%s"] * len(vals))
        sql = (
            f"INSERT INTO {self.table_name()} "
            f"({', '.join(cols)}) VALUES ({placeholders})"
        )
        cur = self.dbconn.conn.cursor()
        try:
            cur.execute(sql, vals)
            self.dbconn.conn.commit()
            return True
        except Exception as e:
            self.dbconn.conn.rollback()
            print(f"Ошибка вставки данных: {e}")
            return False

    def update_by_id(self, id_val, vals):
        """Обновление записи по ID."""
        cols = self.column_names_without_id()
        set_clause = ", ".join([f"{col} = %s" for col in cols])
        sql = f"UPDATE {self.table_name()} SET {set_clause} WHERE id = %s"
        cur = self.dbconn.conn.cursor()
        try:
            cur.execute(sql, list(vals) + [id_val])
            self.dbconn.conn.commit()
            return True
        except Exception as e:
            self.dbconn.conn.rollback()
            print(f"Ошибка обновления данных: {e}")
            return False

    def delete_by_id(self, id_val):
        """Удаление записи по ID."""
        sql = f"DELETE FROM {self.table_name()} WHERE id = %s"
        cur = self.dbconn.conn.cursor()
        try:
            cur.execute(sql, (id_val,))
            self.dbconn.conn.commit()
            return True
        except Exception as e:
            self.dbconn.conn.rollback()
            print(f"Ошибка удаления данных: {e}")
            return False

    def all(self, limit=None, offset=None):
        """Получение всех записей с поддержкой пагинации."""
        sql = (
            f"SELECT * FROM {self.table_name()} "
            f"ORDER BY {', '.join(self.primary_key())}"
        )
        params = []
        if limit is not None:
            sql += " LIMIT %s"
            params.append(limit)
            if offset is not None:
                sql += " OFFSET %s"
                params.append(offset)
        
        cur = self.dbconn.conn.cursor()
        try:
            cur.execute(sql, params) if params else cur.execute(sql)
            return cur.fetchall()
        except Exception as e:
            print(f"Ошибка получения данных: {e}")
            return []

    def count(self):
        """Подсчет общего количества записей."""
        sql = f"SELECT COUNT(*) FROM {self.table_name()}"
        cur = self.dbconn.conn.cursor()
        cur.execute(sql)
        result = cur.fetchone()
        return result[0] if result else 0

    def find_by_position(self, num):
        """Получение записи по позиции."""
        sql = (
            f"SELECT * FROM {self.table_name()} "
            f"ORDER BY {', '.join(self.primary_key())} "
            "LIMIT 1 OFFSET %s"
        )
        cur = self.dbconn.conn.cursor()
        try:
            cur.execute(sql, (num - 1,))
            return cur.fetchone()
        except Exception as e:
            print(f"Ошибка получения записи: {e}")
            return None
