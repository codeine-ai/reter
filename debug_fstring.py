#!/usr/bin/env python3
"""Debug script to trace f-string mode stack."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reter import Reter

# The minimal failing case
CODE = '''class First:
    def method(self, h, w):
        return f' {h:<{w}} '


class Second:
    def __init__(self, x):
        self.x = x
'''

print("=" * 60)
print("Parsing code with f-string format spec:")
print("=" * 60)
print(CODE)
print("=" * 60)

reasoner = Reter()
wme_count, errors = reasoner.load_python_code(CODE, "test_module")

print("\n" + "=" * 60)
print("Parsing complete. Checking classes:")
print("=" * 60)

classes = reasoner.pattern(
    ("?x", "type", "py:Class"),
    ("?x", "name", "?name"),
    ("?x", "qualifiedName", "?qname")
).to_list()

for c in classes:
    print(f"  Class: {c['?name']}, qualifiedName: {c['?qname']}")
    parts = c["?qname"].split(".")
    if len(parts) > 2:
        print(f"    WARNING: Nested incorrectly!")

print("\n" + "=" * 60)
print(f"Total classes: {len(classes)}")
if len(classes) == 2:
    print("PASS: Found 2 classes as expected")
else:
    print(f"FAIL: Expected 2 classes, got {len(classes)}")
