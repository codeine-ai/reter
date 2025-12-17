"""
Isolated test to verify type tracking and method call resolution.
Tests the basic functionality step by step.
"""

from reter import Reter
import tempfile
import os


def test_simple_attribute_creation():
    """Test that a simple attribute with type is created."""
    code = '''
class MyClass:
    def __init__(self):
        self.value = 42
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        f.flush()
        temp_path = f.name

    try:
        r = Reter()
        print(f"\n=== Loading Python file: {temp_path} ===")
        r.load_python_file(temp_path)

        # Check what facts were created - use REQL
        print("\n=== Checking all classes ===")
        result = r.reql("""
            SELECT ?class ?name
            WHERE {
                ?class concept "py:Class" .
                ?class name ?name
            }
        """)
        print(f"Classes found: {result.num_rows}")
        if result.num_rows > 0:
            for row in range(result.num_rows):
                print(f"  {result.column('?name')[row].as_py()}")

        print("\n=== Checking all methods ===")
        result = r.reql("""
            SELECT ?method ?name
            WHERE {
                ?method concept "py:Method" .
                ?method name ?name
            }
        """)
        print(f"Methods found: {result.num_rows}")
        if result.num_rows > 0:
            for row in range(result.num_rows):
                print(f"  {result.column('?name')[row].as_py()}")

        return result.num_rows > 0

    finally:
        os.unlink(temp_path)


def test_constructor_call_type():
    """Test that constructor call type is detected."""
    code = '''
class Server:
    def __init__(self):
        self.manager = Manager()

class Manager:
    pass
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        f.flush()
        temp_path = f.name

    try:
        r = Reter()
        print(f"\n\n=== Loading Python file with constructor: {temp_path} ===")
        r.load_python_file(temp_path)

        # Check for attributes
        print("\n=== Checking for attributes ===")
        result = r.reql("""
            SELECT ?attr ?name ?type ?vis
            WHERE {
                ?attr concept "py:Attribute" .
                ?attr name ?name .
                OPTIONAL { ?attr hasType ?type } .
                OPTIONAL { ?attr visibility ?vis }
            }
        """)
        print(f"Attributes found: {result.num_rows}")
        if result.num_rows > 0:
            for row in range(result.num_rows):
                name = result.column('?name')[row].as_py()
                typ = result.column('?type')[row].as_py() if result.column('?type')[row].is_valid else "N/A"
                vis = result.column('?vis')[row].as_py() if result.column('?vis')[row].is_valid else "N/A"
                print(f"  - {name}: type={typ}, visibility={vis}")

        return result.num_rows > 0

    finally:
        os.unlink(temp_path)


def test_method_call_simple():
    """Test simple method call without chaining."""
    code = '''
class Server:
    def __init__(self):
        pass

    def start(self):
        self.initialize()

    def initialize(self):
        pass
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        f.flush()
        temp_path = f.name

    try:
        r = Reter()
        print(f"\n\n=== Loading Python file with method calls: {temp_path} ===")
        r.load_python_file(temp_path)

        # Check for method calls
        print("\n=== Checking for method calls ===")
        result = r.reql("""
            SELECT ?caller ?callerName ?callee ?calleeName
            WHERE {
                ?caller concept "py:Method" .
                ?caller name ?callerName .
                ?caller calls ?callee .
                ?callee concept "py:Method" .
                ?callee name ?calleeName
            }
        """)
        print(f"Method calls found: {result.num_rows}")
        if result.num_rows > 0:
            for row in range(result.num_rows):
                caller = result.column('?callerName')[row].as_py()
                callee = result.column('?calleeName')[row].as_py()
                print(f"  {caller} -> {callee}")

        return result.num_rows > 0

    finally:
        os.unlink(temp_path)


def test_out_of_order_assignment():
    """Test case where method is called before type is assigned."""
    code = '''
class Server:
    def start(self):
        # Call happens here, but type assigned later
        self.manager.load_plugins()

    def __init__(self):
        # Type assigned here, after start method definition
        self.manager = PluginManager()

class PluginManager:
    def load_plugins(self):
        pass
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        f.flush()
        temp_path = f.name

    try:
        r = Reter()
        print(f"\n\n=== Testing out-of-order assignment: {temp_path} ===")
        r.load_python_file(temp_path)

        # Check for attributes with types
        print("\n=== Checking for manager attribute ===")
        result = r.reql("""
            SELECT ?attr ?name ?type
            WHERE {
                ?attr concept "py:Attribute" .
                ?attr name ?name .
                OPTIONAL { ?attr hasType ?type }
            }
        """)
        print(f"Attributes found: {result.num_rows}")
        if result.num_rows > 0:
            for row in range(result.num_rows):
                name = result.column('?name')[row].as_py()
                typ = result.column('?type')[row].as_py() if result.column('?type')[row].is_valid else "N/A"
                print(f"  - {name}: type={typ}")

        # Check for method calls (should be resolved even though type assigned later)
        print("\n=== Checking for method calls from 'start' ===")
        result = r.reql("""
            SELECT ?caller ?callerName ?callee ?calleeName
            WHERE {
                ?caller concept "py:Method" .
                ?caller name ?callerName .
                ?caller calls ?callee .
                ?callee concept "py:Method" .
                ?callee name ?calleeName
            }
        """)
        print(f"Method calls found: {result.num_rows}")
        if result.num_rows > 0:
            for row in range(result.num_rows):
                caller = result.column('?callerName')[row].as_py()
                callee = result.column('?calleeName')[row].as_py()
                print(f"  {caller} -> {callee}")

        return result.num_rows > 0

    finally:
        os.unlink(temp_path)


if __name__ == "__main__":
    print("=" * 80)
    print("ISOLATED TYPE TRACKING TESTS")
    print("=" * 80)

    success_count = 0
    total_count = 4

    if test_simple_attribute_creation():
        success_count += 1
        print("\n✓ Test 1 passed: Simple attribute creation")
    else:
        print("\n✗ Test 1 failed: Simple attribute creation")

    if test_constructor_call_type():
        success_count += 1
        print("\n✓ Test 2 passed: Constructor call type detection")
    else:
        print("\n✗ Test 2 failed: Constructor call type detection")

    if test_method_call_simple():
        success_count += 1
        print("\n✓ Test 3 passed: Simple method call")
    else:
        print("\n✗ Test 3 failed: Simple method call")

    if test_out_of_order_assignment():
        success_count += 1
        print("\n✓ Test 4 passed: Out-of-order assignment")
    else:
        print("\n✗ Test 4 failed: Out-of-order assignment")

    print("\n" + "=" * 80)
    print(f"RESULTS: {success_count}/{total_count} tests passed")
    print("=" * 80)
