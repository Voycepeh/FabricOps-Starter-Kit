import json
from pathlib import Path
import re


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


def test_docs_url_points_to_generated_reference_routes():
    data = json.loads(Path('docs/reference/dependency-metadata.json').read_text(encoding='utf-8'))
    callables = data['callables']
    for qn, node in callables.items():
        short_name = node['short_name']
        module = node['module']
        expected = f'/FabricOps-Starter-Kit/reference/{short_name}/' if node.get('classification') in {'essential', 'optional'} else f'/FabricOps-Starter-Kit/reference/internal/{module}/{short_name}/'
        assert node['docs_url'] == expected, f'{qn} has wrong docs_url'


def test_call_graph_page_contains_canvas_and_status_text():
    page = Path('docs/reference/call-graph.md').read_text(encoding='utf-8')
    assert 'id="call-graph-canvas"' in page
    assert 'id="call-graph-search-results"' in page
    assert 'id="call-graph-search-empty"' in page

    assert 'No matching function found.' in page

    js = Path('docs/javascripts/call-graph.js').read_text(encoding='utf-8')
    for msg in ['Loading call graph...', 'Unable to load dependency metadata.', 'No callable nodes found.']:
        assert msg in js

    for script_fragment in [
        'call-graph-module',
        'call-graph-function-chip',
        'refreshEdges',
        'call-graph-search-option',
        'window.history.replaceState',
        'renderDropdown([])',
        'searchInput.value = selectedRecord.searchLabel',
        "const functionQuery = params.get('function')",
    ]:
        assert script_fragment in js


def test_dependency_metadata_contains_module_grouping_keys():
    data = json.loads(Path('docs/reference/dependency-metadata.json').read_text(encoding='utf-8'))
    assert isinstance(data.get('modules'), dict)
    assert data['modules']
    for qn, node in data['callables'].items():
        assert node.get('module'), f'{qn} missing module'
        assert node.get('short_name'), f'{qn} missing short_name'


def test_no_duplicate_relationship_sections_in_generated_function_pages_script():
    script = Path('docs/gen_ref_pages.py').read_text(encoding='utf-8')
    assert '## Relationship details' not in script
    assert '## Function flow details' not in script


def test_module_callable_chip_links_resolve_to_known_docs_routes():
    metadata = json.loads(Path('docs/reference/dependency-metadata.json').read_text(encoding='utf-8'))['callables']
    known_routes = {v['docs_url'] for v in metadata.values()}

    for module_page in Path('docs/api/modules').glob('*.md'):
        text = module_page.read_text(encoding='utf-8')
        for href in re.findall(r'href="([^"]+)"', text):
            if not href.startswith('../../reference/'):
                continue
            if href.startswith('../../reference/call-graph/'):
                continue
            route = href.replace('../../reference', '/FabricOps-Starter-Kit/reference').rstrip('/') + '/'
            if '/FabricOps-Starter-Kit/reference/internal/' in route or route.count('/') == 5:
                assert route in known_routes, f'{module_page}: broken route {href}'


def test_generated_callable_call_graph_link_uses_reference_route_not_api_reference():
    script = Path('docs/gen_ref_pages.py').read_text(encoding='utf-8')
    assert '../call-graph/?function=' not in script
    assert '../../../reference/call-graph/?function=' in script


def test_module_page_relationship_sections_are_readable_and_grouped():
    text = Path('docs/api/modules/config.md').read_text(encoding='utf-8')
    assert '### Callable relationships' in text
    assert '#### Inside this module' in text
    assert '#### External callers' in text
    assert '#### External callees' in text
    assert '<div class="module-relationship-list">' not in text
    assert '#### Module relationships' not in text
    assert '../../reference/call-graph/?module=fabricops_kit.config' in text
    assert '**fabric_input_output**' in text
    assert '<h6>Public callables</h6>' in text
    assert '<h6>Internal helpers</h6>' in text
