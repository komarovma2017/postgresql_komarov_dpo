"""Модуль для установки соединения с базой данных PostgreSQL."""
import psycopg2


class DbConnection:
    """Класс для управления подключением к базе данных."""

    def __init__(self, config):
        """Инициализация подключения к БД."""
        self.dbname = config.dbname
        self.user = config.user
        self.password = config.password
        self.host = config.host
        self.prefix = config.dbtableprefix
        self.conn = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
        )

    def __del__(self):
        """Закрытие соединения при удалении объекта."""
        if self.conn:
            self.conn.close()
