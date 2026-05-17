import ast
from pathlib import Path


ALLOWED_DUNDER = {
    "__init__", "__new__", "__repr__", "__str__", "__bytes__", "__format__", "__lt__", "__le__", "__eq__", "__ne__", "__gt__", "__ge__",
    "__hash__", "__bool__", "__getattr__", "__getattribute__", "__setattr__", "__delattr__", "__dir__", "__get__", "__set__", "__delete__",
    "__set_name__", "__call__", "__len__", "__length_hint__", "__getitem__", "__setitem__", "__delitem__", "__iter__", "__next__",
    "__reversed__", "__contains__", "__add__", "__sub__", "__mul__", "__matmul__", "__truediv__", "__floordiv__", "__mod__", "__divmod__",
    "__pow__", "__lshift__", "__rshift__", "__and__", "__xor__", "__or__", "__radd__", "__rsub__", "__rmul__", "__rmatmul__", "__rtruediv__",
    "__rfloordiv__", "__rmod__", "__rdivmod__", "__rpow__", "__rlshift__", "__rrshift__", "__rand__", "__rxor__", "__ror__", "__iadd__",
    "__isub__", "__imul__", "__imatmul__", "__itruediv__", "__ifloordiv__", "__imod__", "__ipow__", "__ilshift__", "__irshift__", "__iand__",
    "__ixor__", "__ior__", "__neg__", "__pos__", "__abs__", "__invert__", "__complex__", "__int__", "__float__", "__index__", "__round__",
    "__trunc__", "__floor__", "__ceil__", "__enter__", "__exit__", "__aenter__", "__aexit__", "__await__", "__aiter__", "__anext__",
    "__copy__", "__deepcopy__", "__getstate__", "__setstate__", "__reduce__", "__reduce_ex__", "__getnewargs__", "__getnewargs_ex__", "__sizeof__",
    "__subclasshook__", "__init_subclass__", "__class_getitem__", "__mro_entries__", "__instancecheck__", "__subclasscheck__", "__post_init__",
}


def test_no_accidental_non_dunder_double_underscore_helpers():
    violations = []
    for path in Path("src/fabricops_kit").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                name = node.name
                if name.startswith("__") and not name.endswith("__"):
                    violations.append(f"{path}:{node.lineno} -> {name}")
                elif name.startswith("__") and name.endswith("__") and name not in ALLOWED_DUNDER:
                    violations.append(f"{path}:{node.lineno} -> {name} (non-standard dunder)")
    assert not violations, "Found accidental/non-standard double-underscore helper names:\n" + "\n".join(violations)
