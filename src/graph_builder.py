"""Построение графа зависимостей с помощью рекурсивного BFS."""


def is_filtered(package_name: str, substring: str) -> bool:
    """Проверяет, нужно ли исключить пакет по подстроке."""
    return bool(substring) and substring in package_name


def process_level_node(
    node: str,
    repo_map: dict[str, list[str]],
    graph: dict[str, list[str]],
    visited: set[str],
    filter_substring: str,
) -> list[str]:
    """Обрабатывает один узел уровня и возвращает новых соседей."""
    if is_filtered(node, filter_substring):
        return []
    raw_deps = repo_map.get(node, [])
    filtered_deps = [
        dep for dep in raw_deps if not is_filtered(dep, filter_substring)
    ]
    graph[node] = filtered_deps
    next_nodes: list[str] = []
    for dep in filtered_deps:
        if dep not in visited:
            visited.add(dep)
            next_nodes.append(dep)
    return next_nodes


def bfs_recursive(
    current_level: list[str],
    depth: int,
    max_depth: int,
    repo_map: dict[str, list[str]],
    graph: dict[str, list[str]],
    visited: set[str],
    filter_substring: str,
) -> None:
    """Рекурсивный обход графа зависимостей в ширину по уровням."""
    if not current_level or depth > max_depth:
        return
    next_level: list[str] = []
    for node in current_level:
        neighbors = process_level_node(
            node, repo_map, graph, visited, filter_substring
        )
        next_level.extend(neighbors)
    bfs_recursive(
        next_level,
        depth + 1,
        max_depth,
        repo_map,
        graph,
        visited,
        filter_substring,
    )


def build_dependency_graph(
    root_package: str,
    repo_map: dict[str, list[str]],
    max_depth: int,
    filter_substring: str,
) -> dict[str, list[str]]:
    """Строит транзитивный граф зависимостей от корневого пакета."""
    if is_filtered(root_package, filter_substring):
        return {}
    graph: dict[str, list[str]] = {}
    visited = {root_package}
    bfs_recursive(
        [root_package],
        1,
        max_depth,
        repo_map,
        graph,
        visited,
        filter_substring,
    )
    return graph

STATE_UNVISITED = 0
STATE_VISITING = 1
STATE_VISITED = 2


def visit_load_node(
    node: str,
    graph: dict[str, list[str]],
    state: dict[str, int],
    order: list[str],
) -> None:
    """Рекурсивно обходит зависимости в post-order для порядка загрузки."""
    current_state = state.get(node, STATE_UNVISITED)
    if current_state != STATE_UNVISITED:
        return
    state[node] = STATE_VISITING
    for dep in graph.get(node, []):
        visit_load_node(dep, graph, state, order)
    state[node] = STATE_VISITED
    order.append(node)


def get_load_order(
    root_package: str, graph: dict[str, list[str]]
) -> list[str]:
    """Возвращает порядок загрузки пакетов от листьев к корневому."""
    if root_package not in graph:
        return []
    state: dict[str, int] = {}
    order: list[str] = []
    visit_load_node(root_package, graph, state, order)
    return order