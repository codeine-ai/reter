"""
Test Suite for Query Result Indexing (Week 6, Day 1-2)

Tests C++-optimized indexed access and slicing for query results.
Expected behavior: Zero-copy indexed access without materializing entire result set.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from reter import Reter


def test_basic_indexing():
    """Test basic integer indexing"""
    print("\n=== Test 1: Basic indexing ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
        Person（bob）
        hasAge（john，30）
        hasAge（mary，25）
        hasAge（bob，35）
    """)

    results = r.pattern(("?x", "type", "Person"), ("?x", "hasAge", "?age"))

    # Test first result
    first = results[0]
    print(f"First result: {first}")
    assert "?x" in first and "?age" in first

    # Test last result (negative indexing)
    last = results[-1]
    print(f"Last result: {last}")
    assert "?x" in last and "?age" in last

    # Test middle result
    middle = results[1]
    print(f"Middle result: {middle}")
    assert "?x" in middle and "?age" in middle

    print("✓ Basic indexing test passed")


def test_slicing():
    """Test slice operations"""
    print("\n=== Test 2: Slicing ===")

    r = Reter()

    # Create 10 people
    ontology = []
    for i in range(10):
        ontology.append(f"Person（person{i}）")
        ontology.append(f"hasAge（person{i}，{20+i}）")

    r.load_ontology("\n".join(ontology))

    results = r.pattern(("?x", "type", "Person"), ("?x", "hasAge", "?age"))

    # Test slice
    first_five = results[:5]
    print(f"First 5 results: {len(first_five)} items")
    assert len(first_five) == 5

    # Test range slice
    middle = results[3:7]
    print(f"Results [3:7]: {len(middle)} items")
    assert len(middle) == 4

    # Test step slice
    every_other = results[::2]
    print(f"Every other result: {len(every_other)} items")
    assert len(every_other) == 5

    print("✓ Slicing test passed")


def test_out_of_bounds():
    """Test out of bounds access"""
    print("\n=== Test 3: Out of bounds ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
    """)

    results = r.pattern(("?x", "type", "Person"))

    # Test out of bounds
    try:
        _ = results[10]  # Only 2 results
        assert False, "Should have raised IndexError"
    except IndexError:
        print("✓ Correctly raised IndexError for out of bounds access")

    print("✓ Out of bounds test passed")


def test_negative_indexing():
    """Test negative indexing"""
    print("\n=== Test 4: Negative indexing ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
        Person（bob）
    """)

    results = r.pattern(("?x", "type", "Person"))

    # Test negative indices
    last = results[-1]
    second_last = results[-2]
    first_negative = results[-3]

    print(f"Last: {last}")
    print(f"Second last: {second_last}")
    print(f"First (via -3): {first_negative}")

    # Should match positive indexing
    assert results[0] == results[-3]
    assert results[1] == results[-2]
    assert results[2] == results[-1]

    print("✓ Negative indexing test passed")


def test_empty_slice():
    """Test empty slice"""
    print("\n=== Test 5: Empty slice ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
    """)

    results = r.pattern(("?x", "type", "Person"))

    # Empty slice
    empty = results[5:10]  # Beyond available results
    print(f"Empty slice: {len(empty)} items")
    assert len(empty) == 0

    print("✓ Empty slice test passed")


def test_large_result_set():
    """Test indexing with large result sets"""
    print("\n=== Test 6: Large result set ===")

    r = Reter()

    # Create 100 people
    ontology = []
    for i in range(100):
        ontology.append(f"Person（person{i}）")

    r.load_ontology("\n".join(ontology))

    results = r.pattern(("?x", "type", "Person"))

    # Access various indices without materializing all results
    # Don't assert specific values since order isn't guaranteed
    first = results[0]
    assert "?x" in first
    assert first["?x"].startswith("person")

    middle = results[50]
    assert "?x" in middle
    assert middle["?x"].startswith("person")

    last = results[99]
    assert "?x" in last
    assert last["?x"].startswith("person")

    # Verify negative indexing works
    last_neg = results[-1]
    assert "?x" in last_neg

    # Slice
    subset = results[10:20]
    assert len(subset) == 10

    print(f"✓ Large result set test passed (100 results)")


def test_with_variables():
    """Test indexing with variable selection"""
    print("\n=== Test 7: With variable selection ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
        hasAge（john，30）
        hasAge（mary，25）
    """)

    # Select only ?x
    results = r.pattern(
        ("?x", "type", "Person"),
        ("?x", "hasAge", "?age"),
        select=["?x"]
    )

    first = results[0]
    print(f"First result (selected vars): {first}")

    assert "?x" in first
    assert "?age" not in first  # Not selected

    print("✓ Variable selection test passed")


def test_combined_operations():
    """Test combining indexing with iteration"""
    print("\n=== Test 8: Combined operations ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
        Person（bob）
    """)

    results = r.pattern(("?x", "type", "Person"))

    # Mix indexing and iteration
    first_via_index = results[0]
    print(f"First via index: {first_via_index}")

    # Iterate
    count = 0
    for r in results:
        count += 1

    assert count == 3

    # Index again after iteration
    last_via_index = results[-1]
    print(f"Last via index: {last_via_index}")

    print("✓ Combined operations test passed")


def run_all_tests():
    """Run all indexing tests"""
    print("=" * 70)
    print("Query Result Indexing Test Suite (Week 6, Day 1-2)")
    print("=" * 70)

    tests = [
        test_basic_indexing,
        test_slicing,
        test_out_of_bounds,
        test_negative_indexing,
        test_empty_slice,
        test_large_result_set,
        test_with_variables,
        test_combined_operations,
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
