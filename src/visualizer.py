"""Генерация представлений графа в форматах D2, PNG и ASCII-дерева."""

import shutil
import subprocess
import tempfile
from pathlib import Path


class RenderError(Exception):
    """Исключение при генерации изображения графа."""


def format_d2_node(name: str) -> str:
    """Экранирует имя пакета для использования в синтаксисе D2."""
    escaped = name.replace('"', '\\"')
    return f'"{escaped}"'


def generate_d2_text(
    root_package: str, graph: dict[str, list[str]]
) -> str:
    """Формирует текстовое описание графа зависимостей на языке D2."""
    if not graph:
        return f"{format_d2_node(root_package)}\n"
    lines: list[str] = ["direction: down"]
    for pkg, deps in graph.items():
        src_node = format_d2_node(pkg)
        if not deps:
            lines.append(src_node)
            continue
        for dep in deps:
            dst_node = format_d2_node(dep)
            lines.append(f"{src_node} -> {dst_node}")
    return "\n".join(lines) + "\n"


def render_d2_to_png(d2_text: str, output_file: str) -> None:
    """Компилирует текст D2 в PNG-файл с помощью утилиты d2."""
    d2_bin = shutil.which("d2")
    if not d2_bin:
        raise RenderError(
            "Утилита 'd2' не найдена в PATH. Установите её: brew install d2"
        )
    out_path = Path(output_file)
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".d2", encoding="utf-8", delete=True
    ) as tmp_d2:
        tmp_d2.write(d2_text)
        tmp_d2.flush()
        result = subprocess.run(
            [d2_bin, tmp_d2.name, str(out_path)],
            capture_output=True,
            text=True,
            check=False,
        )
    if result.returncode != 0:
        err_msg = result.stderr.strip() or "неизвестная ошибка d2"
        raise RenderError(f"Ошибка рендеринга D2: {err_msg}")


def collect_ascii_lines(
    node: str,
    graph: dict[str, list[str]],
    prefix: str,
    is_last: bool,
    ancestors: set[str],
    lines: list[str],
) -> None:
    """Рекурсивно формирует строки ASCII-дерева с защитой от циклов."""
    connector = "└── " if is_last else "├── "
    is_cycle = node in ancestors
    suffix = " (цикл)" if is_cycle else ""
    lines.append(f"{prefix}{connector}{node}{suffix}")
    if is_cycle:
        return
    deps = graph.get(node, [])
    next_prefix = prefix + ("    " if is_last else "│   ")
    next_ancestors = ancestors | {node}
    for idx, dep in enumerate(deps):
        last_child = idx == len(deps) - 1
        collect_ascii_lines(
            dep, graph, next_prefix, last_child, next_ancestors, lines
        )


def build_ascii_tree(
    root_package: str, graph: dict[str, list[str]]
) -> str:
    """Возвращает строковое представление графа в виде ASCII-дерева."""
    if root_package not in graph:
        return f"{root_package} (исключен фильтром)"
    lines = [root_package]
    deps = graph.get(root_package, [])
    for idx, dep in enumerate(deps):
        last_child = idx == len(deps) - 1
        collect_ascii_lines(
            dep, graph, "", last_child, {root_package}, lines
        )
    return "\n".join(lines)