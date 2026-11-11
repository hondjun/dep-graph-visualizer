"""Тесты валидации конфигурации приложения."""

import json
import tempfile
import unittest
from pathlib import Path

from src.config import ConfigError, parse_config

class TestConfigValidation(unittest.TestCase):
    """Набор тестов для проверки обработки ошибок параметров."""

    def setUp(self) -> None:
        """Создает базовый валидный конфиг во временной директории."""
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.cfg_path = Path(self.tmp_dir.name) / "config.json"
        self.valid_data = {
            "package_name": "curl",
            "repo_url": "http://archive.ubuntu.com/ubuntu",
            "test_mode": False,
            "package_version": "8.5.0",
            "output_file": "graph.png",
            "ascii_tree": False,
            "max_depth": 2,
            "filter_substring": "",
        }

    def tearDown(self) -> None:
        """Удаляет временную директорию."""
        self.tmp_dir.cleanup()

    def write_cfg(self, data: dict) -> str:
        """Записывает словарь в JSON-файл и возвращает путь."""
        self.cfg_path.write_text(json.dumps(data), encoding="utf-8")
        return str(self.cfg_path)

    def test_valid_config(self) -> None:
        """Проверяет успешную загрузку корректного конфига."""
        path = self.write_cfg(self.valid_data)
        result = parse_config(path)
        self.assertEqual(result["package_name"], "curl")

    def test_missing_key(self) -> None:
        """Проверяет ошибку при отсутствии обязательного ключа."""
        del self.valid_data["package_version"]
        path = self.write_cfg(self.valid_data)
        with self.assertRaises(ConfigError):
            parse_config(path)

    def test_invalid_type(self) -> None:
        """Проверяет ошибку при неверном типе значения."""
        self.valid_data["max_depth"] = "three"
        path = self.write_cfg(self.valid_data)
        with self.assertRaises(ConfigError):
            parse_config(path)

    def test_invalid_depth_value(self) -> None:
        """Проверяет ошибку при глубине меньше допустимой."""
        self.valid_data["max_depth"] = 0
        path = self.write_cfg(self.valid_data)
        with self.assertRaises(ConfigError):
            parse_config(path)

    def test_missing_test_repo_file(self) -> None:
        """Проверяет ошибку при несуществующем файле в тестовом режиме."""
        self.valid_data["test_mode"] = True
        self.valid_data["repo_url"] = "non_existent_repo.txt"
        path = self.write_cfg(self.valid_data)
        with self.assertRaises(ConfigError):
            parse_config(path)


if __name__ == "__main__":
    unittest.main()