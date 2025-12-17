"""
Test Suite for Live Query API (Week 4, Day 4-7)

Tests auto-updating result sets that track fact changes incrementally.
Expected behavior: Live queries automatically reflect changes as facts are added.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from reter import Reter


def test_live_query_basic():
    """Test basic live query creation and access"""
    print("\n=== Test 1: Basic live query ===")

    r = Reter()

    # Load initial ontology
    r.load_ontology("""
        Person（john）
        Person（mary）
    """)

    # Create live query
    live = r.live_pattern(
        ("?x", "type", "Person")
    )

    # Check initial results
    results = live.to_list()
    print(f"Initial results: {len(results)} people")
    assert len(results) == 2, f"Expected 2 people, got {len(results)}"

    # Check individuals
    individuals = {r["?x"] for r in results}
    assert individuals == {"john", "mary"}, f"Unexpected individuals: {individuals}"

    print("✓ Basic live query test passed")


def test_live_query_auto_update():
    """Test that live queries auto-update when facts are added"""
    print("\n=== Test 2: Auto-update on fact addition ===")

    r = Reter()

    # Load initial ontology
    r.load_ontology("""
        Person（john）
        Person（mary）
    """)

    # Create live query
    live = r.live_pattern(
        ("?x", "type", "Person")
    )

    # Check initial count
    initial_count = len(live)
    print(f"Initial count: {initial_count}")
    assert initial_count == 2

    # Add new person
    r.load_ontology("""
        Person（bob）
    """)

    # Check that live query automatically updated
    new_count = len(live)
    print(f"After adding bob: {new_count}")
    assert new_count == 3, f"Expected 3 people after addition, got {new_count}"

    # Verify new person is in results
    individuals = {r["?x"] for r in live}
    assert "bob" in individuals, "New person 'bob' not found in live query results"

    print("✓ Auto-update test passed")


def test_live_query_iteration():
    """Test iteration over live query results"""
    print("\n=== Test 3: Live query iteration ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
    """)

    live = r.live_pattern(("?x", "type", "Person"))

    # Test __iter__
    count = 0
    individuals = set()
    for binding in live:
        count += 1
        individuals.add(binding["?x"])
        print(f"  Found: {binding['?x']}")

    assert count == 2, f"Expected 2 iterations, got {count}"
    assert individuals == {"john", "mary"}

    # Test __len__
    assert len(live) == 2, f"Expected len=2, got {len(live)}"

    print("✓ Iteration test passed")


def test_live_query_join():
    """Test live query with joins (multiple patterns)"""
    print("\n=== Test 4: Live query with joins ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
        hasAge（john，30）
        hasAge（mary，25）
    """)

    # Live query with join
    live = r.live_pattern(
        ("?x", "type", "Person"),
        ("?x", "hasAge", "?age")
    )

    # Check initial results
    initial_results = live.to_list()
    print(f"Initial: {len(initial_results)} people with age")
    assert len(initial_results) == 2

    # Add new person with age
    r.load_ontology("""
        Person（bob）
        hasAge（bob，35）
    """)

    # Check auto-update
    new_results = live.to_list()
    print(f"After adding bob: {len(new_results)} people with age")
    assert len(new_results) == 3, f"Expected 3 people with age, got {len(new_results)}"

    # Verify bob is in results
    names = {r["?x"] for r in new_results}
    assert "bob" in names

    print("✓ Join test passed")


def test_live_query_with_filters():
    """Test live query with SWRL builtin filters"""
    print("\n=== Test 5: Live query with filters ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
        Person（bob）
        hasAge（john，30）
        hasAge（mary，22）
        hasAge（bob，18）
    """)

    # Live query with filter (age > 21)
    adults = r.live_pattern(
        ("?x", "type", "Person"),
        ("?x", "hasAge", "?age"),
        where=[("﹥", "?age", "21")]  # greaterThan
    )

    # Check initial results (john=30, mary=22)
    initial_count = len(adults)
    print(f"Initial adults (age > 21): {initial_count}")
    assert initial_count == 2, f"Expected 2 adults, got {initial_count}"

    # Add new adult
    r.load_ontology("""
        Person（alice）
        hasAge（alice，28）
    """)

    # Check auto-update
    new_count = len(adults)
    print(f"After adding alice (28): {new_count}")
    assert new_count == 3, f"Expected 3 adults, got {new_count}"

    print("✓ Filter test passed")


