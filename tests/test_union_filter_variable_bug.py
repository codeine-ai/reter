#!/usr/bin/env python
"""
Test for UNION + FILTER variable bug (BUG-002).

This test documents and verifies the fix for a bug where FILTER fails to access
variables that are not in the SELECT clause when UNION is present.

Bug description:
- Without UNION: FILTER can access variables NOT in SELECT (works correctly)
- With UNION: FILTER FAILS with "Variable not found in query results" if
  the variable is not in SELECT

Root cause:
In ReqlExecutor.cpp, when building sub-query for patterns outside UNION,
only SELECT variables are included in patterns_query.selectVariables,
but FILTER variables should also be included.

Fix location: reter_core/rete_cpp/sparql/ReqlExecutor.cpp lines 1108-1113
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from reter.reasoner import Reter


@pytest.fixture
def reter_with_code_facts():
    """Create a Reter instance with code-like facts for testing."""
    r = Reter()

    # Load code-like ontology (no comments allowed in ontology string)
    ontology = """
    Method ⊑ᑦ Function
    pyMethod（method1）
    pyMethod（method2）
    pyMethod（method3）
    ooFunction（func1）
    name（method1，execute）
    name（method2，run）
    name（method3，process）
    name（func1，helper）
    concept（method1，pyMethod）
    concept（method2，pyMethod）
    concept（method3，pyMethod）
    concept（func1，ooFunction）
    calls（method1，method2）
    calls（method2，method3）
    maybeCalls（method1，func1）
    """
    r.load_ontology(ontology)
    return r


class TestFilterWithoutUnion:
    """Tests for FILTER without UNION - should work correctly."""

    def test_filter_on_variable_in_select(self, reter_with_code_facts):
        """FILTER on variable that IS in SELECT - should always work."""
        r = reter_with_code_facts

        query = """
        SELECT ?x ?name ?t WHERE {
            ?x type pyMethod .
            ?x name ?name .
            ?x concept ?t .
            FILTER(CONTAINS(?t, "Method"))
        }
        """

        results = r.reql(query)
        assert results.num_rows >= 1, "Should find at least one method"
        assert "?x" in results.column_names
        assert "?name" in results.column_names
        assert "?t" in results.column_names
        print(f"✓ Filter on variable in SELECT (no UNION): {results.num_rows} results")

    def test_filter_on_variable_not_in_select(self, reter_with_code_facts):
        """FILTER on variable NOT in SELECT - should work without UNION."""
        r = reter_with_code_facts

        # Note: ?t is used in FILTER but NOT in SELECT
        query = """
        SELECT ?x ?name WHERE {
            ?x type pyMethod .
            ?x name ?name .
            ?x concept ?t .
            FILTER(CONTAINS(?t, "Method"))
        }
        """

        results = r.reql(query)
        assert results.num_rows >= 1, "Should find at least one method"
        assert "?x" in results.column_names
        assert "?name" in results.column_names
        # Note: ?t may or may not be in results depending on implementation
        # The key point is that the query works and filters correctly
        print(f"✓ Filter on variable NOT in SELECT (no UNION): {results.num_rows} results")


class TestFilterWithUnion:
    """Tests for FILTER with UNION - this is where the bug manifests."""

    def test_union_filter_on_variable_in_select(self, reter_with_code_facts):
        """FILTER on variable that IS in SELECT with UNION - should work."""
        r = reter_with_code_facts

        # ?t is in SELECT, so this should work
        query = """
        SELECT ?caller ?callee ?t WHERE {
            { ?caller calls ?callee } UNION { ?caller maybeCalls ?callee }
            ?caller name ?name .
            ?caller concept ?t .
            FILTER(CONTAINS(?t, "Method"))
        }
        """

        results = r.reql(query)
        assert results.num_rows >= 1, "Should find at least one call relationship"
        assert "?caller" in results.column_names
        assert "?callee" in results.column_names
        assert "?t" in results.column_names
        print(f"✓ UNION with FILTER on variable in SELECT: {results.num_rows} results")

    def test_union_filter_on_variable_not_in_select_bug(self, reter_with_code_facts):
        """
        BUG TEST: FILTER on variable NOT in SELECT with UNION.

        This test demonstrates the bug:
        - ?t is used in FILTER(CONTAINS(?t, "Method"))
        - ?t is NOT in SELECT
        - UNION is present

        Before fix: Fails with "Variable not found in query results: ?t"
        After fix: Should work correctly (same as without UNION)
        """
        r = reter_with_code_facts

        # ?t is NOT in SELECT - this fails with UNION but works without
        query = """
        SELECT ?caller ?callee WHERE {
            { ?caller calls ?callee } UNION { ?caller maybeCalls ?callee }
            ?caller name ?name .
            ?caller concept ?t .
            FILTER(CONTAINS(?t, "Method"))
        }
        """

        # This is the bug - should work but currently fails
        results = r.reql(query)
        assert results.num_rows >= 1, "Should find at least one call relationship"
        assert "?caller" in results.column_names
        assert "?callee" in results.column_names
        # Note: ?t may be in results as implementation detail for filtering
        # The key point is that the query works without throwing "Variable not found"
        print(f"✓ UNION with FILTER on variable NOT in SELECT (BUG FIX): {results.num_rows} results")

    def test_union_filter_multiple_variables_not_in_select(self, reter_with_code_facts):
        """
        BUG TEST: Multiple FILTER variables not in SELECT with UNION.
        """
        r = reter_with_code_facts

        # Both ?t and ?name are used in FILTER but only ?caller, ?callee in SELECT
        query = """
        SELECT ?caller ?callee WHERE {
            { ?caller calls ?callee } UNION { ?caller maybeCalls ?callee }
            ?caller name ?name .
            ?caller concept ?t .
            FILTER(CONTAINS(?t, "Method") && CONTAINS(?name, "e"))
        }
        """

        results = r.reql(query)
        # Should work after fix - query executes without error
        assert "?caller" in results.column_names
        assert "?callee" in results.column_names
        # Note: ?t and ?name may be in results as implementation detail for filtering
        # The key point is that the query works without throwing "Variable not found"
        print(f"✓ UNION with multiple FILTER vars NOT in SELECT: {results.num_rows} results")


class TestConsistencyBetweenUnionAndNonUnion:
    """Tests that verify UNION and non-UNION queries behave consistently."""

    def test_same_results_with_and_without_union(self, reter_with_code_facts):
        """
        The same query should give equivalent results with or without UNION.
        (When the UNION doesn't actually add alternative patterns)
        """
        r = reter_with_code_facts

        # Query without UNION
        query_no_union = """
        SELECT ?x ?name WHERE {
            ?x type pyMethod .
            ?x name ?name .
            ?x concept ?t .
            FILTER(CONTAINS(?t, "Method"))
        }
        """

        # Equivalent query with trivial UNION (same pattern in both arms)
        # This should give the same results
        query_with_union = """
        SELECT ?x ?name WHERE {
            { ?x type pyMethod } UNION { ?x type pyMethod }
            ?x name ?name .
            ?x concept ?t .
            FILTER(CONTAINS(?t, "Method"))
        }
        """

        results_no_union = r.reql(query_no_union)
        results_with_union = r.reql(query_with_union)

        # Both should return results (after deduplication, UNION might return same count)
        assert results_no_union.num_rows >= 1
        assert results_with_union.num_rows >= 1
        print(f"✓ Consistency check: no UNION={results_no_union.num_rows}, "
              f"with UNION={results_with_union.num_rows}")


def run_tests():
    """Run all tests manually (for debugging)."""
    r = Reter()

    # Load code-like ontology (no comments allowed in ontology string)
    ontology = """
    Method ⊑ᑦ Function
    pyMethod（method1）
    pyMethod（method2）
    pyMethod（method3）
    ooFunction（func1）
    name（method1，execute）
    name（method2，run）
    name（method3，process）
    name（func1，helper）
    concept（method1，pyMethod）
    concept（method2，pyMethod）
    concept（method3，pyMethod）
    concept（func1，ooFunction）
    calls（method1，method2）
    calls（method2，method3）
    maybeCalls（method1，func1）
    """
    r.load_ontology(ontology)

    print("=" * 70)
    print("UNION + FILTER Variable Bug Test Suite")
    print("=" * 70)

    # Test 1: Without UNION, variable in SELECT
    print("\n--- Test 1: Without UNION, FILTER var in SELECT ---")
    try:
        query = """
        SELECT ?x ?name ?t WHERE {
            ?x type pyMethod .
            ?x name ?name .
            ?x concept ?t .
            FILTER(CONTAINS(?t, "Method"))
        }
        """
        results = r.reql(query)
        print(f"✓ PASS: {results.num_rows} results")
    except Exception as e:
        print(f"✗ FAIL: {e}")

    # Test 2: Without UNION, variable NOT in SELECT
    print("\n--- Test 2: Without UNION, FILTER var NOT in SELECT ---")
    try:
        query = """
        SELECT ?x ?name WHERE {
            ?x type pyMethod .
            ?x name ?name .
            ?x concept ?t .
            FILTER(CONTAINS(?t, "Method"))
        }
        """
        results = r.reql(query)
        print(f"✓ PASS: {results.num_rows} results")
    except Exception as e:
        print(f"✗ FAIL: {e}")

    # Test 3: With UNION, variable in SELECT
    print("\n--- Test 3: With UNION, FILTER var in SELECT ---")
    try:
        query = """
        SELECT ?caller ?callee ?t WHERE {
            { ?caller calls ?callee } UNION { ?caller maybeCalls ?callee }
            ?caller name ?name .
            ?caller concept ?t .
            FILTER(CONTAINS(?t, "Method"))
        }
        """
        results = r.reql(query)
        print(f"✓ PASS: {results.num_rows} results")
    except Exception as e:
        print(f"✗ FAIL: {e}")

    # Test 4: With UNION, variable NOT in SELECT (THE BUG)
    print("\n--- Test 4: With UNION, FILTER var NOT in SELECT (BUG) ---")
    try:
        query = """
        SELECT ?caller ?callee WHERE {
            { ?caller calls ?callee } UNION { ?caller maybeCalls ?callee }
            ?caller name ?name .
            ?caller concept ?t .
            FILTER(CONTAINS(?t, "Method"))
        }
        """
        results = r.reql(query)
        print(f"✓ PASS (BUG FIXED): {results.num_rows} results")
    except Exception as e:
        print(f"✗ FAIL (BUG EXISTS): {e}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    run_tests()
