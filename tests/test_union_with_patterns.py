"""
Test Suite for REQL UNION with patterns outside UNION blocks.

This tests the case where UNION is followed by additional patterns:
    { ?x type A } UNION { ?x type B }
    ?x name ?name .  <-- pattern OUTSIDE the UNION blocks

This is failing with "Variable not found in query results" error.
"""

import pytest
from reter import Reter


@pytest.fixture
def reasoner_with_data():
    """Create a reasoner with test data"""
    r = Reter()
    r.load_ontology("""
        py:Method（m1）
        py:Method（m2）
        py:Function（f1）
        py:Function（f2）

        name（m1，"method1"）
        name（m2，"method2"）
        name（f1，"function1"）
        name（f2，"function2"）

        inFile（m1，"file1.py"）
        inFile（m2，"file1.py"）
        inFile（f1，"file2.py"）
        inFile（f2，"file2.py"）

        atLine（m1，"10"）
        atLine（m2，"20"）
        atLine（f1，"30"）
        atLine（f2，"40"）

        calls（m1，"execute_select"）
        calls（m2，"other_func"）
        calls（f1，"execute_select"）
        calls（f2，"third_func"）
    """)
    return r


class TestUnionBaseline:
    """Baseline tests - UNION without additional patterns"""

    def test_simple_type_query_method(self, reasoner_with_data):
        """Test simple type query for Method"""
        r = reasoner_with_data
        results = r.reql("SELECT ?x WHERE { ?x type py:Method }").to_pylist()
        print(f"Methods: {results}")
        assert len(results) == 2
        names = {row["?x"] for row in results}
        assert names == {"m1", "m2"}

    def test_simple_type_query_function(self, reasoner_with_data):
        """Test simple type query for Function"""
        r = reasoner_with_data
        results = r.reql("SELECT ?x WHERE { ?x type py:Function }").to_pylist()
        print(f"Functions: {results}")
        assert len(results) == 2
        names = {row["?x"] for row in results}
        assert names == {"f1", "f2"}

    def test_union_without_additional_patterns(self, reasoner_with_data):
        """Test UNION without patterns outside the UNION blocks"""
        r = reasoner_with_data
        query = """
            SELECT ?x WHERE {
                { ?x type py:Method }
                UNION
                { ?x type py:Function }
            }
        """
        results = r.reql(query).to_pylist()
        print(f"UNION result: {results}")
        assert len(results) == 4
        names = {row["?x"] for row in results}
        assert names == {"m1", "m2", "f1", "f2"}


class TestUnionWithAdditionalPatterns:
    """Tests for UNION with patterns OUTSIDE the UNION blocks - THE FAILING CASE"""

    def test_union_with_one_additional_pattern(self, reasoner_with_data):
        """Test UNION with one additional pattern outside"""
        r = reasoner_with_data
        query = """
            SELECT ?x ?name WHERE {
                { ?x type py:Method }
                UNION
                { ?x type py:Function }
                ?x name ?name .
            }
        """
        results = r.reql(query).to_pylist()
        print(f"UNION + name pattern: {results}")

        # Should return 4 rows (2 methods + 2 functions) with their names
        assert len(results) == 4
        names = {row["?name"] for row in results}
        # Data properties store values with quotes
        assert names == {'"method1"', '"method2"', '"function1"', '"function2"'}

    def test_union_with_multiple_additional_patterns(self, reasoner_with_data):
        """Test UNION with multiple additional patterns outside"""
        r = reasoner_with_data
        query = """
            SELECT ?x ?name ?file WHERE {
                { ?x type py:Method }
                UNION
                { ?x type py:Function }
                ?x name ?name .
                ?x inFile ?file .
            }
        """
        results = r.reql(query).to_pylist()
        print(f"UNION + name + file patterns: {results}")

        # Should return 4 rows with name and file
        assert len(results) == 4

    def test_union_with_filter_on_additional_pattern(self, reasoner_with_data):
        """Test UNION with FILTER on pattern outside UNION - similar to find_usages"""
        r = reasoner_with_data
        query = """
            SELECT ?x ?name ?callee WHERE {
                { ?x type py:Method }
                UNION
                { ?x type py:Function }
                ?x name ?name .
                ?x calls ?callee .
                FILTER ( CONTAINS(?callee, "execute_select") )
            }
        """
        results = r.reql(query).to_pylist()
        print(f"UNION + filter result: {results}")

        # Should return m1 and f1 (both call execute_select)
        assert len(results) == 2
        names = {row["?name"] for row in results}
        # Data properties store values with quotes
        assert names == {'"method1"', '"function1"'}


class TestUnionWithPatternsAndTimeout:
    """Test UNION with additional patterns using timeout parameter"""

    def test_union_patterns_no_timeout(self, reasoner_with_data):
        """Test with timeout_ms=0 (no timeout)"""
        r = reasoner_with_data
        query = """
            SELECT ?x ?name WHERE {
                { ?x type py:Method }
                UNION
                { ?x type py:Function }
                ?x name ?name .
            }
        """
        results = r.reql(query, timeout_ms=0).to_pylist()
        print(f"UNION + pattern (timeout=0): {results}")
        assert len(results) == 4

    def test_union_patterns_with_timeout(self, reasoner_with_data):
        """Test with timeout_ms > 0"""
        r = reasoner_with_data
        query = """
            SELECT ?x ?name WHERE {
                { ?x type py:Method }
                UNION
                { ?x type py:Function }
                ?x name ?name .
            }
        """
        results = r.reql(query, timeout_ms=5000).to_pylist()
        print(f"UNION + pattern (timeout=5000): {results}")
        assert len(results) == 4


class TestUnionPatternsInsideBlocks:
    """Test that patterns INSIDE UNION blocks work correctly"""

    def test_patterns_inside_each_union_block(self, reasoner_with_data):
        """Patterns inside each UNION block should work"""
        r = reasoner_with_data
        query = """
            SELECT ?x ?name WHERE {
                { ?x type py:Method . ?x name ?name }
                UNION
                { ?x type py:Function . ?x name ?name }
            }
        """
        results = r.reql(query).to_pylist()
        print(f"Patterns inside UNION blocks: {results}")

        # Should return 4 rows
        assert len(results) == 4
        names = {row["?name"] for row in results}
        # Data properties store values with quotes
        assert names == {'"method1"', '"method2"', '"function1"', '"function2"'}


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
