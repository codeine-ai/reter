"""Debug script to see what facts are being created."""

from reter import Reter
import tempfile
import os

code = '''
class MyClass:
    def __init__(self):
        self.manager = PluginManager()

class PluginManager:
    pass
'''

with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
    f.write(code)
    f.flush()
    temp_path = f.name

try:
    r = Reter()
    r.load_python_file(temp_path)

    # Check what facts are created
    print("\n=== ALL FACTS ===")
    all_facts = r.query([("?s", "?p", "?o")])
    count = 0
    for fact in all_facts:
        count += 1
        print(f"{count}. {fact}")
        if count > 50:  # Limit output
            print("... (more facts)")
            break

    print(f"\nTotal facts checked: {count}")

    # Check for attributes specifically
    print("\n=== CHECKING FOR ATTRIBUTES ===")
    attr_results = r.query([
        ("?attr", "type", "py:Attribute")
    ])
    attr_list = list(attr_results)
    print(f"Found {len(attr_list)} attributes")
    for attr in attr_list:
        print(f"  - {attr}")

    # Check for assignments
    print("\n=== CHECKING FOR ASSIGNMENTS ===")
    assign_results = r.query([
        ("?assign", "type", "py:Assignment")
    ])
    assign_list = list(assign_results)
    print(f"Found {len(assign_list)} assignments")
    for assign in assign_list[:10]:
        print(f"  - {assign}")

    # Check for methods
    print("\n=== CHECKING FOR METHODS ===")
    method_results = r.query([
        ("?method", "type", "py:Method")
    ])
    method_list = list(method_results)
    print(f"Found {len(method_list)} methods")
    for method in method_list:
        print(f"  - {method}")

finally:
    os.unlink(temp_path)
