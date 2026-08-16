from __future__ import annotations

import importlib.util
from pathlib import Path
import re


path = Path('.github/agent_stage1.py')
spec = importlib.util.spec_from_file_location('agent_stage1', path)
if spec is None or spec.loader is None:
    raise RuntimeError('Could not load Stage 1 implementation module')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def replace_once(text: str, pattern: str, replacement: str, label: str) -> str:
    compiled = re.compile(pattern, re.S)
    matches = list(compiled.finditer(text))
    if len(matches) != 1:
        raise RuntimeError(f'Could not replace {label} exactly once; found {len(matches)} matches')
    return compiled.sub(lambda _match: replacement, text, count=1)


module.replace_once = replace_once
module.main()

reference_test_path = Path('tests/unit/test_reference_agent_docs.py')
reference_test = reference_test_path.read_text(encoding='utf-8')
old_assertion = '    assert text.index(image_reference) < text.index("<div class=\\"grid cards\\" markdown>")'
new_assertion = '    assert text.index(image_reference) < text.index("## [METADATA_DATA_STEWARD]")'
if reference_test.count(old_assertion) != 1:
    raise RuntimeError('Expected exactly one metadata grid ordering assertion to update')
reference_test_path.write_text(reference_test.replace(old_assertion, new_assertion), encoding='utf-8')

# Temporary runner only: this commit triggers the final validated publish pass.
