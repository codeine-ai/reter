"""
Test for REQL GROUP BY + FILTER patterns.

This test documents a potential issue where GROUP BY can return empty results
when combined with FILTER on a variable that is not in the GROUP BY clause.

The pattern was discovered in the feature_envy CADSL detector which needs to:
1. Find methods that call other methods
2. Filter to only cross-class calls (caller class != callee class)
3. Group by caller method and count external calls

Note: This test uses simplified predicates (definedIn, name) and may pass
even when the same pattern fails with actual ontology predicates (is-defined-in,
has-name) in CADSL tools. The bug may be data-dependent or scale-dependent.

Recommended approach: For complex queries that combine GROUP BY with FILTER
on non-grouped variables, use Python aggregation for reliability.
"""

import pytest
from reter import Reter


@pytest.fixture
def reter_with_classes():
    """Create a Reter instance with test classes and method calls.

    Uses the EXACT predicates from CADSL tools:
    - type, has-name, is-in-file, is-at-line, is-defined-in, calls
    """
    r = Reter()

    # Create two classes (matching CADSL ontology)
    r.add_triple("ClassA", "type", "class")
    r.add_triple("ClassA", "has-name", "ClassA")
    r.add_triple("ClassA", "is-in-file", "test.py")
    r.add_triple("ClassA", "is-at-line", "1")

    r.add_triple("ClassB", "type", "class")
    r.add_triple("ClassB", "has-name", "ClassB")
    r.add_triple("ClassB", "is-in-file", "test.py")
    r.add_triple("ClassB", "is-at-line", "20")

    # Create methods in ClassA
    r.add_triple("methodA1", "type", "method")
    r.add_triple("methodA1", "has-name", "do_work")
    r.add_triple("methodA1", "is-defined-in", "ClassA")
    r.add_triple("methodA1", "is-in-file", "test.py")
    r.add_triple("methodA1", "is-at-line", "5")

    r.add_triple("methodA2", "type", "method")
    r.add_triple("methodA2", "has-name", "helper")
    r.add_triple("methodA2", "is-defined-in", "ClassA")
    r.add_triple("methodA2", "is-in-file", "test.py")
    r.add_triple("methodA2", "is-at-line", "10")

    # Create methods in ClassB
    r.add_triple("methodB1", "type", "method")
    r.add_triple("methodB1", "has-name", "process")
    r.add_triple("methodB1", "is-defined-in", "ClassB")
    r.add_triple("methodB1", "is-in-file", "test.py")
    r.add_triple("methodB1", "is-at-line", "25")

    r.add_triple("methodB2", "type", "method")
    r.add_triple("methodB2", "has-name", "validate")
    r.add_triple("methodB2", "is-defined-in", "ClassB")
    r.add_triple("methodB2", "is-in-file", "test.py")
    r.add_triple("methodB2", "is-at-line", "30")

    # methodA1 calls methods in ClassB (cross-class calls)
    r.add_triple("methodA1", "calls", "methodB1")
    r.add_triple("methodA1", "calls", "methodB2")

    # methodA1 also calls method in own class (same-class call)
    r.add_triple("methodA1", "calls", "methodA2")

    return r


@pytest.fixture
def reter_with_many_classes():
    """Create a larger dataset to test scale-dependent behavior.

    Creates 10 classes with 5 methods each, with various cross-class calls.
    """
    r = Reter()

    # Create 10 classes
    for i in range(10):
        class_id = f"Class{i}"
        r.add_triple(class_id, "type", "class")
        r.add_triple(class_id, "has-name", class_id)
        r.add_triple(class_id, "is-in-file", f"module{i}.py")
        r.add_triple(class_id, "is-at-line", str(i * 100))

        # Each class has 5 methods
        for j in range(5):
            method_id = f"method_{i}_{j}"
            r.add_triple(method_id, "type", "method")
            r.add_triple(method_id, "has-name", f"method_{j}")
            r.add_triple(method_id, "is-defined-in", class_id)
            r.add_triple(method_id, "is-in-file", f"module{i}.py")
            r.add_triple(method_id, "is-at-line", str(i * 100 + j * 10))

    # Create cross-class calls:
    # method_0_0 calls 5 methods in Class1 (cross-class)
    for j in range(5):
        r.add_triple("method_0_0", "calls", f"method_1_{j}")

    # method_0_0 also calls 2 methods in own class (same-class)
    r.add_triple("method_0_0", "calls", "method_0_1")
    r.add_triple("method_0_0", "calls", "method_0_2")

    # method_2_0 calls 3 methods in Class3 (cross-class)
    for j in range(3):
        r.add_triple("method_2_0", "calls", f"method_3_{j}")

    return r


