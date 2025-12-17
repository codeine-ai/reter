"""
Test Suite for UNION Support (Week 5, Day 4-5)

Tests combining multiple query results using UNION (OR semantics).
Expected behavior: Results from multiple queries are merged and deduplicated.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from reter import Reter


def test_union_basic():
    """Test basic UNION of two queries"""
    print("\n=== Test 1: Basic UNION ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
        Student（alice）
        Student（bob）
    """)

    # Get people OR students
    q1 = r.pattern(("?x", "type", "Person"))
    q2 = r.pattern(("?x", "type", "Student"))

    results = r.union(q1, q2)
    result_list = results.to_list()

    print(f"Results: {len(result_list)} individuals")

    # Should get all 4: john, mary, alice, bob
    assert len(result_list) == 4, f"Expected 4 results, got {len(result_list)}"

    individuals = {r["?x"] for r in result_list}
    assert individuals == {"john", "mary", "alice", "bob"}, f"Unexpected individuals: {individuals}"

    print("✓ Basic UNION test passed")


def test_union_with_overlap():
    """Test UNION with overlapping results (deduplication)"""
    print("\n=== Test 2: UNION with overlap ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
        hasAge（john，30）
        hasAge（mary，25）
    """)

    # Query 1: All people (only ?x variable)
    q1 = r.pattern(("?x", "type", "Person"), select=["?x"])

    # Query 2: People (only ?x variable) - should be identical to q1
    q2 = r.pattern(
        ("?x", "type", "Person"),
        ("?x", "hasAge", "?age"),
        select=["?x"]
    )

    results = r.union(q1, q2)
    result_list = results.to_list()

    print(f"Results: {len(result_list)} people")

    # With select=[\"?x\"], both queries return same structure, so deduplication works
    assert len(result_list) == 2, f"Expected 2 results, got {len(result_list)}"

    people = {r["?x"] for r in result_list}
    assert people == {"john", "mary"}

    print("✓ UNION with overlap test passed")


def test_union_three_queries():
    """Test UNION of three queries"""
    print("\n=== Test 3: UNION of three queries ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Student（alice）
        Teacher（bob）
    """)

    q1 = r.pattern(("?x", "type", "Person"))
    q2 = r.pattern(("?x", "type", "Student"))
    q3 = r.pattern(("?x", "type", "Teacher"))

    results = r.union(q1, q2, q3)
    result_list = results.to_list()

    print(f"Results: {len(result_list)} individuals")

    assert len(result_list) == 3, f"Expected 3 results, got {len(result_list)}"

    individuals = {r["?x"] for r in result_list}
    assert individuals == {"john", "alice", "bob"}

    print("✓ Three-query UNION test passed")


def test_union_different_variables():
    """Test UNION with queries having different variables"""
    print("\n=== Test 4: UNION with different variables ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
        hasAge（john，30）
        livesIn（mary，NYC）
    """)

    # Query 1: Get people and their ages
    q1 = r.pattern(
        ("?x", "type", "Person"),
        ("?x", "hasAge", "?age")
    )

    # Query 2: Get people and their cities
    q2 = r.pattern(
        ("?x", "type", "Person"),
        ("?x", "livesIn", "?city")
    )

    results = r.union(q1, q2)
    result_list = results.to_list()

    print(f"Results: {len(result_list)} bindings")

    # Should get 2 results with potentially different variables
    assert len(result_list) == 2, f"Expected 2 results, got {len(result_list)}"

    # john should have ?age, mary should have ?city
    john = next((r for r in result_list if r.get("?x") == "john"), None)
    mary = next((r for r in result_list if r.get("?x") == "mary"), None)

    assert john is not None and "?age" in john
    assert mary is not None and "?city" in mary

    print("✓ Different variables UNION test passed")


def test_union_empty_query():
    """Test UNION with one empty query"""
    print("\n=== Test 5: UNION with empty query ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
    """)

    q1 = r.pattern(("?x", "type", "Person"))
    q2 = r.pattern(("?x", "type", "NonExistent"))  # No results

    results = r.union(q1, q2)
    result_list = results.to_list()

    print(f"Results: {len(result_list)} people")

    # Should get 2 from q1 (q2 contributes nothing)
    assert len(result_list) == 2, f"Expected 2 results, got {len(result_list)}"

    people = {r["?x"] for r in result_list}
    assert people == {"john", "mary"}

    print("✓ Empty query UNION test passed")


