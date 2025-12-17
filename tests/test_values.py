"""
Test Suite for VALUES Support (Week 5, Day 1-2)

Tests inline data filtering using VALUES constraints.
Expected behavior: Queries filter results to only include specified values.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from reter import Reter


def test_values_basic():
    """Test basic VALUES constraint"""
    print("\n=== Test 1: Basic VALUES ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
        Person（bob）
        livesIn（john，NYC）
        livesIn（mary，LA）
        livesIn（bob，Chicago）
    """)

    # Query with VALUES constraint - only NYC and LA
    results = r.pattern(
        ("?x", "livesIn", "?city"),
        values={"?city": ["NYC", "LA"]}
    )

    # Should only get john and mary (not bob from Chicago)
    result_list = results.to_list()
    print(f"Results: {len(result_list)} people in NYC or LA")

    assert len(result_list) == 2, f"Expected 2 results, got {len(result_list)}"

    cities = {r["?city"] for r in result_list}
    assert cities == {"NYC", "LA"}, f"Unexpected cities: {cities}"

    people = {r["?x"] for r in result_list}
    assert people == {"john", "mary"}, f"Unexpected people: {people}"
    assert "bob" not in people, "Bob from Chicago should not be in results"

    print("✓ Basic VALUES test passed")


def test_values_single_value():
    """Test VALUES with single value"""
    print("\n=== Test 2: Single value in VALUES ===")

    r = Reter()
    r.load_ontology("""
        Person（alice）
        Person（bob）
        Person（charlie）
        hasAge（alice，25）
        hasAge（bob，30）
        hasAge（charlie，25）
    """)

    # Query for only age 25
    results = r.pattern(
        ("?x", "type", "Person"),
        ("?x", "hasAge", "?age"),
        values={"?age": ["25"]}
    )

    result_list = results.to_list()
    print(f"Results: {len(result_list)} people aged 25")

    assert len(result_list) == 2, f"Expected 2 results, got {len(result_list)}"

    people = {r["?x"] for r in result_list}
    assert people == {"alice", "charlie"}, f"Unexpected people: {people}"

    print("✓ Single value test passed")


def test_values_multiple_variables():
    """Test VALUES with multiple variables"""
    print("\n=== Test 3: Multiple variable VALUES ===")

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
        hasAge（john，30）
        hasAge（mary，25）
        hasAge（bob，35）
        hasAge（alice，28）
    """)

    # Filter by both city and age
    results = r.pattern(
        ("?x", "livesIn", "?city"),
        ("?x", "hasAge", "?age"),
        values={
            "?city": ["NYC", "LA"],
            "?age": ["28", "30"]
        }
    )

    result_list = results.to_list()
    print(f"Results: {len(result_list)} people")

    # Should get john (NYC, 30) and alice (NYC, 28)
    # mary is LA but age 25 (not in age VALUES)
    # bob is Chicago (not in city VALUES)
    assert len(result_list) == 2, f"Expected 2 results, got {len(result_list)}"

    people = {r["?x"] for r in result_list}
    assert people == {"john", "alice"}, f"Unexpected people: {people}"

    print("✓ Multiple variable VALUES test passed")


def test_values_empty_results():
    """Test VALUES with no matching results"""
    print("\n=== Test 4: VALUES with no matches ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        livesIn（john，NYC）
    """)

    # Query for cities that don't exist
    results = r.pattern(
        ("?x", "livesIn", "?city"),
        values={"?city": ["Tokyo", "London", "Paris"]}
    )

    result_list = results.to_list()
    print(f"Results: {len(result_list)} people")

    assert len(result_list) == 0, f"Expected 0 results, got {len(result_list)}"

    print("✓ Empty results test passed")


