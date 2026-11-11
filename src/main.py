"""CLI-приложение для визуализации графа зависимостей пакетов."""

import sys
from pathlib import Path
from typing import Any

from src.apt_parser import (
    RepoError,
    build_apt_repo_map,
    fetch_index_text,
    parse_test_repo,
)
from src.config import ConfigError, parse_config
from src.graph_builder import build_dependency_graph
from src.visualizer import (
    RenderError,
    build_ascii_tree,
    generate_d2_text,
    render_d2_to_png,
)

DEFAULT_CONFIG = Path(__file__).resolve().parent.parent / "config.json"


def load_repo_map(config: dict[str, Any]) -> dict[str, list[str]]:
    """Загружает карту зависимостей из тестового файла или URL."""
    if config["test_mode"]:
        return parse_test_repo(config["repo_url"])
    index_text = fetch_index_text(config["repo_url"])
    return build_apt_repo_map(
        index_text, config["package_name"], config["package_version"]
    )


def main() -> int:
    """Точка входа CLI-приложения."""
    config_path = sys.argv[1] if len(sys.argv) > 1 else str(DEFAULT_CONFIG)
    try:
        config = parse_config(config_path)
        repo_map = load_repo_map(config)
        graph = build_dependency_graph(
            config["package_name"],
            repo_map,
            config["max_depth"],
            config["filter_substring"],
        )
        d2_text = generate_d2_text(config["package_name"], graph)
        render_d2_to_png(d2_text, config["output_file"])
        print(f"Граф сохранён в файл: {config['output_file']}")
        if config["ascii_tree"]:
            print(build_ascii_tree(config["package_name"], graph))
    except (ConfigError, RepoError, RenderError) as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())