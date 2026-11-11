"""Парсер индексов репозитория Ubuntu (APT) и тестовых файлов."""

import gzip
import lzma
import urllib.error
import urllib.request
from pathlib import Path

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


def extract_deps_from_fields(fields: dict[str, str]) -> list[str]:
    """Объединяет Pre-Depends и Depends одного блока пакета."""
    raw_pre = fields.get("Pre-Depends", "")
    raw_dep = fields.get("Depends", "")
    combined = ", ".join(filter(None, [raw_pre, raw_dep]))
    return parse_depends_field(combined)


def build_apt_repo_map(
    index_text: str, root_package: str, root_version: str
) -> dict[str, list[str]]:
    """Строит карту зависимостей из индекса APT с учетом версии корня."""
    repo_map: dict[str, list[str]] = {}
    root_found = False
    for block in index_text.strip().split("\n\n"):
        if not block.strip():
            continue
        fields = parse_stanza(block)
        pkg = fields.get("Package", "")
        ver = fields.get("Version", "")
        if not pkg:
            continue
        if pkg == root_package and ver == root_version:
            repo_map[pkg] = extract_deps_from_fields(fields)
            root_found = True
        elif pkg != root_package and pkg not in repo_map:
            repo_map[pkg] = extract_deps_from_fields(fields)
    if not root_found:
        raise RepoError(
            f"Пакет '{root_package}' версии '{root_version}' не найден."
        )
    return repo_map


def parse_test_repo(file_path: str) -> dict[str, list[str]]:
    """Читает тестовый репозиторий вида 'A: B, C' из файла."""
    repo_map: dict[str, list[str]] = {}
    lines = Path(file_path).read_text(encoding="utf-8").splitlines()
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if ":" not in stripped:
            raise RepoError(f"Некорректная строка в тесте: {stripped}")
        pkg, raw_deps = stripped.split(":", 1)
        pkg_name = pkg.strip()
        deps = [d.strip() for d in raw_deps.split(",") if d.strip()]
        repo_map[pkg_name] = deps
    return repo_map

def get_direct_dependencies(
    index_text: str, package_name: str, package_version: str
) -> list[str]:
    """Возвращает прямые зависимости пакета заданной версии."""
    repo_map = build_apt_repo_map(index_text, package_name, package_version)
    return repo_map[package_name]