def test_values_with_type_query():
    """Test VALUES combined with type queries"""
    print("\n=== Test 5: VALUES with type query ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
        Person（bob）
    """)

    # Filter Person instances by specific names
    results = r.pattern(
        ("?x", "type", "Person"),
        values={"?x": ["john", "mary"]}
    )

    result_list = results.to_list()
    print(f"Results: {len(result_list)} specific people")

    assert len(result_list) == 2, f"Expected 2 results, got {len(result_list)}"

    people = {r["?x"] for r in result_list}
    assert people == {"john", "mary"}, f"Unexpected people: {people}"
    assert "bob" not in people

    print("✓ VALUES with type query test passed")


def test_values_caching():
    """Test that VALUES queries are properly cached"""
    print("\n=== Test 6: VALUES caching ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
        livesIn（john，NYC）
        livesIn（mary，LA）
    """)

    # Run same query twice
    results1 = r.pattern(
        ("?x", "livesIn", "?city"),
        values={"?city": ["NYC"]}
    )

    results2 = r.pattern(
        ("?x", "livesIn", "?city"),
        values={"?city": ["NYC"]}
    )

    # Both should return same results
    list1 = results1.to_list()
    list2 = results2.to_list()

    assert len(list1) == len(list2) == 1
    assert list1[0]["?x"] == list2[0]["?x"] == "john"

    print("✓ Caching test passed")


def test_values_iteration():
    """Test iteration over VALUES results"""
    print("\n=== Test 7: VALUES iteration ===")

    r = Reter()
    r.load_ontology("""
        Person（alice）
        Person（bob）
        Person（charlie）
        hasAge（alice，25）
        hasAge（bob，30）
        hasAge（charlie，25）
    """)

    results = r.pattern(
        ("?x", "hasAge", "?age"),
        values={"?age": ["25", "30"]}
    )

    # Test __iter__
    count = 0
    people = set()
    for binding in results:
        count += 1
        people.add(binding["?x"])
        print(f"  Found: {binding['?x']} age {binding['?age']}")

    assert count == 3, f"Expected 3 iterations, got {count}"
    assert people == {"alice", "bob", "charlie"}

    # Test __len__
    assert len(results) == 3, f"Expected len=3, got {len(results)}"

    print("✓ Iteration test passed")


def test_values_select():
    """Test VALUES with variable selection"""
    print("\n=== Test 8: VALUES with select ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
        livesIn（john，NYC）
        livesIn（mary，LA）
    """)

    # Select only city variable
    results = r.pattern(
        ("?x", "livesIn", "?city"),
        values={"?city": ["NYC", "LA"]},
        select=["?city"]
    )

    result_list = results.to_list()

    # Should only have ?city in results
    for r in result_list:
        assert "?city" in r, "Expected ?city in results"
        assert "?x" not in r, "Did not expect ?x in results (select=[?city])"

    cities = {r["?city"] for r in result_list}
    assert cities == {"NYC", "LA"}

    print("✓ Select test passed")


def test_values_large_list():
    """Test VALUES with large value list"""
    print("\n=== Test 9: VALUES with large list ===")

    r = Reter()

    # Create ontology with many individuals
    ontology = []
    for i in range(100):
        ontology.append(f"Person（person{i}）")
        ontology.append(f"hasID（person{i}，{i}）")

    r.load_ontology("\n".join(ontology))

    # Filter for specific IDs (every 10th person)
    target_ids = [str(i) for i in range(0, 100, 10)]

    results = r.pattern(
        ("?x", "hasID", "?id"),
        values={"?id": target_ids}
    )

    result_list = results.to_list()
    print(f"Results: {len(result_list)} people with target IDs")

    assert len(result_list) == 10, f"Expected 10 results, got {len(result_list)}"

    ids = {r["?id"] for r in result_list}
    assert ids == set(target_ids), f"ID mismatch: {ids} vs {set(target_ids)}"

    print("✓ Large list test passed")


def test_values_pandas():
    """Test pandas conversion with VALUES"""
    print("\n=== Test 10: VALUES with pandas ===")

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
    """)

    results = r.pattern(
        ("?x", "livesIn", "?city"),
        values={"?city": ["NYC", "LA"]}
    )

    # Convert to pandas
    df = results.to_pandas()
    print(f"DataFrame shape: {df.shape}")
    print(df)

    assert "?x" in df.columns
    assert "?city" in df.columns
    assert len(df) == 2

    cities = set(df["?city"].values)
    assert cities == {"NYC", "LA"}

    print("✓ Pandas test passed")


def run_all_tests():
    """Run all VALUES tests"""
    print("=" * 70)
    print("VALUES Support Test Suite (Week 5, Day 1-2)")
    print("=" * 70)

    tests = [
        test_values_basic,
        test_values_single_value,
        test_values_multiple_variables,
        test_values_empty_results,
        test_values_with_type_query,
        test_values_caching,
        test_values_iteration,
        test_values_select,
        test_values_large_list,
        test_values_pandas,
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