def test_union_with_filters():
    """Test UNION where queries have filters"""
    print("\n=== Test 6: UNION with filters ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
        Person（bob）
        hasAge（john，30）
        hasAge（mary，25）
        hasAge（bob，35）
    """)

    # Young people (age <= 25)
    q1 = r.pattern(
        ("?x", "type", "Person"),
        ("?x", "hasAge", "?age"),
        where=[("≤", "?age", "25")]  # lessThanOrEqual
    )

    # Old people (age >= 35)
    q2 = r.pattern(
        ("?x", "type", "Person"),
        ("?x", "hasAge", "?age"),
        where=[("≥", "?age", "35")]  # greaterThanOrEqual
    )

    results = r.union(q1, q2)
    result_list = results.to_list()

    print(f"Results: {len(result_list)} people")

    # Should get mary (25) and bob (35), not john (30)
    assert len(result_list) == 2, f"Expected 2 results, got {len(result_list)}"

    people = {r["?x"] for r in result_list}
    assert people == {"mary", "bob"}, f"Unexpected people: {people}"
    assert "john" not in people

    print("✓ Filtered UNION test passed")


def test_union_with_values():
    """Test UNION where queries have VALUES constraints"""
    print("\n=== Test 7: UNION with VALUES ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
        Person（bob）
        Person（alice）
        livesIn（john，NYC）
        livesIn（mary，LA）
        livesIn（bob，Chicago）
        livesIn（alice，Boston）
    """)

    # People in NYC or LA
    q1 = r.pattern(
        ("?x", "livesIn", "?city"),
        values={"?city": ["NYC", "LA"]}
    )

    # People in Chicago or Boston
    q2 = r.pattern(
        ("?x", "livesIn", "?city"),
        values={"?city": ["Chicago", "Boston"]}
    )

    results = r.union(q1, q2)
    result_list = results.to_list()

    print(f"Results: {len(result_list)} people")

    # Should get all 4
    assert len(result_list) == 4, f"Expected 4 results, got {len(result_list)}"

    people = {r["?x"] for r in result_list}
    assert people == {"john", "mary", "bob", "alice"}

    print("✓ VALUES UNION test passed")


def test_union_iteration():
    """Test iteration over UNION results"""
    print("\n=== Test 8: UNION iteration ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Student（alice）
    """)

    q1 = r.pattern(("?x", "type", "Person"))
    q2 = r.pattern(("?x", "type", "Student"))

    results = r.union(q1, q2)

    # Test __iter__
    count = 0
    individuals = set()
    for binding in results:
        count += 1
        individuals.add(binding["?x"])
        print(f"  Found: {binding['?x']}")

    assert count == 2, f"Expected 2 iterations, got {count}"
    assert individuals == {"john", "alice"}

    # Test __len__
    assert len(results) == 2, f"Expected len=2, got {len(results)}"

    print("✓ Iteration test passed")


def test_union_pandas():
    """Test pandas conversion with UNION"""
    print("\n=== Test 9: UNION with pandas ===")

    try:
        import pandas as pd
    except ImportError:
        print("⊘ pandas not installed, skipping test")
        return

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
        Student（alice）
        Student（bob）
    """)

    q1 = r.pattern(("?x", "type", "Person"))
    q2 = r.pattern(("?x", "type", "Student"))

    results = r.union(q1, q2)

    # Convert to pandas
    df = results.to_pandas()
    print(f"DataFrame shape: {df.shape}")
    print(df)

    assert "?x" in df.columns
    assert len(df) == 4

    individuals = set(df["?x"].values)
    assert individuals == {"john", "mary", "alice", "bob"}

    print("✓ Pandas test passed")


def test_union_select():
    """Test UNION with variable selection"""
    print("\n=== Test 10: UNION with select ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
        hasAge（john，30）
        livesIn（mary，NYC）
    """)

    # Both queries select only ?x
    q1 = r.pattern(
        ("?x", "type", "Person"),
        ("?x", "hasAge", "?age"),
        select=["?x"]
    )

    q2 = r.pattern(
        ("?x", "type", "Person"),
        ("?x", "livesIn", "?city"),
        select=["?x"]
    )

    results = r.union(q1, q2)
    result_list = results.to_list()

    # Should only have ?x in results, not ?age or ?city
    for r in result_list:
        assert "?x" in r
        assert "?age" not in r
        assert "?city" not in r

    people = {r["?x"] for r in result_list}
    assert people == {"john", "mary"}

    print("✓ Select test passed")


def run_all_tests():
    """Run all UNION tests"""
    print("=" * 70)
    print("UNION Support Test Suite (Week 5, Day 4-5)")
    print("=" * 70)

    tests = [
        test_union_basic,
        test_union_with_overlap,
        test_union_three_queries,
        test_union_different_variables,
        test_union_empty_query,
        test_union_with_filters,
        test_union_with_values,
        test_union_iteration,
        test_union_pandas,
        test_union_select,
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
