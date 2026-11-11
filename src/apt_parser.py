"""Парсер индексов репозитория пакетов Ubuntu (APT)."""

import gzip
import lzma
import urllib.error
import urllib.request

REQUEST_TIMEOUT = 30


class RepoError(Exception):
    """Исключение при загрузке или разборе индекса репозитория."""


def fetch_index_text(repo_url: str) -> str:
    """Скачивает индекс пакетов по URL и распаковывает при необходимости."""
    try:
        req = urllib.request.Request(
            repo_url, headers={"User-Agent": "dep-graph-visualizer/1.0"}
        )
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            raw_data = resp.read()
    except (urllib.error.URLError, ValueError, OSError) as exc:
        raise RepoError(f"Не удалось загрузить индекс: {exc}") from exc

    if repo_url.endswith(".gz"):
        raw_data = gzip.decompress(raw_data)
    elif repo_url.endswith(".xz"):
        raw_data = lzma.decompress(raw_data)

    return raw_data.decode("utf-8", errors="replace")


def parse_stanza(block: str) -> dict[str, str]:
    """Разбирает один текстовый блок описания пакета в словарь полей."""
    fields: dict[str, str] = {}
    current_key = ""
    for line in block.splitlines():
        if line.startswith((" ", "\t")) and current_key:
            fields[current_key] += " " + line.strip()
        elif ":" in line:
            key, val = line.split(":", 1)
            current_key = key.strip()
            fields[current_key] = val.strip()
    return fields


def parse_depends_field(raw_depends: str) -> list[str]:
    """Извлекает имена прямых зависимостей из строки поля Depends."""
    if not raw_depends.strip():
        return []
    dependencies: list[str] = []
    for item in raw_depends.split(","):
        primary_alt = item.split("|")[0].strip()
        pkg_token = primary_alt.split("(", 1)[0].strip()
        pkg_name = pkg_token.split(":", 1)[0].strip()
        if pkg_name and pkg_name not in dependencies:
            dependencies.append(pkg_name)
    return dependencies


def get_direct_dependencies(
    index_text: str, package_name: str, package_version: str
) -> list[str]:
    """Находит пакет заданной версии и возвращает его прямые зависимости."""
    for block in index_text.strip().split("\n\n"):
        if not block.strip():
            continue
        fields = parse_stanza(block)
        is_same_pkg = fields.get("Package") == package_name
        is_same_ver = fields.get("Version") == package_version
        if is_same_pkg and is_same_ver:
            raw_pre = fields.get("Pre-Depends", "")
            raw_dep = fields.get("Depends", "")
            combined = ", ".join(filter(None, [raw_pre, raw_dep]))
            return parse_depends_field(combined)
    raise RepoError(
        f"Пакет '{package_name}' версии '{package_version}' не найден."
    )