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
            assert callee in callables
            assert qn in callables[callee].get('used_by', [])
        for caller in node.get('used_by', []):
            assert caller in callables
            assert qn in callables[caller].get('calls', [])
