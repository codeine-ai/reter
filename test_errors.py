#!/usr/bin/env python3
"""Check if lexer errors are captured."""

from reter import Reter

CODE = '''class A:
    def m(self):
        return f'{1:<{2}}'

class B:
    pass
'''

print("Testing nested f-string format spec:")
print(CODE)
print("-" * 40)

r = Reter()
wme_count, errors = r.load_python_code(CODE, 'test')

print(f"WME count: {wme_count}")
print(f"Errors: {errors}")
print(f"Error count: {len(errors) if errors else 0}")

if errors:
    for i, err in enumerate(errors):
        print(f"  Error {i}: {err}")

# Check classes
classes = r.pattern(
    ("?x", "type", "py:Class"),
    ("?x", "name", "?name"),
    ("?x", "qualifiedName", "?qname")
).to_list()

print(f"\nClasses found: {len(classes)}")
for c in classes:
    print(f"  {c['?name']}: {c['?qname']}")
