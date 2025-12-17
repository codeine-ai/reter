"""
Test Arrow query functions (query and find_facts_arrow)

This test suite verifies:
1. query() with empty pattern (returns all facts)
2. query() with single filter
3. query() with multiple filters (AND logic)
4. query() with non-existent column (returns empty table)
5. find_facts_arrow() as alias
6. Zero-copy behavior (cache hits)
7. Correctness vs. existing query() function
8. Performance improvements over query()
9. Cache invalidation scenarios
"""

import time
import pytest
from reter import Reter


def test_query_empty_pattern():
    """Test 1: Empty pattern should return all facts"""
    print("=" * 60)
    print("Test 1: query() with empty pattern")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Dog ⊑ᑦ Animal
    Cat ⊑ᑦ Animal
    Dog（Fido）
    Cat（Whiskers）
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Get all facts with get_all_facts_arrow()
    all_facts = reasoner.get_all_facts()
    all_count = all_facts.num_rows

    # Query with empty pattern
    query_result = reasoner.network.query({})
    query_count = query_result.num_rows

    print(f"  get_all_facts_arrow(): {all_count} facts")
    print(f"  query({{}}):      {query_count} facts")

    assert query_count == all_count, "Empty pattern should return all facts"
    print("  ✓ Empty pattern returns all facts\n")


def test_query_single_filter():
    """Test 2: Single filter (type='instance_of')"""
    print("=" * 60)
    print("Test 2: query() with single filter")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Dog ⊑ᑦ Animal
    Dog（Fido）
    Dog（Rex）
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Query for instance_of facts
    result = reasoner.network.query({'type': 'instance_of'})
    df = result.to_pandas()

    print(f"  Total facts: {result.num_rows}")
    print(f"  Columns: {result.schema.names}")
    print(f"  Instance_of facts: {len(df)}")

    # Verify all results have type='instance_of'
    assert all(df['type'] == 'instance_of'), "All results should have type='instance_of'"
    print("  ✓ Single filter works correctly\n")


