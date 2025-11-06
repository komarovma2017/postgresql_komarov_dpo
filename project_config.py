"""Модуль для чтения конфигурации проекта из YAML файла."""
import yaml


class ProjectConfig:
    """Класс для работы с конфигурацией проекта."""

    config_path = "config.yaml"

    def __init__(self):
        """Загрузка конфигурации из YAML файла."""
        with open(self.config_path) as f:
            config = yaml.safe_load(f)
            self.dbname = config["dbname"]
            self.user = config["user"]
            self.password = config["password"]
            self.host = config["host"]
            self.dbtableprefix = config["dbtableprefix"]
