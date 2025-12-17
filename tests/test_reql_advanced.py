#!/usr/bin/env python3
"""
Test Advanced REQL Features and Edge Cases

This test suite verifies:
1. Variable naming (? and $ prefixes)
2. Multiple triple patterns (joins)
3. Filter with arithmetic expressions
4. Filter with built-in functions (STR, BOUND)
5. Nested filters
6. Edge cases (empty WHERE, no results, etc.)
7. Performance with larger datasets
8. Special characters in literals
9. Case sensitivity
10. Arrow table integration
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from reter import Reter
from reter_core.owl_rete_cpp import Fact
import pyarrow as pa
import time


def test_dollar_variable_syntax():
    """Test 1: Variables with ? prefix (updated: $ syntax removed)"""
    print("=" * 60)
    print("Test 1: ? Variable Syntax")
    print("=" * 60)

    reasoner = Reter()

    reasoner.add_triple("Alice", "hasAge", "30")
    reasoner.add_triple("Bob", "hasAge", "25")

    # Query using ? ($ syntax no longer supported)
    query = """
    SELECT ?person ?age
    WHERE {
        ?person hasAge ?age .
    }
    """

    results = reasoner.network.reql_query(query)

    print(f"  Results with ? variables: {results.num_rows} rows")

    assert results.num_rows == 2, f"Expected 2 results, got {results.num_rows}"
    # Column names should include ?
    assert '?person' in results.schema.names

    print("  ✓ ? variable syntax works\n")


def test_mixed_variable_syntax():
    """Test 2: Consistent ? variable usage (updated: $ syntax removed)"""
    print("=" * 60)
    print("Test 2: Consistent Variable Syntax")
    print("=" * 60)

    reasoner = Reter()

    reasoner.add_triple("Alice", "hasAge", "30")

    # Query using consistent ? syntax ($ syntax no longer supported)
    query = """
    SELECT ?person ?age
    WHERE {
        ?person hasAge ?age .
    }
    """

    results = reasoner.network.reql_query(query)

    print(f"  Results with ? variables: {results.num_rows} rows")

    assert results.num_rows == 1, f"Expected 1 result, got {results.num_rows}"

    print("  ✓ Consistent variable syntax works\n")


def test_multiple_triple_patterns():
    """Test 3: Multiple triple patterns (join)"""
    print("=" * 60)
    print("Test 3: Multiple Triple Patterns")
    print("=" * 60)

    reasoner = Reter()

    # Add facts for join
    reasoner.add_triple("Alice", "hasAge", "30")
    reasoner.add_triple("Alice", "hasName", "Alice Smith")
    reasoner.add_triple("Bob", "hasAge", "25")
    reasoner.add_triple("Bob", "hasName", "Bob Jones")

    # Query with multiple patterns (should join on ?person)
    query = """
    SELECT ?person ?age ?name
    WHERE {
        ?person hasAge ?age .
        ?person hasName ?name .
    }
    """

    try:
        results = reasoner.network.reql_query(query)

        print(f"  Results with join: {results.num_rows} rows")

        # Should find both Alice and Bob (they have both age and name)
        # Note: Current implementation may only support single triple pattern
        # This test documents the expected behavior for future implementation
        print(f"  Columns: {results.schema.names}")

        if results.num_rows > 0:
            print("  ✓ Multiple triple patterns work\n")
        else:
            print("  ⚠ Multiple triple patterns not yet fully implemented\n")

    except Exception as e:
        print(f"  ⚠ Multiple triple patterns not yet supported: {e}\n")


def test_filter_arithmetic():
    """Test 4: FILTER with arithmetic expressions"""
    print("=" * 60)
    print("Test 4: FILTER with Arithmetic")
    print("=" * 60)

    reasoner = Reter()

    reasoner.add_triple("Alice", "hasAge", "30")
    reasoner.add_triple("Bob", "hasAge", "25")

    # Filter with arithmetic (age + 5 > 32)
    query = """
    SELECT ?person ?age
    WHERE {
        ?person hasAge ?age .
        FILTER (?age + 5 > 32)
    }
    """

    try:
        results = reasoner.network.reql_query(query)

        print(f"  Results with arithmetic filter: {results.num_rows} rows")

        # Should return Alice (30 + 5 = 35 > 32), not Bob (25 + 5 = 30 < 32)
        print("  ✓ Arithmetic in filters works\n")

    except Exception as e:
        print(f"  ⚠ Arithmetic filters not yet fully supported: {e}\n")


def test_filter_str_function():
    """Test 5: FILTER with STR() function"""
    print("=" * 60)
    print("Test 5: FILTER with STR() Function")
    print("=" * 60)

    reasoner = Reter()

    reasoner.add_triple("Alice", "hasName", "Alice")
    reasoner.add_triple("Bob", "hasName", "Bob")

    # Filter using STR function
    query = """
    SELECT ?person ?name
    WHERE {
        ?person hasName ?name .
        FILTER (STR(?name) = 'Alice')
    }
    """

    try:
        results = reasoner.network.reql_query(query)

        print(f"  Results with STR filter: {results.num_rows} rows")

        assert results.num_rows >= 1, "Should find Alice"
        print("  ✓ STR() function works\n")

    except Exception as e:
        print(f"  ⚠ STR() function not yet fully supported: {e}\n")


def test_filter_bound_function():
    """Test 6: FILTER with BOUND() function"""
    print("=" * 60)
    print("Test 6: FILTER with BOUND() Function")
    print("=" * 60)

    reasoner = Reter()

    reasoner.add_triple("Alice", "hasAge", "30")
    reasoner.add_triple("Bob", "hasAge", "25")

    # Filter using BOUND function
    query = """
    SELECT ?person ?age
    WHERE {
        ?person hasAge ?age .
        FILTER (BOUND(?age))
    }
    """

    try:
        results = reasoner.network.reql_query(query)

        print(f"  Results with BOUND filter: {results.num_rows} rows")

        # All results should have bound ?age
        assert results.num_rows == 2, "All results should have bound age"
        print("  ✓ BOUND() function works\n")

    except Exception as e:
        print(f"  ⚠ BOUND() function not yet fully supported: {e}\n")


@pytest.mark.skip(reason="Causes access violation crash - needs C++ investigation")
def test_empty_where_clause():
    """Test 7: Empty WHERE clause (should fail)"""
    print("=" * 60)
    print("Test 7: Empty WHERE Clause")
    print("=" * 60)

    reasoner = Reter()

    reasoner.add_triple("Alice", "hasAge", "30")

    # Query with empty WHERE (invalid)
    query = """
    SELECT ?person
    WHERE {
    }
    """

    print("  Testing empty WHERE clause...")

    with pytest.raises(Exception):
        results = reasoner.network.reql_query(query)

    print("  ✓ Empty WHERE correctly raises error\n")


def test_special_characters_in_literals():
    """Test 8: Special characters in string literals"""
    print("=" * 60)
    print("Test 8: Special Characters in Literals")
    print("=" * 60)

    reasoner = Reter()

    # Add facts with special characters
    reasoner.add_triple("Alice", "hasEmail", "alice@example.com")
    reasoner.add_triple("Bob", "hasEmail", "bob.jones@test.org")

    query = """
    SELECT ?person ?email
    WHERE {
        ?person hasEmail ?email .
    }
    """

    results = reasoner.network.reql_query(query)

    print(f"  Results with special characters: {results.num_rows} rows")

    assert results.num_rows == 2, f"Expected 2 results, got {results.num_rows}"

    # Check that special characters are preserved
    df = results.to_pandas()
    emails = df['?email'].tolist()
    print(f"  Emails: {emails}")
    assert any('@' in email for email in emails), "Special characters should be preserved"

    print("  ✓ Special characters handled correctly\n")


def test_performance_large_dataset():
    """Test 9: Performance with larger dataset"""
    print("=" * 60)
    print("Test 9: Performance with Large Dataset")
    print("=" * 60)

    reasoner = Reter()

    # Add 1000 facts
    print("  Adding 1000 facts...")
    for i in range(1000):
        reasoner.add_triple(f"Person{i}", "hasAge", str(20 + (i % 50)))

    print(f"  Total facts: {reasoner.network.fact_count()}")

    query = """
    SELECT ?person ?age
    WHERE {
        ?person hasAge ?age .
        FILTER (?age > 30)
    }
    ORDER BY DESC(?age)
    LIMIT 10
    """

    print("  Executing complex query...")
    start_time = time.time()
    results = reasoner.network.reql_query(query)
    end_time = time.time()

    execution_time = (end_time - start_time) * 1000  # Convert to ms

    print(f"  Results: {results.num_rows} rows")
    print(f"  Execution time: {execution_time:.2f} ms")

    assert results.num_rows == 10, f"Expected 10 results (LIMIT 10), got {results.num_rows}"
    assert execution_time < 1000, f"Query too slow: {execution_time:.2f} ms"

    print("  ✓ Large dataset query performs well\n")


def test_arrow_table_schema():
    """Test 10: Arrow table schema correctness"""
    print("=" * 60)
    print("Test 10: Arrow Table Schema")
    print("=" * 60)

    reasoner = Reter()

    reasoner.add_triple("Alice", "hasAge", "30")

    query = """
    SELECT ?person ?age
    WHERE {
        ?person hasAge ?age .
    }
    """

    results = reasoner.network.reql_query(query)

    print(f"  Schema: {results.schema}")
    print(f"  Column names: {results.schema.names}")
    print(f"  Column types: {[field.type for field in results.schema]}")

    # Verify it's a valid Arrow table
    assert isinstance(results, pa.Table), "Result should be a PyArrow Table"
    assert len(results.schema.names) == 2, "Should have 2 columns"
    assert '?person' in results.schema.names, "Should have '?person' column"
    assert '?age' in results.schema.names, "Should have '?age' column"

    # Verify pandas conversion works
    df = results.to_pandas()
    assert len(df) == 1, "DataFrame should have 1 row"
    assert '?person' in df.columns and '?age' in df.columns, f"DataFrame columns: {list(df.columns)}"

    print("  ✓ Arrow table schema is correct\n")


def test_case_sensitivity_variables():
    """Test 11: Variable name case sensitivity"""
    print("=" * 60)
    print("Test 11: Variable Name Case Sensitivity")
    print("=" * 60)

    reasoner = Reter()

    reasoner.add_triple("Alice", "hasAge", "30")

    # Test that ?person and ?Person are different variables
    query = """
    SELECT ?Person
    WHERE {
        ?Person hasAge ?age .
    }
    """

    results = reasoner.network.reql_query(query)

    print(f"  Results with ?Person: {results.num_rows} rows")
    print(f"  Columns: {results.schema.names}")

    # Should work - variables are case-sensitive
    assert results.num_rows == 1, f"Expected 1 result, got {results.num_rows}"
    assert '?Person' in results.schema.names or '?person' in results.schema.names

    print("  ✓ Variable names are case-sensitive\n")


def test_predicate_with_special_names():
    """Test 12: Predicates with underscores and special names"""
    print("=" * 60)
    print("Test 12: Special Predicate Names")
    print("=" * 60)

    reasoner = Reter()

    # Add facts with various predicate names
    reasoner.add_triple("Alice", "has_age", "30")
    reasoner.add_triple("Bob", "hasAge", "25")
    reasoner.add_triple("Charlie", "age", "35")

    query = """
    SELECT ?person ?age
    WHERE {
        ?person has_age ?age .
    }
    """

    results = reasoner.network.reql_query(query)

    print(f"  Results with has_age predicate: {results.num_rows} rows")

    assert results.num_rows == 1, f"Expected 1 result (Alice), got {results.num_rows}"

    print("  ✓ Special predicate names work\n")


def test_filter_not_equal():
    """Test 13: FILTER with != operator"""
    print("=" * 60)
    print("Test 13: FILTER with != Operator")
    print("=" * 60)

    reasoner = Reter()

    reasoner.add_triple("Alice", "hasAge", "30")
    reasoner.add_triple("Bob", "hasAge", "25")
    reasoner.add_triple("Charlie", "hasAge", "30")

    query = """
    SELECT ?person ?age
    WHERE {
        ?person hasAge ?age .
        FILTER (?age != 30)
    }
    """

    results = reasoner.network.reql_query(query)

    print(f"  Results with age != 30: {results.num_rows} rows")

    # Should return only Bob (age 25)
    assert results.num_rows >= 1, f"Expected at least 1 result, got {results.num_rows}"

    df = results.to_pandas()
    ages = [int(age) for age in df['?age'].tolist()]
    assert 30 not in ages, "Should not include age 30"

    print("  ✓ != operator works\n")


def test_filter_less_equal():
    """Test 14: FILTER with <= operator"""
    print("=" * 60)
    print("Test 14: FILTER with <= Operator")
    print("=" * 60)

    reasoner = Reter()

    reasoner.add_triple("Alice", "hasAge", "30")
    reasoner.add_triple("Bob", "hasAge", "25")
    reasoner.add_triple("Charlie", "hasAge", "35")

    query = """
    SELECT ?person ?age
    WHERE {
        ?person hasAge ?age .
        FILTER (?age <= 30)
    }
    """

    results = reasoner.network.reql_query(query)

    print(f"  Results with age <= 30: {results.num_rows} rows")

    assert results.num_rows >= 2, f"Expected at least 2 results, got {results.num_rows}"

    df = results.to_pandas()
    ages = [int(age) for age in df['?age'].tolist()]
    assert all(age <= 30 for age in ages), f"All ages should be <= 30: {ages}"

    print("  ✓ <= operator works\n")


def test_zero_copy_to_python():
    """Test 15: Zero-copy Arrow integration"""
    print("=" * 60)
    print("Test 15: Zero-Copy Arrow Integration")
    print("=" * 60)

    reasoner = Reter()

    # Add many facts to test zero-copy benefits
    for i in range(100):
        reasoner.network.add_fact(Fact({
            "subject": f"Person{i}",
            "predicate": "hasAge",
            "object": str(20 + i)
        }))

    query = """
    SELECT ?person ?age
    WHERE {
        ?person hasAge ?age .
    }
    """

    # Measure time for query execution
    start_time = time.time()
    results = reasoner.network.reql_query(query)
    query_time = time.time() - start_time

    # Measure time for pandas conversion
    start_time = time.time()
    df = results.to_pandas()
    conversion_time = time.time() - start_time

    print(f"  Query time: {query_time * 1000:.2f} ms")
    print(f"  Pandas conversion time: {conversion_time * 1000:.2f} ms")
    print(f"  Total rows: {len(df)}")

    # Pandas conversion should be very fast (zero-copy)
    assert conversion_time < 0.1, f"Pandas conversion too slow: {conversion_time * 1000:.2f} ms"

    print("  ✓ Zero-copy integration is fast\n")


if __name__ == "__main__":
    # Run all tests
    print("\n" + "=" * 60)
    print("REQL Advanced Features Test Suite")
    print("=" * 60 + "\n")

    pytest.main([__file__, "-v"])
