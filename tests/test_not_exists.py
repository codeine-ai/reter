"""
Test Suite for NOT EXISTS Support (Week 5, Day 1-3)

Tests negative pattern filtering using NOT EXISTS constraints.
Expected behavior: Queries filter out results that match NOT EXISTS patterns.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from reter import Reter


def test_not_exists_basic():
    """Test basic NOT EXISTS constraint"""
    print("\n=== Test 1: Basic NOT EXISTS ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
        Person（bob）
        hasChild（john，alice）
        hasChild（mary，charlie）
    """)

    # Find people who don't have children
    results = r.pattern(
        ("?x", "type", "Person"),
        not_exists=[("?x", "hasChild", "?y")]
    )

    result_list = results.to_list()
    print(f"Results: {len(result_list)} people without children")

    # Only bob should be returned (john and mary have children)
    assert len(result_list) == 1, f"Expected 1 result, got {len(result_list)}"
    assert result_list[0]["?x"] == "bob", f"Expected bob, got {result_list[0]['?x']}"

    print("✓ Basic NOT EXISTS test passed")


def test_not_exists_multiple_patterns():
    """Test NOT EXISTS with multiple patterns (all must not exist)"""
    print("\n=== Test 2: NOT EXISTS with multiple patterns ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
        Person（bob）
        hasChild（john，alice）
        livesIn（mary，NYC）
    """)

    # Find people who don't have children AND don't live somewhere
    results = r.pattern(
        ("?x", "type", "Person"),
        not_exists=[
            ("?x", "hasChild", "?y"),
            ("?x", "livesIn", "?city")
        ]
    )

    result_list = results.to_list()
    print(f"Results: {len(result_list)} people")

    # Only bob should be returned
    assert len(result_list) == 1, f"Expected 1 result, got {len(result_list)}"
    assert result_list[0]["?x"] == "bob"

    print("✓ Multiple pattern NOT EXISTS test passed")


def test_not_exists_with_variable_binding():
    """Test NOT EXISTS with variables bound in main pattern"""
    print("\n=== Test 3: NOT EXISTS with bound variables ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
        Person（bob）
        livesIn（john，NYC）
        livesIn（mary，LA）
        livesIn（bob，Chicago）
        hasChild（john，alice）
    """)

    # Find people who live somewhere but don't have children
    results = r.pattern(
        ("?x", "type", "Person"),
        ("?x", "livesIn", "?city"),
        not_exists=[("?x", "hasChild", "?y")]
    )

    result_list = results.to_list()
    print(f"Results: {len(result_list)} people")

    # mary and bob (not john who has a child)
    assert len(result_list) == 2, f"Expected 2 results, got {len(result_list)}"
    people = {r["?x"] for r in result_list}
    assert people == {"mary", "bob"}, f"Unexpected people: {people}"
    assert "john" not in people

    print("✓ NOT EXISTS with bound variables test passed")


def test_not_exists_all_filtered():
    """Test NOT EXISTS where all results are filtered out"""
    print("\n=== Test 4: NOT EXISTS filters all results ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
        hasChild（john，alice）
        hasChild（mary，bob）
    """)

    # All people have children, so should return empty
    results = r.pattern(
        ("?x", "type", "Person"),
        not_exists=[("?x", "hasChild", "?y")]
    )

    result_list = results.to_list()
    print(f"Results: {len(result_list)} people")

    assert len(result_list) == 0, f"Expected 0 results, got {len(result_list)}"

    print("✓ All filtered test passed")


def test_not_exists_none_filtered():
    """Test NOT EXISTS where no results are filtered"""
    print("\n=== Test 5: NOT EXISTS filters nothing ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
        Person（bob）
    """)

    # No one has children, so all should be returned
    results = r.pattern(
        ("?x", "type", "Person"),
        not_exists=[("?x", "hasChild", "?y")]
    )

    result_list = results.to_list()
    print(f"Results: {len(result_list)} people")

    assert len(result_list) == 3, f"Expected 3 results, got {len(result_list)}"
    people = {r["?x"] for r in result_list}
    assert people == {"john", "mary", "bob"}

    print("✓ None filtered test passed")


