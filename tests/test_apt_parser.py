"""Тесты парсера индекса пакетов Ubuntu APT."""

import unittest

from src.apt_parser import (
    RepoError,
    get_direct_dependencies,
    parse_depends_field,
)

SAMPLE_INDEX = """Package: curl
Version: 8.5.0-2ubuntu10
Depends: libc6 (>= 2.38), libcurl4t64 (= 8.5.0-2ubuntu10), zlib1g (>= 1:1.1.4)

Package: curl
Version: 8.5.0-2ubuntu10.6
Depends: libc6 (>= 2.38), libcurl4t64 (= 8.5.0-2ubuntu10.6)
"""


class TestAptParser(unittest.TestCase):
    """Набор тестов для разбора индекса пакетов APT."""

    def test_parse_depends_with_alternatives(self) -> None:
        """Проверяет разбор зависимостей с версиями и альтернативами."""
        raw = "libc6 (>= 2.34), default-mta | mail-transport-agent, python3:any"
        result = parse_depends_field(raw)
        self.assertEqual(result, ["libc6", "default-mta", "python3"])

    def test_get_exact_version_dependencies(self) -> None:
        """Проверяет выбор зависимостей строго для указанной версии."""
        deps = get_direct_dependencies(
            SAMPLE_INDEX, "curl", "8.5.0-2ubuntu10"
        )
        self.assertEqual(deps, ["libc6", "libcurl4t64", "zlib1g"])

    def test_package_version_not_found(self) -> None:
        """Проверяет ошибку при отсутствии нужной версии пакета."""
        with self.assertRaises(RepoError):
            get_direct_dependencies(SAMPLE_INDEX, "curl", "9.9.9")


if __name__ == "__main__":
    unittest.main()