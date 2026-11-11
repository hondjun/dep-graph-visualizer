"""Модуль загрузки и валидации JSON-конфигурации."""

import json
from pathlib import Path
from typing import Any

MIN_DEPTH = 1
REQUIRED_KEYS = {
    "package_name": str,
    "repo_url": str,
    "test_mode": bool,
    "package_version": str,
    "output_file": str,
    "ascii_tree": bool,
    "max_depth": int,
    "filter_substring": str,
}


class ConfigError(Exception):
    """Исключение при ошибке чтения или валидации конфигурации."""


def load_json(config_path: str) -> dict[str, Any]:
    """Загружает JSON-файл и проверяет, что корень является словарем."""
    path = Path(config_path)
    if not path.is_file():
        raise ConfigError(f"Файл конфигурации не найден: {config_path}")
    try:
        content = path.read_text(encoding="utf-8")
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Ошибка синтаксиса JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError("Корень JSON должен быть объектом.")
    return data


def validate_types(data: dict[str, Any]) -> None:
    """Проверяет наличие всех обязательных ключей и их типы."""
    for key, expected_type in REQUIRED_KEYS.items():
        if key not in data:
            raise ConfigError(f"Отсутствует обязательный параметр: {key}")
        val = data[key]
        is_invalid_bool = expected_type is int and isinstance(val, bool)
        if not isinstance(val, expected_type) or is_invalid_bool:
            raise ConfigError(f"Неверный тип параметра '{key}'.")


def validate_values(data: dict[str, Any]) -> None:
    """Проверяет корректность значений параметров конфигурации."""
    non_empty = ("package_name", "repo_url", "package_version", "output_file")
    for key in non_empty:
        if not data[key].strip():
            raise ConfigError(f"Параметр '{key}' не может быть пустым.")
    if data["max_depth"] < MIN_DEPTH:
        raise ConfigError(f"Параметр 'max_depth' должен быть >= {MIN_DEPTH}.")
    if data["test_mode"] and not Path(data["repo_url"]).is_file():
        raise ConfigError("В тестовом режиме 'repo_url' должен вести к файлу.")


def parse_config(config_path: str) -> dict[str, Any]:
    """Читает и полностью валидирует конфигурационный файл."""
    data = load_json(config_path)
    validate_types(data)
    validate_values(data)
    return {key: data[key] for key in REQUIRED_KEYS}