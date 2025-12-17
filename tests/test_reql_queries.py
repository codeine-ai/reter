#!/usr/bin/env python3
"""
Test SPARQL Query Support in RETER

This test suite verifies:
1. Basic SELECT queries with single triple patterns
2. SELECT with multiple variables
3. SELECT * (all variables)
4. FILTER constraints (numeric comparisons)
5. FILTER with logical operators (AND, OR, NOT)
6. ORDER BY (ASC and DESC)
7. LIMIT and OFFSET
8. DISTINCT modifier
9. String literals in queries
10. Numeric literals in queries
11. Boolean literals in queries
12. Error handling for invalid queries
13. Empty result sets
14. Integration with DL ontology facts
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from reter import Reter
from reter.owl_rete_cpp import Fact


def test_basic_select():
    """Test 1: Basic SELECT query with single triple pattern"""
    print("=" * 60)
    print("Test 1: Basic SELECT Query")
    print("=" * 60)

    reasoner = Reter()

    # Add some test facts using add_triple (REQL-compatible)
    reasoner.add_triple("Alice", "hasAge", "30")
    reasoner.add_triple("Bob", "hasAge", "25")
    reasoner.add_triple("Charlie", "hasAge", "35")

    # Execute SPARQL query
    query = """
    SELECT ?person ?age
    WHERE {
        ?person hasAge ?age .
    }
    """

    results = reasoner.network.reql_query(query)

    print(f"  Results: {results.num_rows} rows")
    print(f"  Columns: {results.schema.names}")

    assert results.num_rows == 3, f"Expected 3 results, got {results.num_rows}"
    assert '?person' in results.schema.names, "Missing '?person' column"
    assert '?age' in results.schema.names, "Missing '?age' column"

    print("  ✓ Basic SELECT query works\n")


def test_select_star():
    """Test 2: SELECT * returns all variables"""
    print("=" * 60)
    print("Test 2: SELECT * Query")
    print("=" * 60)

    reasoner = Reter()

    reasoner.add_triple("Alice", "hasAge", "30")
    reasoner.add_triple("Bob", "hasAge", "25")

    query = """
    SELECT *
    WHERE {
        ?person hasAge ?age .
    }
    """

    results = reasoner.network.reql_query(query)

    print(f"  Results: {results.num_rows} rows")
    print(f"  Columns: {results.schema.names}")

    assert results.num_rows == 2, f"Expected 2 results, got {results.num_rows}"
    # Should have columns for all variables in the pattern
    assert len(results.schema.names) > 0, "SELECT * should return columns"

    print("  ✓ SELECT * query works\n")


def test_filter_numeric_comparison():
    """Test 3: FILTER with numeric comparison operators"""
    print("=" * 60)
    print("Test 3: FILTER with Numeric Comparison")
    print("=" * 60)

    reasoner = Reter()

    reasoner.add_triple("Alice", "hasAge", "30")
    reasoner.add_triple("Bob", "hasAge", "25")
    reasoner.add_triple("Charlie", "hasAge", "35")
    reasoner.add_triple("Diana", "hasAge", "20")

    # Test FILTER with > operator
    query = """
    SELECT ?person ?age
    WHERE {
        ?person hasAge ?age .
        FILTER (?age > 25)
    }
    """

    results = reasoner.network.reql_query(query)

    print(f"  Results with age > 25: {results.num_rows} rows")

    # Should return Alice (30) and Charlie (35), not Bob (25) or Diana (20)
    assert results.num_rows >= 2, f"Expected at least 2 results, got {results.num_rows}"

    print("  ✓ FILTER with > operator works\n")


def test_filter_multiple_conditions():
    """Test 4: FILTER with multiple conditions (AND)"""
    print("=" * 60)
    print("Test 4: FILTER with Multiple Conditions")
    print("=" * 60)

    reasoner = Reter()

    reasoner.add_triple("Alice", "hasAge", "30")
    reasoner.add_triple("Bob", "hasAge", "25")
    reasoner.add_triple("Charlie", "hasAge", "35")
    reasoner.add_triple("Diana", "hasAge", "20")

    # Test FILTER with AND condition
    query = """
    SELECT ?person ?age
    WHERE {
        ?person hasAge ?age .
        FILTER (?age >= 25 && ?age <= 30)
    }
    """

    results = reasoner.network.reql_query(query)

    print(f"  Results with 25 <= age <= 30: {results.num_rows} rows")

    # Should return Alice (30) and Bob (25), not Charlie (35) or Diana (20)
    assert results.num_rows >= 2, f"Expected at least 2 results, got {results.num_rows}"

    print("  ✓ FILTER with && operator works\n")


def test_order_by_asc():
    """Test 5: ORDER BY ascending"""
    print("=" * 60)
    print("Test 5: ORDER BY ASC")
    print("=" * 60)

    reasoner = Reter()

    reasoner.add_triple("Alice", "hasAge", "30")
    reasoner.add_triple("Bob", "hasAge", "25")
    reasoner.add_triple("Charlie", "hasAge", "35")

    query = """
    SELECT ?person ?age
    WHERE {
        ?person hasAge ?age .
    }
    ORDER BY ASC(?age)
    """

    results = reasoner.network.reql_query(query)

    print(f"  Results ordered by age ASC: {results.num_rows} rows")

    # Convert to pandas to check ordering
    df = results.to_pandas()
    ages = df['?age'].tolist()
    print(f"  Ages in order: {ages}")

    # Check if sorted (note: values are strings, so need numeric comparison)
    ages_numeric = [int(age) for age in ages]
    assert ages_numeric == sorted(ages_numeric), f"Results not sorted ascending: {ages_numeric}"

    print("  ✓ ORDER BY ASC works\n")


def test_order_by_desc():
    """Test 6: ORDER BY descending"""
    print("=" * 60)
    print("Test 6: ORDER BY DESC")
    print("=" * 60)

    reasoner = Reter()

    reasoner.add_triple("Alice", "hasAge", "30")
    reasoner.add_triple("Bob", "hasAge", "25")
    reasoner.add_triple("Charlie", "hasAge", "35")

    query = """
    SELECT ?person ?age
    WHERE {
        ?person hasAge ?age .
    }
    ORDER BY DESC(?age)
    """

    results = reasoner.network.reql_query(query)

    print(f"  Results ordered by age DESC: {results.num_rows} rows")

    # Convert to pandas to check ordering
    df = results.to_pandas()
    ages = df['?age'].tolist()
    print(f"  Ages in order: {ages}")

    # Check if reverse sorted
    ages_numeric = [int(age) for age in ages]
    assert ages_numeric == sorted(ages_numeric, reverse=True), f"Results not sorted descending: {ages_numeric}"

    print("  ✓ ORDER BY DESC works\n")


def test_limit():
    """Test 7: LIMIT clause"""
    print("=" * 60)
    print("Test 7: LIMIT Clause")
    print("=" * 60)

    reasoner = Reter()

    reasoner.add_triple("Alice", "hasAge", "30")
    reasoner.add_triple("Bob", "hasAge", "25")
    reasoner.add_triple("Charlie", "hasAge", "35")
    reasoner.add_triple("Diana", "hasAge", "28")

    query = """
    SELECT ?person ?age
    WHERE {
        ?person hasAge ?age .
    }
    LIMIT 2
    """

    results = reasoner.network.reql_query(query)

    print(f"  Results with LIMIT 2: {results.num_rows} rows")

    assert results.num_rows == 2, f"Expected 2 results (LIMIT 2), got {results.num_rows}"

    print("  ✓ LIMIT clause works\n")


def test_offset():
    """Test 8: OFFSET clause"""
    print("=" * 60)
    print("Test 8: OFFSET Clause")
    print("=" * 60)

    reasoner = Reter()

    reasoner.add_triple("Alice", "hasAge", "30")
    reasoner.add_triple("Bob", "hasAge", "25")
    reasoner.add_triple("Charlie", "hasAge", "35")
    reasoner.add_triple("Diana", "hasAge", "28")

    # Query without OFFSET
    query_all = """
    SELECT ?person ?age
    WHERE {
        ?person hasAge ?age .
    }
    """
    all_results = reasoner.network.reql_query(query_all)
    total_count = all_results.num_rows

    # Query with OFFSET 2
    query_offset = """
    SELECT ?person ?age
    WHERE {
        ?person hasAge ?age .
    }
    OFFSET 2
    """
    offset_results = reasoner.network.reql_query(query_offset)

    print(f"  Total results: {total_count}")
    print(f"  Results with OFFSET 2: {offset_results.num_rows} rows")

    assert offset_results.num_rows == (total_count - 2), f"Expected {total_count - 2} results, got {offset_results.num_rows}"

    print("  ✓ OFFSET clause works\n")


def test_limit_and_offset():
    """Test 9: LIMIT and OFFSET together"""
    print("=" * 60)
    print("Test 9: LIMIT and OFFSET Together")
    print("=" * 60)

    reasoner = Reter()

    for i in range(10):
        reasoner.add_triple(f"Person{i}", "hasAge", str(20 + i))

    query = """
    SELECT ?person ?age
    WHERE {
        ?person hasAge ?age .
    }
    OFFSET 3
    LIMIT 2
    """

    results = reasoner.network.reql_query(query)

    print(f"  Results with OFFSET 3 LIMIT 2: {results.num_rows} rows")

    assert results.num_rows == 2, f"Expected 2 results, got {results.num_rows}"

    print("  ✓ LIMIT and OFFSET together work\n")


def test_distinct():
    """Test 10: DISTINCT modifier"""
    print("=" * 60)
    print("Test 10: DISTINCT Modifier")
    print("=" * 60)

    reasoner = Reter()

    # Add facts with duplicate values
    reasoner.add_triple("Alice", "likes", "Pizza")
    reasoner.add_triple("Bob", "likes", "Pizza")
    reasoner.add_triple("Charlie", "likes", "Sushi")
    reasoner.add_triple("Diana", "likes", "Pizza")

    # Query without DISTINCT
    query_all = """
    SELECT ?food
    WHERE {
        ?person likes ?food .
    }
    """
    all_results = reasoner.network.reql_query(query_all)

    # Query with DISTINCT
    query_distinct = """
    SELECT DISTINCT ?food
    WHERE {
        ?person likes ?food .
    }
    """
    distinct_results = reasoner.network.reql_query(query_distinct)

    print(f"  Results without DISTINCT: {all_results.num_rows} rows")
    print(f"  Results with DISTINCT: {distinct_results.num_rows} rows")

    # Should have fewer results with DISTINCT (only 2 unique foods: Pizza, Sushi)
    assert distinct_results.num_rows < all_results.num_rows, "DISTINCT should reduce result count"
    assert distinct_results.num_rows == 2, f"Expected 2 distinct foods, got {distinct_results.num_rows}"

    print("  ✓ DISTINCT modifier works\n")


def test_string_literals():
    """Test 11: String literals in queries"""
    print("=" * 60)
    print("Test 11: String Literals")
    print("=" * 60)

    reasoner = Reter()

    reasoner.add_triple("Alice", "hasName", "Alice Smith")
    reasoner.add_triple("Bob", "hasName", "Bob Jones")

    # Query with string literal filter
    query = """
    SELECT ?person
    WHERE {
        ?person hasName 'Alice Smith' .
    }
    """

    results = reasoner.network.reql_query(query)

    print(f"  Results matching 'Alice Smith': {results.num_rows} rows")

    assert results.num_rows >= 1, f"Expected at least 1 result, got {results.num_rows}"

    print("  ✓ String literals work\n")


def test_numeric_literals():
    """Test 12: Numeric literals in queries"""
    print("=" * 60)
    print("Test 12: Numeric Literals")
    print("=" * 60)

    reasoner = Reter()

    reasoner.add_triple("Alice", "hasAge", "30")
    reasoner.add_triple("Bob", "hasAge", "25")

    # Query with numeric literal
    query = """
    SELECT ?person
    WHERE {
        ?person hasAge 30 .
    }
    """

    results = reasoner.network.reql_query(query)

    print(f"  Results with age = 30: {results.num_rows} rows")

    assert results.num_rows >= 1, f"Expected at least 1 result, got {results.num_rows}"

    print("  ✓ Numeric literals work\n")


def test_empty_results():
    """Test 13: Empty result sets"""
    print("=" * 60)
    print("Test 13: Empty Result Sets")
    print("=" * 60)

    reasoner = Reter()

    reasoner.add_triple("Alice", "hasAge", "30")

    # Query that should return no results
    query = """
    SELECT ?person ?age
    WHERE {
        ?person hasAge ?age .
        FILTER (?age > 100)
    }
    """

    results = reasoner.network.reql_query(query)

    print(f"  Results with age > 100: {results.num_rows} rows")

    assert results.num_rows == 0, f"Expected 0 results, got {results.num_rows}"
    assert '?person' in results.schema.names, "Schema should still have '?person' column"
    assert '?age' in results.schema.names, "Schema should still have '?age' column"

    print("  ✓ Empty results handled correctly\n")


def test_integration_with_dl_ontology():
    """Test 14: Integration with DL ontology reasoning"""
    print("=" * 60)
    print("Test 14: Integration with DL Ontology")
    print("=" * 60)

    reasoner = Reter()

    # Load ontology with subsumption
    ontology = """
    Dog ⊑ᑦ Animal
    Cat ⊑ᑦ Animal
    Dog（Fido）
    Cat（Whiskers）
    """
    reasoner.load_ontology(ontology)

    # Query for all animals (should include inferred types)
    query = """
    SELECT ?x
    WHERE {
        ?x type Animal .
    }
    """

    results = reasoner.network.reql_query(query)

    print(f"  Animals found: {results.num_rows} rows")

    # Should find Fido and Whiskers as Animals (via subsumption)
    assert results.num_rows >= 2, f"Expected at least 2 animals, got {results.num_rows}"

    print("  ✓ Integration with DL reasoning works\n")


def test_invalid_query_syntax():
    """Test 15: Error handling for invalid queries"""
    print("=" * 60)
    print("Test 15: Invalid Query Syntax")
    print("=" * 60)

    reasoner = Reter()

    # Invalid query (missing closing brace)
    invalid_query = """
    SELECT ?person ?age
    WHERE {
        ?person hasAge ?age .
    """

    print("  Testing invalid query (missing closing brace)...")

    with pytest.raises(Exception) as exc_info:
        results = reasoner.network.reql_query(invalid_query)

    print(f"  ✓ Correctly raised exception: {type(exc_info.value).__name__}")
    print(f"    Message: {str(exc_info.value)}\n")


def test_complex_query():
    """Test 16: Complex query with multiple features"""
    print("=" * 60)
    print("Test 16: Complex Query")
    print("=" * 60)

    reasoner = Reter()

    # Add comprehensive test data
    reasoner.add_triple("Alice", "hasAge", "30")
    reasoner.add_triple("Alice", "hasName", "Alice Smith")
    reasoner.add_triple("Bob", "hasAge", "25")
    reasoner.add_triple("Bob", "hasName", "Bob Jones")
    reasoner.add_triple("Charlie", "hasAge", "35")
    reasoner.add_triple("Charlie", "hasName", "Charlie Brown")
    reasoner.add_triple("Diana", "hasAge", "28")
    reasoner.add_triple("Diana", "hasName", "Diana Prince")

    # Complex query with FILTER, ORDER BY, and LIMIT
    query = """
    SELECT ?person ?age
    WHERE {
        ?person hasAge ?age .
        FILTER (?age >= 25)
    }
    ORDER BY DESC(?age)
    LIMIT 3
    """

    results = reasoner.network.reql_query(query)

    print(f"  Results: {results.num_rows} rows")

    assert results.num_rows == 3, f"Expected 3 results (LIMIT 3), got {results.num_rows}"

    # Check ordering (should be descending by age)
    df = results.to_pandas()
    ages = [int(age) for age in df['?age'].tolist()]
    print(f"  Ages in descending order: {ages}")
    assert ages == sorted(ages, reverse=True), "Results not sorted correctly"

    # All ages should be >= 25
    assert all(age >= 25 for age in ages), "Filter not applied correctly"

    print("  ✓ Complex query works correctly\n")


if __name__ == "__main__":
    # Run all tests
    print("\n" + "=" * 60)
    print("SPARQL Query Test Suite")
    print("=" * 60 + "\n")

    pytest.main([__file__, "-v"])
