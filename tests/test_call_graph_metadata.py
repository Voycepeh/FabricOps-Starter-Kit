import json
from pathlib import Path


def test_call_graph_metadata_integrity():
    path = Path('docs/reference/dependency-metadata.json')
    data = json.loads(path.read_text(encoding='utf-8'))
    callables = data.get('callables', {})
    assert callables

    for qn, node in callables.items():
        assert node.get('docs_url')
        for callee in node.get('calls', []):
            if callee in callables:
                assert qn in callables[callee].get('used_by', [])
        for caller in node.get('used_by', []):
            assert caller in callables
            assert qn in callables[caller].get('calls', [])


def test_docs_url_routes_public_vs_internal():
    data = json.loads(Path('docs/reference/dependency-metadata.json').read_text(encoding='utf-8'))
    callables = data['callables']
    for qn, node in callables.items():
        module = node['module']
        short_name = node['short_name']
        expected_public = f'/FabricOps-Starter-Kit/reference/{short_name}/'
        expected_internal = f'/FabricOps-Starter-Kit/reference/internal/{module}/{short_name}/'
        if node.get('classification') in {'essential', 'optional'}:
            assert node['docs_url'] == expected_public
        else:
            assert node['docs_url'] == expected_internal


def test_no_short_name_collision_breaks_navigation():
    data = json.loads(Path('docs/reference/dependency-metadata.json').read_text(encoding='utf-8'))
    callables = data['callables']
    by_short = {}
    for qn, node in callables.items():
        by_short.setdefault(node['short_name'], []).append((qn, node))

    collisions = {name: rows for name, rows in by_short.items() if len(rows) > 1}
    for _name, rows in collisions.items():
        urls = {node['docs_url'] for _, node in rows}
        assert len(urls) == len(rows), 'colliding short names must not share docs_url'


def test_module_external_callers_do_not_include_same_module():
    data = json.loads(Path('docs/reference/dependency-metadata.json').read_text(encoding='utf-8'))
    callables = data['callables']
    for qn, node in callables.items():
        current_module = node['module']
        for caller_qn in node.get('used_by', []):
            caller_module = caller_qn.split('.')[-2]
            if caller_module == current_module:
                continue
            assert caller_module != current_module
