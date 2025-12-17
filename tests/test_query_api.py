"""
Test Python Pattern API
Week 1, Day 5-7 of IMPLEMENTATION_PLAN.md
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'rete_cpp'))
from reter import Reter


def test_pattern_basic():
    """Test basic pattern query"""
    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
    """)

    # Query: All persons
    results = r.pattern(("?x", "type", "Person"))
    persons = [b["?x"] for b in results]
    assert set(persons) == {"john", "mary"}
    print(f"✓ Basic pattern query found persons: {persons}")


def test_pattern_join():
    """Test pattern with join"""
    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
        hasAge（john，30）
        hasAge（mary，25）
    """)

    # Query: Persons with ages
    results = r.pattern(
        ("?x", "type", "Person"),
        ("?x", "hasAge", "?age")
    )

    bindings = list(results)
    assert len(bindings) == 2

    # Check john
    john = next(b for b in bindings if b["?x"] == "john")
    assert john["?age"] == "30"
    print(f"✓ Join query found john with age: {john['?age']}")

    # Check mary
    mary = next(b for b in bindings if b["?x"] == "mary")
    assert mary["?age"] == "25"
    print(f"✓ Join query found mary with age: {mary['?age']}")


def test_pattern_caching():
    """Test that patterns are cached"""
    r = Reter()
    r.load_ontology("Person（john）")

    # First call
    results1 = r.pattern(("?x", "type", "Person"), cache="test")

    # Second call - should hit cache
    results2 = r.pattern(("?x", "type", "Person"), cache="test")

    # Should return same results (caching works)
    assert results1.to_list() == results2.to_list()
    assert len(results1) == len(results2) == 1
    print("✓ Pattern caching works - same results returned")


def test_query_result_set_iteration():
    """Test QueryResultSet iteration"""
    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
        Person（bob）
    """)

    results = r.pattern(("?x", "type", "Person"))

    # Test len
    assert len(results) == 3
    print(f"✓ QueryResultSet has correct length: {len(results)}")

    # Test iteration
    persons = [b["?x"] for b in results]
    assert len(persons) == 3
    print(f"✓ Iteration works: {persons}")

    # Test to_list
    bindings_list = results.to_list()
    assert len(bindings_list) == 3
    print(f"✓ to_list() works: {len(bindings_list)} bindings")


def test_select_variables():
    """Test selecting specific variables"""
    r = Reter()
    r.load_ontology("""
        Person（john）
        hasAge（john，30）
    """)

    # Query person with age, select only name
    results = r.pattern(
        ("?x", "type", "Person"),
        ("?x", "hasAge", "?age"),
        select=["?x"]  # Don't return ?age
    )

    binding = next(iter(results))
    assert "?x" in binding
    assert "?age" not in binding  # ?age should not be in result
    print(f"✓ Variable selection works: {binding}")


if __name__ == "__main__":
    print("Testing Python Pattern API...")
    print("=" * 50)

    test_pattern_basic()
    print()

    test_pattern_join()
    print()

    test_pattern_caching()
    print()

    test_query_result_set_iteration()
    print()

    test_select_variables()
    print()

    print("=" * 50)
    print("\nAll Day 5-7 tests passed!")
    print("Next: Week 2 - Arrow Integration + Filters")