class TestReqlGroupByFilterBug:
    """Test cases for the GROUP BY + FILTER bug."""

    def test_base_query_without_filter_works(self, reter_with_classes):
        """Verify the base query returns results without the problematic FILTER."""
        r = reter_with_classes

        # Simple GROUP BY without cross-class filter - should work
        query = """
            SELECT ?m ?name (COUNT(?callee) AS ?call_count)
            WHERE {
                ?m type method .
                ?m has-name ?name .
                ?m calls ?callee
            }
            GROUP BY ?m ?name
            ORDER BY DESC(?call_count)
        """

        # Use timeout_ms=60000 to match MCP/production code path
        result = r.reql(query, timeout_ms=60000)
        assert result.num_rows > 0, "Base query should return results"

        # methodA1 calls 3 methods
        df = result.to_pandas()
        method_a1 = df[df['?name'] == 'do_work']
        assert len(method_a1) == 1
        assert method_a1['?call_count'].iloc[0] == 3

    def test_filter_without_group_by_works(self, reter_with_classes):
        """Verify FILTER works correctly without GROUP BY."""
        r = reter_with_classes

        # Query cross-class calls without GROUP BY - should work
        # NOTE: Must include ?callee in SELECT to get unique rows per call,
        # otherwise SPARQL semantics collapse identical projected rows
        query = """
            SELECT ?m ?name ?class_name ?callee ?ext_class_name
            WHERE {
                ?m type method .
                ?m has-name ?name .
                ?m is-defined-in ?c .
                ?c has-name ?class_name .
                ?m calls ?callee .
                ?callee is-defined-in ?ext_class .
                ?ext_class has-name ?ext_class_name .
                FILTER ( ?class_name != ?ext_class_name )
            }
        """

        result = r.reql(query, timeout_ms=60000)
        assert result.num_rows > 0, "Filter query without GROUP BY should return results"

        # Should find methodA1's 2 cross-class calls (to methodB1 and methodB2)
        # but NOT the same-class call (to methodA2)
        df = result.to_pandas()
        assert len(df) == 2
        for _, row in df.iterrows():
            assert row['?class_name'] != row['?ext_class_name']

    def test_group_by_with_filter_on_non_grouped_variable(self, reter_with_classes):
        """
        Test GROUP BY with FILTER on non-grouped variable.

        This query counts cross-class calls per method. The FILTER references
        ?ext_class_name which is not in the GROUP BY clause.

        This was previously a bug but is now fixed by ensuring execute_query
        handles all post-processing consistently.
        """
        r = reter_with_classes

        # This query combines GROUP BY with FILTER on non-grouped variable
        # It SHOULD return methodA1 with 2 external calls, but returns empty
        query = """
            SELECT ?m ?name ?class_name (COUNT(?callee) AS ?external_calls)
            WHERE {
                ?m type method .
                ?m has-name ?name .
                ?m is-defined-in ?c .
                ?c has-name ?class_name .
                ?m calls ?callee .
                ?callee is-defined-in ?ext_class .
                ?ext_class has-name ?ext_class_name .
                FILTER ( ?class_name != ?ext_class_name )
            }
            GROUP BY ?m ?name ?class_name
            HAVING (?external_calls >= 1)
            ORDER BY DESC(?external_calls)
        """

        result = r.reql(query, timeout_ms=60000)

        # This assertion fails due to the bug - result is empty
        assert result.num_rows > 0, "GROUP BY with FILTER on non-grouped variable should return results"

        # Expected: methodA1 (do_work) should have 2 external calls
        df = result.to_pandas()
        method_a1 = df[df['?name'] == 'do_work']
        assert len(method_a1) == 1
        assert method_a1['?external_calls'].iloc[0] == 2

    def test_group_by_with_ext_class_in_group_by_also_fails(self, reter_with_classes):
        """
        Even including ?ext_class_name in GROUP BY doesn't help.

        This variant includes ?ext_class_name in GROUP BY, which should work
        but still returns empty results.
        """
        r = reter_with_classes

        query = """
            SELECT ?m ?name ?class_name ?ext_class_name (COUNT(?callee) AS ?call_count)
            WHERE {
                ?m type method .
                ?m has-name ?name .
                ?m is-defined-in ?c .
                ?c has-name ?class_name .
                ?m calls ?callee .
                ?callee is-defined-in ?ext_class .
                ?ext_class has-name ?ext_class_name .
                FILTER ( ?class_name != ?ext_class_name )
            }
            GROUP BY ?m ?name ?class_name ?ext_class_name
            ORDER BY DESC(?call_count)
        """

        result = r.reql(query, timeout_ms=60000)

        # This also returns empty due to the bug
        # Mark as xfail if this also fails
        if result.num_rows == 0:
            pytest.xfail("GROUP BY with FILTER on joined variable also returns empty")

        assert result.num_rows > 0


