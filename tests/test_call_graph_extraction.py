"""
Test call graph extraction from Python code

This test verifies that RETER correctly extracts function calls
and creates caller/callee relationships.
"""

import pytest
from reter import Reter


def test_simple_function_call():
    """Test extraction of a simple function call"""

    code = """
def greet(name):
    print(f"Hello {name}")
    return name

def main():
    result = greet("Alice")
    print(result)
"""

    r = Reter()
    wme_count = r.load_python_code(code, "test_module")

    print(f"\n✓ Loaded {wme_count} WMEs")

    # Query for all call facts (using direct calls relation)
    query = """
    SELECT ?caller ?callee
    WHERE {
        ?caller calls ?callee
    }
    """

    result = r.reql(query)
    df = result.to_pandas()

    print(f"\n📊 Call facts found: {len(df)}")
    print(df.to_string())

    # Should find calls: main -> greet, main -> print, greet -> print
    assert len(df) > 0, "No call facts were extracted!"

    # Check if we can find the greet call
    greet_calls = df[df['?callee'].str.contains('greet', na=False)]
    print(f"\n✓ Calls to 'greet': {len(greet_calls)}")
    print(greet_calls.to_string())

    return df


def test_method_call():
    """Test extraction of method calls"""

    code = """
class Calculator:
    def add(self, a, b):
        return a + b

    def calculate(self, x, y):
        result = self.add(x, y)
        print(result)
        return result

def use_calculator():
    calc = Calculator()
    value = calc.calculate(10, 20)
"""

    r = Reter()
    wme_count = r.load_python_code(code, "calculator_module")

    print(f"\n✓ Loaded {wme_count} WMEs")

    # Query for method calls (using direct calls relation)
    query = """
    SELECT ?caller ?callee
    WHERE {
        ?caller calls ?callee
    }
    """

    result = r.reql(query)
    df = result.to_pandas()

    print(f"\n📊 Call facts found: {len(df)}")
    print(df.to_string())

    # Should find: calculate -> add, calculate -> print, use_calculator -> calculate
    assert len(df) > 0, "No method call facts were extracted!"

    return df


def test_query_structure():
    """Test the actual query structure used in the feedback document"""

    code = """
def foo():
    bar()

def bar():
    baz()

def baz():
    pass
"""

    r = Reter()
    r.load_python_code(code, "simple_calls")

    # Query using direct calls relation (new implementation)
    correct_query = """
    SELECT ?caller ?callee WHERE {
      ?caller calls ?callee
    }
    """

    print("\n✅ Testing direct calls relation...")
    result = r.reql(correct_query)
    df = result.to_pandas()
    print(f"Results: {len(df)} rows")
    print(df.to_string())

    return df


def test_all_call_predicates():
    """Test to discover all predicates related to calls"""

    code = """
def caller_func():
    callee_func()

def callee_func():
    pass
"""

    r = Reter()
    r.load_python_code(code, "call_test")

    # Find all facts with "call" in the predicate
    query = """
    SELECT DISTINCT ?s ?p ?o
    WHERE {
        ?s ?p ?o
    }
    LIMIT 1000
    """

    result = r.reql(query)
    df = result.to_pandas()

    # Filter for call-related predicates
    call_facts = df[
        df['?p'].str.contains('call', case=False, na=False) |
        df['?s'].str.contains('call', case=False, na=False) |
        df['?o'].str.contains('call', case=False, na=False)
    ]

    print(f"\n📋 Call-related facts ({len(call_facts)} found):")
    print(call_facts.to_string())

    return call_facts


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Call Graph Extraction")
    print("=" * 60)

    print("\n" + "=" * 60)
    print("Test 1: Simple Function Call")
    print("=" * 60)
    try:
        test_simple_function_call()
    except Exception as e:
        print(f"❌ FAILED: {e}")

    print("\n" + "=" * 60)
    print("Test 2: Method Calls")
    print("=" * 60)
    try:
        test_method_call()
    except Exception as e:
        print(f"❌ FAILED: {e}")

    print("\n" + "=" * 60)
    print("Test 3: Query Structure (from feedback)")
    print("=" * 60)
    try:
        test_query_structure()
    except Exception as e:
        print(f"❌ FAILED: {e}")

    print("\n" + "=" * 60)
    print("Test 4: Discover All Call Predicates")
    print("=" * 60)
    try:
        test_all_call_predicates()
    except Exception as e:
        print(f"❌ FAILED: {e}")

    print("\n" + "=" * 60)
    print("Testing Complete")
    print("=" * 60)
