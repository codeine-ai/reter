#!/usr/bin/env python3
"""Test various f-string cases."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reter import Reter

def test_case(name, code):
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}")
    print(code)
    print("-" * 40)

    reasoner = Reter()
    wme_count, errors = reasoner.load_python_code(code, "test_module")

    classes = reasoner.pattern(
        ("?x", "type", "py:Class"),
        ("?x", "name", "?name"),
        ("?x", "qualifiedName", "?qname")
    ).to_list()

    all_ok = True
    for c in classes:
        is_nested = len(c["?qname"].split(".")) > 2
        status = "FAIL" if is_nested else "OK"
        if is_nested:
            all_ok = False
        print(f"  {status}: {c['?name']} -> {c['?qname']}")

    return all_ok

# Test cases
cases = [
    ("Simple return", '''class First:
    def method(self):
        return 123

class Second:
    def __init__(self):
        pass
'''),

    ("Simple f-string", '''class First:
    def method(self, x):
        return f'value: {x}'

class Second:
    def __init__(self):
        pass
'''),

    ("F-string with format", '''class First:
    def method(self, x):
        return f'{x:>10}'

class Second:
    def __init__(self):
        pass
'''),

    ("F-string with nested expr", '''class First:
    def method(self, h, w):
        return f'{h:<{w}}'

class Second:
    def __init__(self):
        pass
'''),

    ("F-string with nested expr and space", '''class First:
    def method(self, h, w):
        return f' {h:<{w}} '

class Second:
    def __init__(self):
        pass
'''),
]

results = []
for name, code in cases:
    ok = test_case(name, code)
    results.append((name, ok))

print("\n" + "=" * 60)
print("SUMMARY:")
print("=" * 60)
for name, ok in results:
    status = "PASS" if ok else "FAIL"
    print(f"  {status}: {name}")
