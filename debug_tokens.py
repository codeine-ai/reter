#!/usr/bin/env python3
"""Debug script to see token stream from Python parser."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test case - minimal failing case
CODE = '''class First:
    def method(self, h, w):
        return f' {h:<{w}} '


class Second:
    def __init__(self, x):
        self.x = x
'''

# Try to get token output from the C++ parser
from reter import Reter

# Try parsing and see if we can get any debug info
reasoner = Reter()

print("=" * 60)
print("Loading code...")
print("=" * 60)
print(CODE)
print("=" * 60)

try:
    wme_count, errors = reasoner.load_python_code(CODE, "test_module")
    print(f"WME count: {wme_count}")
    print(f"Errors: {errors}")
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()

# Query for classes
print("\n" + "=" * 60)
print("Classes found:")
print("=" * 60)
classes = reasoner.pattern(
    ("?x", "type", "py:Class"),
    ("?x", "name", "?name"),
    ("?x", "qualifiedName", "?qname")
).to_list()

for c in classes:
    print(f"  {c['?name']}: {c['?qname']}")

# Query for methods of each class
print("\n" + "=" * 60)
print("Methods per class:")
print("=" * 60)

for c in classes:
    class_name = c['?name']
    methods = reasoner.pattern(
        ("?class", "type", "py:Class"),
        ("?class", "name", class_name),
        ("?class", "hasMethod", "?method"),
        ("?method", "name", "?method_name")
    ).to_list()
    method_names = [m["?method_name"] for m in methods]
    print(f"  {class_name}: {method_names}")