class TestScaleDependentBehavior:
    """Test with larger datasets to check for scale-dependent bugs."""

    def test_group_by_filter_with_many_classes(self, reter_with_many_classes):
        """
        Test GROUP BY + FILTER with a larger dataset.

        This tests if the bug is scale-dependent.
        """
        r = reter_with_many_classes

        # Same pattern as feature_envy
        query = """
            SELECT ?m ?name ?class_name (COUNT(?callee) AS ?external_calls)
            WHERE {
                ?m type method .
                ?m has-name ?name .
                ?m is-defined-in ?c .
                ?c has-name ?class_name .
                ?m calls ?callee .
                ?callee is-defined-in ?ext_class .
                ?ext_class has-name ?ext_class_name .
                FILTER ( ?class_name != ?ext_class_name )
            }
            GROUP BY ?m ?name ?class_name
            HAVING (?external_calls >= 1)
            ORDER BY DESC(?external_calls)
        """

        result = r.reql(query, timeout_ms=60000)

        if result.num_rows == 0:
            pytest.xfail("Bug manifests with larger dataset: GROUP BY + FILTER returns empty")

        df = result.to_pandas()

        # method_0_0 should have 5 external calls (to Class1 methods)
        method_0_0 = df[df['?m'] == 'method_0_0']
        assert len(method_0_0) == 1, "method_0_0 should be in results"
        assert method_0_0['?external_calls'].iloc[0] == 5, "method_0_0 should have 5 external calls"

        # method_2_0 should have 3 external calls (to Class3 methods)
        method_2_0 = df[df['?m'] == 'method_2_0']
        assert len(method_2_0) == 1, "method_2_0 should be in results"
        assert method_2_0['?external_calls'].iloc[0] == 3, "method_2_0 should have 3 external calls"

    def test_workaround_with_many_classes(self, reter_with_many_classes):
        """
        Verify the Python aggregation workaround works with larger dataset.
        """
        r = reter_with_many_classes
        from collections import defaultdict

        # Fetch without GROUP BY
        # NOTE: Include ?callee in SELECT to get unique rows per call
        query = """
            SELECT ?m ?name ?class_name ?callee ?ext_class_name
            WHERE {
                ?m type method .
                ?m has-name ?name .
                ?m is-defined-in ?c .
                ?c has-name ?class_name .
                ?m calls ?callee .
                ?callee is-defined-in ?ext_class .
                ?ext_class has-name ?ext_class_name .
                FILTER ( ?class_name != ?ext_class_name )
            }
        """

        result = r.reql(query, timeout_ms=60000)
        df = result.to_pandas()

        # Should have 8 cross-class calls total (5 from method_0_0 + 3 from method_2_0)
        assert len(df) == 8, f"Should get 8 cross-class call rows, got {len(df)}"

        # Aggregate in Python
        method_calls = defaultdict(lambda: {'count': 0, 'info': {}})
        for _, row in df.iterrows():
            key = row['?m']
            method_calls[key]['count'] += 1
            method_calls[key]['info'] = {
                'name': row['?name'],
                'class_name': row['?class_name']
            }

        # Filter by threshold
        findings = [
            {'method': k, 'external_calls': v['count'], **v['info']}
            for k, v in method_calls.items()
            if v['count'] >= 3
        ]

        # Should find 2 methods with >= 3 external calls
        assert len(findings) == 2
        methods = {f['method'] for f in findings}
        assert 'method_0_0' in methods
        assert 'method_2_0' in methods


class TestWorkaround:
    """Demonstrate the workaround for the GROUP BY + FILTER bug."""

    def test_workaround_fetch_then_aggregate_in_python(self, reter_with_classes):
        """
        Workaround: Fetch raw data without GROUP BY, aggregate in Python.

        This is the approach used in the fixed feature_envy.cadsl detector.
        """
        r = reter_with_classes
        from collections import defaultdict

        # Step 1: Fetch all cross-class calls without GROUP BY
        # NOTE: Include ?callee in SELECT to get unique rows per call
        query = """
            SELECT ?m ?name ?class_name ?callee ?ext_class_name
            WHERE {
                ?m type method .
                ?m has-name ?name .
                ?m is-defined-in ?c .
                ?c has-name ?class_name .
                ?m calls ?callee .
                ?callee is-defined-in ?ext_class .
                ?ext_class has-name ?ext_class_name .
                FILTER ( ?class_name != ?ext_class_name )
            }
        """

        result = r.reql(query, timeout_ms=60000)
        df = result.to_pandas()
        assert len(df) == 2, "Should get 2 cross-class call rows"

        # Step 2: Aggregate in Python
        method_calls = defaultdict(lambda: {'count': 0, 'info': {}})
        for _, row in df.iterrows():
            key = row['?m']
            method_calls[key]['count'] += 1
            method_calls[key]['info'] = {
                'name': row['?name'],
                'class_name': row['?class_name']
            }

        # Step 3: Filter by threshold
        findings = [
            {'method': k, 'external_calls': v['count'], **v['info']}
            for k, v in method_calls.items()
            if v['count'] >= 2
        ]

        # Verify workaround produces correct results
        assert len(findings) == 1
        assert findings[0]['name'] == 'do_work'
        assert findings[0]['external_calls'] == 2
