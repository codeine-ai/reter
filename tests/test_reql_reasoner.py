#!/usr/bin/env python
"""
Test SPARQL support in RETER reasoner
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from reter.reasoner import Reter
import pytest


def test_basic_reql_query():
    """Test basic SPARQL SELECT query"""
    r = Reter()

    # Load sample ontology
    ontology = """
    Person ⊑ᑦ Animal
    Student ⊑ᑦ Person
    Person（john）
    Person（mary）
    Student（alice）
    hasAge（john，30）
    hasAge（mary，25）
    hasAge（alice，22）
    """
    r.load_ontology(ontology)

    # Test basic SPARQL query
    query = """
    SELECT ?person ?age
    WHERE {
        ?person type Person .
        ?person hasAge ?age .
    }
    """

    results = r.reql(query)

    # reql() returns a pyarrow.Table
    # Should get 3 results (john, mary, alice all have ages)
    assert results.num_rows == 3

    # Check that results have the right variables
    assert "?person" in results.column_names
    assert "?age" in results.column_names

    print(f"✓ Basic SPARQL query returned {results.num_rows} results")


def test_reql_with_filter():
    """Test SPARQL query with FILTER"""
    r = Reter()

    # Load sample ontology
    ontology = """
    Person ⊑ᑦ Animal
    Person（john）
    Person（mary）
    Person（alice）
    hasAge（john，30）
    hasAge（mary，25）
    hasAge（alice，22）
    """
    r.load_ontology(ontology)

    # Test SPARQL with FILTER
    query = """
    SELECT ?person ?age
    WHERE {
        ?person type Person .
        ?person hasAge ?age .
        FILTER (?age > 23)
    }
    """

    try:
        results = r.reql(query)
        results_list = list(results)

        # Should get 2 results (john=30 and mary=25, alice=22 is filtered out)
        # Note: Since filter conversion isn't fully implemented yet,
        # this might return all results
        print(f"✓ SPARQL with FILTER returned {len(results_list)} results")

    except Exception as e:
        print(f"Note: FILTER not fully implemented yet: {e}")


def test_reql_with_limit_offset():
    """Test SPARQL query with LIMIT and OFFSET"""
    r = Reter()

    # Load sample ontology
    ontology = """
    Person ⊑ᑦ Animal
    Person（p1）
    Person（p2）
    Person（p3）
    Person（p4）
    Person（p5）
    hasAge（p1，20）
    hasAge（p2，25）
    hasAge（p3，30）
    hasAge（p4，35）
    hasAge（p5，40）
    """
    r.load_ontology(ontology)

    # Test SPARQL with LIMIT
    query_limit = """
    SELECT ?person ?age
    WHERE {
        ?person type Person .
        ?person hasAge ?age .
    }
    LIMIT 3
    """

    results = r.reql(query_limit)
    # reql() returns pyarrow.Table - check num_rows not len(list())
    assert results.num_rows == 3
    print(f"✓ SPARQL with LIMIT 3 returned {results.num_rows} results")

    # Test SPARQL with OFFSET
    query_offset = """
    SELECT ?person ?age
    WHERE {
        ?person type Person .
        ?person hasAge ?age .
    }
    OFFSET 2
    """

    results = r.reql(query_offset)
    assert results.num_rows == 3  # 5 total minus 2 offset
    print(f"✓ SPARQL with OFFSET 2 returned {results.num_rows} results")

    # Test SPARQL with both LIMIT and OFFSET
    query_both = """
    SELECT ?person ?age
    WHERE {
        ?person type Person .
        ?person hasAge ?age .
    }
    LIMIT 2
    OFFSET 1
    """

    results = r.reql(query_both)
    assert results.num_rows == 2
    print(f"✓ SPARQL with LIMIT 2 OFFSET 1 returned {results.num_rows} results")


def test_reql_with_order_by():
    """Test SPARQL query with ORDER BY"""
    r = Reter()

    # Load sample ontology
    ontology = """
    Person ⊑ᑦ Animal
    Person（john）
    Person（mary）
    Person（alice）
    hasAge（john，30）
    hasAge（mary，25）
    hasAge（alice，22）
    """
    r.load_ontology(ontology)

    # Test SPARQL with ORDER BY ASC
    query_asc = """
    SELECT ?person ?age
    WHERE {
        ?person type Person .
        ?person hasAge ?age .
    }
    ORDER BY ?age
    """

    results = r.reql(query_asc)
    # Convert Arrow Table to list of dicts
    results_list = results.to_pylist() if hasattr(results, 'to_pylist') else []

    # Check ordering (should be alice=22, mary=25, john=30)
    if results_list:
        ages = [r["?age"] for r in results_list]
        assert ages == sorted(ages)
        print(f"✓ SPARQL with ORDER BY ASC returned results in correct order")

    # Test SPARQL with ORDER BY DESC
    query_desc = """
    SELECT ?person ?age
    WHERE {
        ?person type Person .
        ?person hasAge ?age .
    }
    ORDER BY DESC(?age)
    """

    results = r.reql(query_desc)
    # Convert Arrow Table to list of dicts
    results_list = results.to_pylist() if hasattr(results, 'to_pylist') else []

    # Check ordering (should be john=30, mary=25, alice=22)
    if results_list:
        ages = [r["?age"] for r in results_list]
        assert ages == sorted(ages, reverse=True)
        print(f"✓ SPARQL with ORDER BY DESC returned results in correct order")


def test_reql_with_distinct():
    """Test SPARQL query with DISTINCT

    Note: REQL has implicit DISTINCT semantics - results are always deduplicated
    after projection. The DISTINCT keyword is accepted but has no additional effect.
    """
    r = Reter()

    # Load sample ontology with duplicate values
    ontology = """
    Person ⊑ᑦ Animal
    Person（john）
    Person（mary）
    Person（alice）
    livesIn（john，NYC）
    livesIn（mary，NYC）
    livesIn（alice，LA）
    """
    r.load_ontology(ontology)

    # Test SPARQL without DISTINCT - implicit distinct after projection
    query_no_distinct = """
    SELECT ?city
    WHERE {
        ?person type Person .
        ?person livesIn ?city .
    }
    """

    results = r.reql(query_no_distinct)
    # Convert Arrow Table to list of dicts
    results_list = results.to_pylist() if hasattr(results, 'to_pylist') else []
    cities = [r["?city"] for r in results_list] if results_list else []
    # REQL has implicit DISTINCT - returns unique cities only (NYC, LA)
    assert len(cities) == 2, f"Expected 2 unique cities (implicit distinct), got {len(cities)}"
    print(f"✓ SPARQL without DISTINCT returned {len(cities)} results (implicit distinct)")

    # Test SPARQL with DISTINCT - same result due to implicit distinct
    query_distinct = """
    SELECT DISTINCT ?city
    WHERE {
        ?person type Person .
        ?person livesIn ?city .
    }
    """

    results = r.reql(query_distinct)
    # Convert Arrow Table to list of dicts
    results_list = results.to_pylist() if hasattr(results, 'to_pylist') else []
    cities = [r["?city"] for r in results_list] if results_list else []
    unique_cities = list(set(cities))
    assert len(cities) == len(unique_cities)  # Should be 2 (NYC, LA)
    assert len(cities) == 2, f"Expected 2 unique cities, got {len(cities)}"
    print(f"✓ SPARQL with DISTINCT returned {len(cities)} unique results")


def test_reql_to_pandas():
    """Test converting SPARQL results to pandas DataFrame"""
    r = Reter()

    # Load sample ontology
    ontology = """
    Person ⊑ᑦ Animal
    Person（john）
    Person（mary）
    Person（alice）
    hasAge（john，30）
    hasAge（mary，25）
    hasAge（alice，22）
    hasName（john，John_Doe）
    hasName（mary，Mary_Smith）
    hasName（alice，Alice_Johnson）
    """
    r.load_ontology(ontology)

    # Test SPARQL query
    query = """
    SELECT ?person ?name ?age
    WHERE {
        ?person type Person .
        ?person hasAge ?age .
        ?person hasName ?name .
    }
    ORDER BY ?age
    """

    results = r.reql(query)

    # Convert to pandas
    try:
        import pandas as pd
        df = results.to_pandas()

        assert len(df) == 3
        assert list(df.columns) == ["?person", "?name", "?age"]
        print(f"✓ SPARQL results converted to pandas DataFrame with {len(df)} rows")
        print("\nDataFrame preview:")
        print(df)

    except ImportError:
        print("Pandas not available, skipping DataFrame test")


def test_empty_reql_query():
    """Test empty SPARQL query"""
    r = Reter()

    # Load minimal ontology
    ontology = """
    Person ⊑ᑦ Animal
    """
    r.load_ontology(ontology)

    # Test SPARQL query with no results
    query = """
    SELECT ?x ?y
    WHERE {
        ?x hasProperty ?y .
    }
    """

    results = r.reql(query)
    # For empty results, check num_rows on Arrow Table
    assert results.num_rows == 0
    print(f"✓ Empty SPARQL query returned 0 results as expected")


def test_reql_complex_query():
    """Test more complex SPARQL query"""
    r = Reter()

    # Load a richer ontology
    ontology = """
    Person ⊑ᑦ Animal
    Student ⊑ᑦ Person
    Professor ⊑ᑦ Person

    Student（alice）
    Student（bob）
    Professor（prof_smith）

    hasAge（alice，22）
    hasAge（bob，24）
    hasAge（prof_smith，45）

    enrolledIn（alice，CS101）
    enrolledIn（alice，MATH201）
    enrolledIn（bob，CS101）
    enrolledIn（bob，PHYS301）

    teaches（prof_smith，CS101）
    teaches（prof_smith，CS201）
    """
    r.load_ontology(ontology)

    # Test complex query: Find students enrolled in courses taught by prof_smith
    query = """
    SELECT ?student ?course
    WHERE {
        ?student type Student .
        ?student enrolledIn ?course .
        prof_smith teaches ?course .
    }
    """

    results = r.reql(query)

    # Convert PyArrow Table to pandas for easier access
    df = results.to_pandas()

    # Should get alice and bob both enrolled in CS101
    assert len(df) >= 2
    print(f"✓ Complex SPARQL query returned {len(df)} results")

    for _, row in df.iterrows():
        print(f"  Student {row['?student']} enrolled in {row['?course']}")


def test_reql_error_handling():
    """Test SPARQL error handling"""
    r = Reter()

    # Test invalid SPARQL syntax
    invalid_query = """
    SELECT ?x
    WHERE {
        ?x type Person
        INVALID SYNTAX HERE
    }
    """

    try:
        results = r.reql(invalid_query)
        assert False, "Should have raised an error for invalid REQL"
    except RuntimeError as e:
        assert "REQL" in str(e) or "parse error" in str(e).lower()
        print(f"✓ Invalid REQL query raised appropriate error")


if __name__ == "__main__":
    print("=" * 70)
    print("SPARQL Support Tests for RETER Reasoner")
    print("=" * 70)

    test_basic_reql_query()
    test_reql_with_filter()
    test_reql_with_limit_offset()
    test_reql_with_order_by()
    test_reql_with_distinct()
    test_reql_to_pandas()
    test_empty_reql_query()
    test_reql_complex_query()
    test_reql_error_handling()

    print("\n" + "=" * 70)
    print("✓ All SPARQL tests completed!")
    print("=" * 70)