def test_query_multiple_filters():
    """Test 3: Multiple filters (AND logic)"""
    print("=" * 60)
    print("Test 3: query() with multiple filters (AND)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Dog ⊑ᑦ Animal
    Cat ⊑ᑦ Animal
    Dog（Fido）
    Dog（Rex）
    Cat（Whiskers）
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Query for Dog instances only
    result = reasoner.network.query({
        'type': 'instance_of',
        'concept': 'Dog'
    })
    df = result.to_pandas()

    print(f"  Total matching facts: {result.num_rows}")
    print(f"  Individuals: {df['individual'].tolist()}")

    # Verify all results match BOTH filters
    assert all(df['type'] == 'instance_of'), "All results should have type='instance_of'"
    assert all(df['concept'] == 'Dog'), "All results should have concept='Dog'"
    assert 'Fido' in df['individual'].values, "Fido should be in results"
    assert 'Rex' in df['individual'].values, "Rex should be in results"
    assert 'Whiskers' not in df['individual'].values, "Whiskers should NOT be in results"
    print("  ✓ Multiple filters (AND) work correctly\n")


def test_query_nonexistent_column():
    """Test 4: Non-existent column returns empty table"""
    print("=" * 60)
    print("Test 4: query() with non-existent column")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Dog ⊑ᑦ Animal
    Dog（Fido）
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Query with non-existent column
    result = reasoner.network.query({'nonexistent_column': 'value'})

    print(f"  Result rows: {result.num_rows}")
    assert result.num_rows == 0, "Non-existent column should return empty table"
    print("  ✓ Non-existent column returns empty table\n")


def test_query_no_matches():
    """Test 5: Pattern with no matches returns empty table"""
    print("=" * 60)
    print("Test 5: query() with no matches")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Dog ⊑ᑦ Animal
    Dog（Fido）
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Query for non-existent individual
    result = reasoner.network.query({
        'type': 'instance_of',
        'individual': 'NonExistentDog'
    })

    print(f"  Result rows: {result.num_rows}")
    assert result.num_rows == 0, "No matches should return empty table"
    print("  ✓ No matches returns empty table\n")


def test_find_facts_arrow_alias():
    """Test 6: find_facts_arrow() is alias for query()"""
    print("=" * 60)
    print("Test 6: find_facts_arrow() alias")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Dog ⊑ᑦ Animal
    Dog（Fido）
    Dog（Rex）
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Call both functions with same pattern
    pattern = {'type': 'instance_of', 'concept': 'Dog'}
    query_result = reasoner.network.query(pattern)
    find_result = reasoner.network.find_facts_arrow(pattern)

    print(f"  query() rows:      {query_result.num_rows}")
    print(f"  find_facts_arrow() rows: {find_result.num_rows}")

    assert query_result.num_rows == find_result.num_rows, "Both functions should return same count"
    print("  ✓ find_facts_arrow() is correct alias\n")


def test_query_zero_copy():
    """Test 7: Zero-copy behavior (cache hits)"""
    print("=" * 60)
    print("Test 7: Zero-copy behavior")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Dog ⊑ᑦ Animal
    Dog（Fido）
    Dog（Rex）
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # First query - builds cache
    print("  First query (builds cache)...")
    start = time.perf_counter()
    result1 = reasoner.network.query({'type': 'instance_of'})
    time1 = time.perf_counter() - start

    # Second query - should use cache
    print("  Second query (uses cache)...")
    start = time.perf_counter()
    result2 = reasoner.network.query({'type': 'instance_of'})
    time2 = time.perf_counter() - start

    print(f"  First query:  {time1*1000:.3f}ms")
    print(f"  Second query: {time2*1000:.3f}ms")
    print(f"  Speedup:      {time1/time2:.1f}x")

    assert result1.num_rows == result2.num_rows, "Results should be consistent"
    assert time2 < time1, "Second query should be faster (cache hit)"
    print("  ✓ Zero-copy cache hits working\n")




def test_query_cache_invalidation():
    """Test 10: Cache invalidation scenarios"""
    print("=" * 60)
    print("Test 10: Cache invalidation")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Dog ⊑ᑦ Animal
    Dog（Fido）
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Initial query
    result1 = reasoner.network.query({'type': 'instance_of'})
    count1 = result1.num_rows
    print(f"  Initial query: {count1} facts")

    # Add new fact
    from reter.owl_rete_cpp import Fact
    reasoner.network.add_fact(Fact({
        'type': 'instance_of',
        'individual': 'Rex',
        'concept': 'Dog',
        'inferred': 'false'
    }))

    # Query again - should include new fact
    result2 = reasoner.network.query({'type': 'instance_of'})
    count2 = result2.num_rows
    print(f"  After add_fact: {count2} facts")

    assert count2 > count1, "Should have more facts after adding"

    # Verify Rex is present
    df = result2.to_pandas()
    assert 'Rex' in df['individual'].values, "Rex should be in results"
    print("  ✓ Cache invalidation works correctly\n")


def test_query_complex_pattern():
    """Test 11: Complex pattern with multiple columns"""
    print("=" * 60)
    print("Test 11: Complex pattern")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Dog ⊑ᑦ Animal
    Cat ⊑ᑦ Animal
    Dog（Fido）
    Dog（Rex）
    Cat（Whiskers）
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Query with very specific pattern
    result = reasoner.network.query({
        'type': 'instance_of',
        'concept': 'Dog',
        'individual': 'Fido'
    })

    df = result.to_pandas()
    print(f"  Matching facts: {result.num_rows}")

    assert result.num_rows >= 1, "Should find Fido"
    assert all(df['individual'] == 'Fido'), "Only Fido should match"
    assert all(df['concept'] == 'Dog'), "Only Dog concept should match"
    print("  ✓ Complex pattern works correctly\n")


def run_all_tests():
    """Run all tests in sequence"""
    print("\n" + "=" * 60)
    print("ARROW QUERY FUNCTIONS TEST SUITE")
    print("=" * 60 + "\n")

    tests = [
        test_query_empty_pattern,
        test_query_single_filter,
        test_query_multiple_filters,
        test_query_nonexistent_column,
        test_query_no_matches,
        test_find_facts_arrow_alias,
        test_query_zero_copy,
        test_query_correctness_vs_query,
        test_query_performance,
        test_query_cache_invalidation,
        test_query_complex_pattern,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"  ✗ FAILED: {e}\n")

    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed == 0:
        print("\n✅ ALL TESTS PASSED!")
    else:
        print(f"\n❌ {failed} test(s) failed")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
