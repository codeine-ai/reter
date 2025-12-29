#!/usr/bin/env python3
"""Debug script to see all tokens produced by the parser."""

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

# Simple case that works
SIMPLE_CODE = '''class First:
    def method(self, h, w):
        return 123


class Second:
    def __init__(self, x):
        self.x = x
'''

from reter import Reter

print("=" * 60)
print("Testing SIMPLE case (no f-string):")
print("=" * 60)
print(SIMPLE_CODE)
print("=" * 60)

reasoner = Reter()
wme_count, errors = reasoner.load_python_code(SIMPLE_CODE, "simple_module")

classes = reasoner.pattern(
    ("?x", "type", "py:Class"),
    ("?x", "name", "?name"),
    ("?x", "qualifiedName", "?qname")
).to_list()

print(f"\nClasses found: {len(classes)}")
for c in classes:
    print(f"  {c['?name']}: {c['?qname']}")
    parts = c["?qname"].split(".")
    if len(parts) > 2:
        print(f"    WARNING: Nested incorrectly!")

print("\n" + "=" * 60)
print("Testing F-STRING case:")
print("=" * 60)
print(CODE)
print("=" * 60)

reasoner2 = Reter()
wme_count, errors = reasoner2.load_python_code(CODE, "fstring_module")

classes = reasoner2.pattern(
    ("?x", "type", "py:Class"),
    ("?x", "name", "?name"),
    ("?x", "qualifiedName", "?qname")
).to_list()

print(f"\nClasses found: {len(classes)}")
for c in classes:
    print(f"  {c['?name']}: {c['?qname']}")
    parts = c["?qname"].split(".")
    if len(parts) > 2:
        print(f"    WARNING: Nested incorrectly!")