def test_live_query_caching():
    """Test that live queries use caching"""
    print("\n=== Test 6: Live query caching ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
    """)

    # Create two live queries with same pattern
    live1 = r.live_pattern(("?x", "type", "Person"), cache="test_cache")
    live2 = r.live_pattern(("?x", "type", "Person"), cache="test_cache")

    # Both should see same results
    assert len(live1) == len(live2), "Cached queries should return same count"

    # Add new fact
    r.load_ontology("""Person（bob）""")

    # Both should auto-update
    assert len(live1) == 3, "First live query should auto-update"
    assert len(live2) == 3, "Second live query should auto-update"

    print("✓ Caching test passed")


def test_live_query_pandas():
    """Test pandas conversion with live queries"""
    print("\n=== Test 7: Pandas conversion ===")

    try:
        import pandas as pd
    except ImportError:
        print("⊘ pandas not installed, skipping test")
        return

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
        hasAge（john，30）
        hasAge（mary，25）
    """)

    live = r.live_pattern(
        ("?x", "type", "Person"),
        ("?x", "hasAge", "?age")
    )

    # Convert to pandas (snapshot)
    df = live.to_pandas()
    print(f"DataFrame shape: {df.shape}")
    print(df)

    assert "?x" in df.columns
    assert "?age" in df.columns
    assert len(df) == 2

    # Add new person
    r.load_ontology("""
        Person（bob）
        hasAge（bob，35）
    """)

    # Convert again (new snapshot)
    df2 = live.to_pandas()
    print(f"After update: {df2.shape}")
    assert len(df2) == 3, f"Expected 3 rows after update, got {len(df2)}"

    print("✓ Pandas test passed")


def test_live_query_empty_results():
    """Test live queries with no results"""
    print("\n=== Test 8: Empty results ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
    """)

    # Query for non-existent class
    live = r.live_pattern(("?x", "type", "Animal"))

    # Should return empty results
    assert len(live) == 0, f"Expected 0 results, got {len(live)}"

    results_list = live.to_list()
    assert results_list == [], "Expected empty list"

    # Add matching fact
    r.load_ontology("""Animal（dog）""")

    # Should auto-update to include new fact
    assert len(live) == 1, f"Expected 1 result after adding Animal, got {len(live)}"

    print("✓ Empty results test passed")


def test_live_query_variable_selection():
    """Test live query with variable selection"""
    print("\n=== Test 9: Variable selection ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
        hasAge（john，30）
        hasAge（mary，25）
    """)

    # Select only age variable
    live = r.live_pattern(
        ("?x", "type", "Person"),
        ("?x", "hasAge", "?age"),
        select=["?age"]
    )

    results = live.to_list()
    print(f"Selected variables: {results}")

    # Should only have ?age in results
    for r in results:
        assert "?age" in r, "Expected ?age in results"
        assert "?x" not in r, "Did not expect ?x in results"

    print("✓ Variable selection test passed")


def test_live_query_repr():
    """Test LiveQueryResultSet representation"""
    print("\n=== Test 10: LiveQueryResultSet repr ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
    """)

    live = r.live_pattern(("?x", "type", "Person"))

    repr_str = repr(live)
    print(f"repr: {repr_str}")

    assert "LiveQueryResultSet" in repr_str
    assert "2 results" in repr_str
    assert "?x" in repr_str

    print("✓ Repr test passed")


def run_all_tests():
    """Run all live query tests"""
    print("=" * 70)
    print("Live Query API Test Suite (Week 4, Day 4-7)")
    print("=" * 70)

    tests = [
        test_live_query_basic,
        test_live_query_auto_update,
        test_live_query_iteration,
        test_live_query_join,
        test_live_query_with_filters,
        test_live_query_caching,
        test_live_query_pandas,
        test_live_query_empty_results,
        test_live_query_variable_selection,
        test_live_query_repr,
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
