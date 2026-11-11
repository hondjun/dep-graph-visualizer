"""Тесты генерации диаграмм D2 и ASCII-дерева."""

import unittest

from src.visualizer import build_ascii_tree, generate_d2_text


class TestVisualizer(unittest.TestCase):
    """Проверка текстового вывода D2 и ASCII-дерева."""

    def test_generate_d2_text(self) -> None:
        """Проверяет корректность генерации рёбер в синтаксисе D2."""
        graph = {"A": ["B", "C"], "B": [], "C": []}
        d2_out = generate_d2_text("A", graph)
        self.assertIn("direction: down", d2_out)
        self.assertIn('"A" -> "B"', d2_out)
        self.assertIn('"A" -> "C"', d2_out)

    def test_ascii_tree_with_cycle(self) -> None:
        """Проверяет построение ASCII-дерева и пометку цикла."""
        graph = {"A": ["B"], "B": ["A"]}
        tree = build_ascii_tree("A", graph)
        expected = "A\n└── B\n    └── A (цикл)"
        self.assertEqual(tree, expected)


if __name__ == "__main__":
    unittest.main()