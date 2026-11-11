"""CLI-приложение для визуализации графа зависимостей пакетов."""

import sys
from pathlib import Path

from src.apt_parser import RepoError, fetch_index_text, get_direct_dependencies
from src.config import ConfigError, parse_config

DEFAULT_CONFIG = Path(__file__).resolve().parent.parent / "config.json"


def main() -> int:
    """Точка входа CLI-приложения."""
    config_path = sys.argv[1] if len(sys.argv) > 1 else str(DEFAULT_CONFIG)
    try:
        config = parse_config(config_path)
        index_text = fetch_index_text(config["repo_url"])
        deps = get_direct_dependencies(
            index_text,
            config["package_name"],
            config["package_version"],
        )
        for dep in deps:
            print(dep)
    except (ConfigError, RepoError) as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())