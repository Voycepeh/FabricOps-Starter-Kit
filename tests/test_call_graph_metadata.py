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
        expected_internal = f'/FabricOps-Starter-Kit/api/modules/{module}/#{short_name}'
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
        expected = (
            f'/FabricOps-Starter-Kit/reference/{short_name}/'
            if node.get('classification') in {'essential', 'optional'}
            else f'/FabricOps-Starter-Kit/api/modules/{module}/#{short_name}'
        )
        assert node['docs_url'] == expected, f'{qn} has wrong docs_url'


def test_call_graph_page_is_deferred_with_explicit_note():
    page = Path('docs/reference/call-graph.md').read_text(encoding='utf-8')
    assert 'Graph exploration is intentionally deferred.' in page
    assert 'Neo4j or a proper graph backend.' in page
    assert 'id="call-graph-canvas"' not in page
    assert not Path('docs/javascripts/call-graph.js').exists()


def test_call_graph_page_css_rules_are_removed():
    css = Path('docs/stylesheets/api-chips.css').read_text(encoding='utf-8')
    assert '.call-graph-page' not in css
    assert '.call-graph-legend' not in css


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
    assert '../../../reference/call-graph/?function=' not in script


def test_module_page_relationship_sections_are_readable_and_grouped():
    text = Path('docs/api/modules/config.md').read_text(encoding='utf-8')
    assert '## Module relationships' in text
    assert '### Callable relationships' in text
    assert '#### Inside this module' in text
    assert '### Related internal helpers' in text
    assert '<summary>Show internal helpers</summary>' in text
    assert '### External callers' in text
    assert '### External callees' in text
    assert '### Callable relationships' in text and '### Related internal helpers' in text
    assert text.index('### Callable relationships') < text.index('#### Inside this module')
    assert text.index('#### Inside this module') < text.index('### Related internal helpers')
    assert text.index('### Related internal helpers') < text.index('### External callers')
    assert text.index('### External callers') < text.index('### External callees')
    assert '<div class="module-relationship-list">' not in text
    assert '#### Module relationships' not in text
    assert '../../reference/call-graph/?module=fabricops_kit.config' not in text
    assert 'Open interactive module graph' not in text
    assert '**fabric_input_output**' in text
    assert '<h6>Public callables</h6>' in text
    assert '<h6>Internal helpers details</h6>' in text


def test_module_pages_do_not_emit_broken_helper_paths():
    for module_page in Path('docs/api/modules').glob('*.md'):
        text = module_page.read_text(encoding='utf-8')
        assert 'modules/modules' not in text
        assert '../../api/modules/' not in text
        assert '/api/api/modules/' not in text


def test_module_pages_do_not_emit_api_relative_call_graph_links():
    for module_page in Path('docs/api/modules').glob('*.md'):
        text = module_page.read_text(encoding='utf-8')
        assert '../../reference/call-graph/' not in text
        assert '/api/reference/call-graph/' not in text


def test_new_internal_helper_pages_are_not_generated():
    internal_dir = Path("docs/reference/internal")
    assert not list(internal_dir.glob("data_agreement__*.md"))
    assert not (internal_dir / "metadata__resolve_action_by.md").exists()
    assert not (internal_dir / "metadata__runtime_context.md").exists()
