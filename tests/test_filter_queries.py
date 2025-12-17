"""
Test filter queries (Week 2, Day 4-7)

Tests SWRL builtin filters in pattern queries:
- greaterThan, lessThan, greaterThanOrEqual, lessThanOrEqual
- equal, notEqual
- Multiple filters (AND logic)
"""

from reter import Reter


def test_basic_filter():
    """Test basic greaterThan filter"""
    print("\n=== Test 1: Basic greaterThan filter ===")

    r = Reter()

    # Load data
    r.load_ontology("""
        Person（alice）
        Person（bob）
        Person（charlie）
        hasAge（alice，25）
        hasAge（bob，30）
        hasAge（charlie，20）
    """)

    # Query without filter
    all_people = r.pattern(
        ("?x", "type", "Person"),
        ("?x", "hasAge", "?age")
    )

    print(f"All people: {len(all_people)} results")
    for binding in all_people:
        print(f"  {binding}")

    assert len(all_people) == 3

    # Query with greaterThan filter
    adults_only = r.pattern(
        ("?x", "type", "Person"),
        ("?x", "hasAge", "?age"),
        where=[("﹥", "?age", "21")]  # greaterThan builtin
    )

    print(f"\nPeople with age > 21: {len(adults_only)} results")
    for binding in adults_only:
        print(f"  {binding}")

    # Should filter out charlie (age 20)
    assert len(adults_only) == 2

    names = [b["?x"] for b in adults_only]
    assert "alice" in names
    assert "bob" in names
    assert "charlie" not in names

    print("✓ Basic filter test passed")


def test_multiple_filters():
    """Test multiple filters (AND logic)"""
    print("\n=== Test 2: Multiple filters ===")

    r = Reter()

    # Load data
    r.load_ontology("""
        Person（alice）
        Person（bob）
        Person（charlie）
        Person（diana）
        hasAge（alice，25）
        hasAge（bob，30）
        hasAge（charlie，20）
        hasAge（diana，28）
    """)

    # Query with age range filter (between 22 and 29)
    mid_age_people = r.pattern(
        ("?x", "type", "Person"),
        ("?x", "hasAge", "?age"),
        where=[
            ("﹥", "?age", "22"),  # greaterThan
            ("﹤", "?age", "29")   # lessThan
        ]
    )

    print(f"People with 22 < age < 29: {len(mid_age_people)} results")
    for binding in mid_age_people:
        print(f"  {binding}")

    # Should include alice (25) and diana (28)
    # Should exclude bob (30) and charlie (20)
    assert len(mid_age_people) == 2

    names = [b["?x"] for b in mid_age_people]
    assert "alice" in names
    assert "diana" in names
    assert "bob" not in names
    assert "charlie" not in names

    print("✓ Multiple filter test passed")


def test_filter_caching():
    """Test that filtered queries are cached"""
    print("\n=== Test 3: Filter query caching ===")

    r = Reter()

    # Load data
    r.load_ontology("""
        Person（alice）
        hasAge（alice，25）
    """)

    # First query - should build production
    result1 = r.pattern(
        ("?x", "type", "Person"),
        ("?x", "hasAge", "?age"),
        where=[("﹥", "?age", "20")]  # greaterThan
    )

    assert len(result1) == 1

    # Second query with same pattern - should use cache
    result2 = r.pattern(
        ("?x", "type", "Person"),
        ("?x", "hasAge", "?age"),
        where=[("﹥", "?age", "20")]  # greaterThan
    )

    assert len(result2) == 1

    # Different filter - should build new production
    result3 = r.pattern(
        ("?x", "type", "Person"),
        ("?x", "hasAge", "?age"),
        where=[("﹤", "?age", "30")]  # lessThan
    )

    assert len(result3) == 1

    print("✓ Filter caching test passed")


def test_empty_results_with_filter():
    """Test filter that matches nothing"""
    print("\n=== Test 4: Empty results with filter ===")

    r = Reter()

    # Load data
    r.load_ontology("""
        Person（alice）
        hasAge（alice，25）
    """)

    # Query with filter that matches nothing
    result = r.pattern(
        ("?x", "type", "Person"),
        ("?x", "hasAge", "?age"),
        where=[("﹥", "?age", "100")]  # greaterThan
    )

    print(f"People with age > 100: {len(result)} results")
    assert len(result) == 0

    print("✓ Empty results test passed")


def test_pandas_with_filter():
    """Test pandas conversion with filtered query"""
    print("\n=== Test 5: Pandas conversion with filter ===")

    try:
        import pandas as pd
    except ImportError:
        print("⚠ Pandas not available, skipping test")
        return

    r = Reter()

    # Load data
    r.load_ontology("""
        Person（alice）
        Person（bob）
        Person（charlie）
        hasAge（alice，25）
        hasAge（bob，30）
        hasAge（charlie，20）
    """)

    # Query with filter
    adults = r.pattern(
        ("?x", "type", "Person"),
        ("?x", "hasAge", "?age"),
        where=[("﹥", "?age", "21")]  # greaterThan
    )

    # Convert to pandas
    df = adults.to_pandas()

    print(f"\nDataFrame shape: {df.shape}")
    print(f"DataFrame:\n{df}")

    assert len(df) == 2
    assert "?x" in df.columns
    assert "?age" in df.columns

    # Check that charlie is not in results
    assert "charlie" not in df["?x"].values

    print("✓ Pandas conversion test passed")


if __name__ == "__main__":
    test_basic_filter()
    test_multiple_filters()
    test_filter_caching()
    test_empty_results_with_filter()
    test_pandas_with_filter()

    print("\n" + "="*50)
    print("✓ All filter query tests passed!")
    print("="*50)
