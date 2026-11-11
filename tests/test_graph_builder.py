"""Тесты рекурсивного BFS-построителя графа зависимостей."""

import tempfile
import unittest
from pathlib import Path

from src.apt_parser import parse_test_repo
from src.graph_builder import build_dependency_graph

TEST_REPO_CONTENT = """A: B, C
B: D, E
C: F
D: A
E: F
F:
"""


class TestGraphBuilder(unittest.TestCase):
    """Проверка построения графа с циклом, глубиной и фильтрацией."""

    def setUp(self) -> None:
        """Создает временный файл тестового репозитория."""
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.repo_file = Path(self.tmp_dir.name) / "repo.txt"
        self.repo_file.write_text(TEST_REPO_CONTENT, encoding="utf-8")
        self.repo_map = parse_test_repo(str(self.repo_file))

    def tearDown(self) -> None:
        """Удаляет временную директорию."""
        self.tmp_dir.cleanup()

    def test_cycle_and_full_traversal(self) -> None:
        """Проверяет обход графа с циклом D -> A без зацикливания."""
        graph = build_dependency_graph("A", self.repo_map, 10, "")
        self.assertEqual(
            graph,
            {
                "A": ["B", "C"],
                "B": ["D", "E"],
                "C": ["F"],
                "D": ["A"],
                "E": ["F"],
                "F": [],
            },
        )

    def test_max_depth_limit(self) -> None:
        """Проверяет остановку обхода на заданной глубине."""
        graph = build_dependency_graph("A", self.repo_map, 1, "")
        self.assertEqual(graph, {"A": ["B", "C"]})

    def test_filter_substring(self) -> None:
        """Проверяет исключение пакетов, содержащих подстроку."""
        graph = build_dependency_graph("A", self.repo_map, 5, "B")
        self.assertEqual(
            graph,
            {
                "A": ["C"],
                "C": ["F"],
                "F": [],
            },
        )


if __name__ == "__main__":
    unittest.main()