def test_not_exists_with_filters():
    """Test NOT EXISTS combined with WHERE filters"""
    print("\n=== Test 6: NOT EXISTS with WHERE filters ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
        Person（bob）
        hasAge（john，30）
        hasAge（mary，25）
        hasAge（bob，35）
        hasChild（john，alice）
    """)

    # Find people aged > 28 who don't have children
    results = r.pattern(
        ("?x", "type", "Person"),
        ("?x", "hasAge", "?age"),
        where=[("﹥", "?age", "28")],  # greaterThan
        not_exists=[("?x", "hasChild", "?y")]
    )

    result_list = results.to_list()
    print(f"Results: {len(result_list)} people")

    # bob (age 35, no children) - john is filtered by NOT EXISTS
    assert len(result_list) == 1, f"Expected 1 result, got {len(result_list)}"
    assert result_list[0]["?x"] == "bob"

    print("✓ NOT EXISTS with filters test passed")


def test_not_exists_with_values():
    """Test NOT EXISTS combined with VALUES"""
    print("\n=== Test 7: NOT EXISTS with VALUES ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
        Person（bob）
        Person（alice）
        livesIn（john，NYC）
        livesIn（mary，LA）
        livesIn（bob，Chicago）
        livesIn（alice，NYC）
        hasChild（john，charlie）
    """)

    # Find people in NYC or LA who don't have children
    results = r.pattern(
        ("?x", "type", "Person"),
        ("?x", "livesIn", "?city"),
        values={"?city": ["NYC", "LA"]},
        not_exists=[("?x", "hasChild", "?y")]
    )

    result_list = results.to_list()
    print(f"Results: {len(result_list)} people")

    # alice (NYC, no children) and mary (LA, no children)
    # john is filtered by NOT EXISTS
    assert len(result_list) == 2, f"Expected 2 results, got {len(result_list)}"
    people = {r["?x"] for r in result_list}
    assert people == {"alice", "mary"}

    print("✓ NOT EXISTS with VALUES test passed")


def test_not_exists_complex_pattern():
    """Test NOT EXISTS with complex patterns"""
    print("\n=== Test 8: NOT EXISTS with complex pattern ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
        Person（bob）
        hasChild（john，alice）
        hasAge（alice，5）
    """)

    # Find people who don't have children under age 10
    # NOT EXISTS pattern joins child with their age
    results = r.pattern(
        ("?x", "type", "Person"),
        not_exists=[
            ("?x", "hasChild", "?child"),
            ("?child", "hasAge", "?childAge")
        ]
    )

    result_list = results.to_list()
    print(f"Results: {len(result_list)} people")

    # mary and bob (no children with ages)
    # john is filtered because alice has an age
    assert len(result_list) == 2, f"Expected 2 results, got {len(result_list)}"
    people = {r["?x"] for r in result_list}
    assert people == {"mary", "bob"}

    print("✓ Complex pattern NOT EXISTS test passed")


def test_not_exists_select():
    """Test NOT EXISTS with variable selection"""
    print("\n=== Test 9: NOT EXISTS with select ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
        livesIn（john，NYC）
        livesIn（mary，LA）
        hasChild（john，alice）
    """)

    # Select only names, not cities
    results = r.pattern(
        ("?x", "type", "Person"),
        ("?x", "livesIn", "?city"),
        not_exists=[("?x", "hasChild", "?y")],
        select=["?x"]
    )

    result_list = results.to_list()

    assert len(result_list) == 1
    assert "?x" in result_list[0]
    assert "?city" not in result_list[0]  # Not selected
    assert result_list[0]["?x"] == "mary"

    print("✓ NOT EXISTS with select test passed")


def test_not_exists_pandas():
    """Test pandas conversion with NOT EXISTS"""
    print("\n=== Test 10: NOT EXISTS with pandas ===")

    try:
        import pandas as pd
    except ImportError:
        print("⊘ pandas not installed, skipping test")
        return

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
        Person（bob）
        livesIn（john，NYC）
        livesIn（mary，LA）
        livesIn（bob，Chicago）
        hasChild（mary，alice）
    """)

    results = r.pattern(
        ("?x", "type", "Person"),
        ("?x", "livesIn", "?city"),
        not_exists=[("?x", "hasChild", "?y")]
    )

    df = results.to_pandas()
    print(f"DataFrame shape: {df.shape}")
    print(df)

    assert len(df) == 2  # john and bob
    people = set(df["?x"].values)
    assert people == {"john", "bob"}
    assert "mary" not in people  # Filtered by NOT EXISTS

    print("✓ Pandas test passed")


def run_all_tests():
    """Run all NOT EXISTS tests"""
    print("=" * 70)
    print("NOT EXISTS Support Test Suite (Week 5, Day 1-3)")
    print("=" * 70)

    tests = [
        test_not_exists_basic,
        test_not_exists_multiple_patterns,
        test_not_exists_with_variable_binding,
        test_not_exists_all_filtered,
        test_not_exists_none_filtered,
        test_not_exists_with_filters,
        test_not_exists_with_values,
        test_not_exists_complex_pattern,
        test_not_exists_select,
        test_not_exists_pandas,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 70)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
