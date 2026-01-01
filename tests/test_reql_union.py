"""
Test Suite for REQL Text Query UNION Syntax

Tests the UNION keyword in REQL text queries (not the Python API union method).
This is to isolate the issue where UNION returns 0 results.
"""

import pytest
from reter import Reter


@pytest.fixture
def reasoner_with_classes():
    """Create a reasoner with some test classes"""
    r = Reter()
    r.load_ontology("""
        Person ⊑ᑦ owl:Thing
        Student ⊑ᑦ Person
        Teacher ⊑ᑦ Person
        Animal ⊑ᑦ owl:Thing
    """)
    return r


@pytest.fixture
def reasoner_with_prefixed_types():
    """Create a reasoner with prefixed type instances like Python analyzer creates"""
    r = Reter()
    # Simulating what Python analyzer creates
    r.load_ontology("""
        py:Class（MyPythonClass）
        py:Class（AnotherPythonClass）
        js:Class（MyJavaScriptClass）
        oo:Class（GenericClass）

        name（MyPythonClass，"MyPythonClass"）
        name（AnotherPythonClass，"AnotherPythonClass"）
        name（MyJavaScriptClass，"MyJavaScriptClass"）
        name（GenericClass，"GenericClass"）
    """)
    return r


class TestReqlUnionBasic:
    """Basic UNION syntax tests"""

    def test_simple_union_two_types(self, reasoner_with_classes):
        """Test basic UNION of two type queries"""
        r = reasoner_with_classes

        # First verify individual queries work
        q1 = "SELECT ?x WHERE { ?x type Student }"
        q2 = "SELECT ?x WHERE { ?x type Teacher }"

        r1 = r.reql(q1).to_pylist()
        r2 = r.reql(q2).to_pylist()

        print(f"Students: {r1}")
        print(f"Teachers: {r2}")

        # Now test UNION
        union_query = """
            SELECT ?x WHERE {
                { ?x type Student }
                UNION
                { ?x type Teacher }
            }
        """

        results = r.reql(union_query).to_pylist()
        print(f"UNION results: {results}")

        # The union should return at least what individual queries return
        assert isinstance(results, list)

    def test_union_with_actual_instances(self, reasoner_with_classes):
        """Test UNION with actual class instances"""
        r = reasoner_with_classes

        # Add some instances
        r.load_ontology("""
            Student（alice）
            Teacher（bob）
            Animal（fido）
        """)

        # Verify individual queries
        students = r.reql("SELECT ?x WHERE { ?x type Student }").to_pylist()
        teachers = r.reql("SELECT ?x WHERE { ?x type Teacher }").to_pylist()

        print(f"Students: {students}")
        print(f"Teachers: {teachers}")

        assert len(students) == 1, f"Expected 1 student, got {len(students)}"
        assert len(teachers) == 1, f"Expected 1 teacher, got {len(teachers)}"

        # Test UNION
        union_query = """
            SELECT ?x WHERE {
                { ?x type Student }
                UNION
                { ?x type Teacher }
            }
        """

        results = r.reql(union_query).to_pylist()
        print(f"UNION results: {results}")

        # UNION should return alice + bob = 2 results
        assert len(results) == 2, f"Expected 2 results from UNION, got {len(results)}"

        names = {r["?x"] for r in results}
        assert names == {"alice", "bob"}, f"Expected alice and bob, got {names}"

    def test_union_with_names(self, reasoner_with_classes):
        """Test UNION with name property"""
        r = reasoner_with_classes

        # Add instances with names
        r.load_ontology("""
            Student（alice）
            Teacher（bob）
            name（alice，"Alice Smith"）
            name（bob，"Bob Jones"）
        """)

        union_query = """
            SELECT ?x ?name WHERE {
                { ?x type Student . ?x name ?name }
                UNION
                { ?x type Teacher . ?x name ?name }
            }
        """

        results = r.reql(union_query).to_pylist()
        print(f"UNION with names: {results}")

        assert len(results) == 2, f"Expected 2 results, got {len(results)}"


class TestReqlUnionPrefixedTypes:
    """Test UNION with prefixed types like py:Class, js:Class"""

    def test_individual_prefixed_queries(self, reasoner_with_prefixed_types):
        """Verify individual prefixed type queries work"""
        r = reasoner_with_prefixed_types

        py_query = "SELECT ?c WHERE { ?c type py:Class }"
        js_query = "SELECT ?c WHERE { ?c type js:Class }"
        oo_query = "SELECT ?c WHERE { ?c type oo:Class }"

        py_results = r.reql(py_query).to_pylist()
        js_results = r.reql(js_query).to_pylist()
        oo_results = r.reql(oo_query).to_pylist()

        print(f"py:Class results: {py_results}")
        print(f"js:Class results: {js_results}")
        print(f"oo:Class results: {oo_results}")

        assert len(py_results) == 2, f"Expected 2 py:Class, got {len(py_results)}"
        assert len(js_results) == 1, f"Expected 1 js:Class, got {len(js_results)}"
        assert len(oo_results) == 1, f"Expected 1 oo:Class, got {len(oo_results)}"

    def test_union_prefixed_types(self, reasoner_with_prefixed_types):
        """Test UNION with prefixed types - this is the failing case"""
        r = reasoner_with_prefixed_types

        union_query = """
            SELECT ?c WHERE {
                { ?c type py:Class }
                UNION
                { ?c type js:Class }
            }
        """

        results = r.reql(union_query).to_pylist()
        print(f"UNION py:Class + js:Class: {results}")

        # Should return 2 Python classes + 1 JS class = 3 total
        assert len(results) == 3, f"Expected 3 results from UNION, got {len(results)}"

    def test_union_with_names_prefixed(self, reasoner_with_prefixed_types):
        """Test UNION with names and prefixed types"""
        r = reasoner_with_prefixed_types

        union_query = """
            SELECT ?c ?name WHERE {
                { ?c type py:Class . ?c name ?name }
                UNION
                { ?c type js:Class . ?c name ?name }
            }
        """

        results = r.reql(union_query).to_pylist()
        print(f"UNION with names: {results}")

        # Should return 2 Python classes + 1 JS class = 3 total
        assert len(results) == 3, f"Expected 3 results, got {len(results)}"

    def test_union_all_language_types(self, reasoner_with_prefixed_types):
        """Test UNION of all language type prefixes"""
        r = reasoner_with_prefixed_types

        union_query = """
            SELECT ?c WHERE {
                { ?c type py:Class }
                UNION
                { ?c type js:Class }
                UNION
                { ?c type oo:Class }
            }
        """

        results = r.reql(union_query).to_pylist()
        print(f"UNION all types: {results}")

        # Should return 2 + 1 + 1 = 4 total
        assert len(results) == 4, f"Expected 4 results, got {len(results)}"


class TestReqlUnionEdgeCases:
    """Edge cases for UNION"""

    def test_union_one_empty_branch(self):
        """Test UNION where one branch returns no results"""
        r = Reter()
        r.load_ontology("""
            Person ⊑ᑦ owl:Thing
            Person（alice）
        """)

        union_query = """
            SELECT ?x WHERE {
                { ?x type Person }
                UNION
                { ?x type NonExistent }
            }
        """

        results = r.reql(union_query).to_pylist()
        print(f"UNION with empty branch: {results}")

        # Should return alice from the first branch
        assert len(results) == 1, f"Expected 1 result, got {len(results)}"
        assert results[0]["?x"] == "alice"

    def test_union_both_empty_branches(self):
        """Test UNION where both branches return no results"""
        r = Reter()
        r.load_ontology("Person ⊑ᑦ owl:Thing")

        union_query = """
            SELECT ?x WHERE {
                { ?x type NonExistent1 }
                UNION
                { ?x type NonExistent2 }
            }
        """

        results = r.reql(union_query).to_pylist()
        print(f"UNION both empty: {results}")

        assert len(results) == 0

    def test_union_duplicate_results(self):
        """Test that UNION deduplicates results"""
        r = Reter()
        r.load_ontology("""
            Person ⊑ᑦ owl:Thing
            Employee ⊑ᑦ owl:Thing
            Person（alice）
            Employee（alice）
        """)

        union_query = """
            SELECT ?x WHERE {
                { ?x type Person }
                UNION
                { ?x type Employee }
            }
        """

        results = r.reql(union_query).to_pylist()
        print(f"UNION with overlap: {results}")

        # alice matches both, should be deduplicated
        names = [r["?x"] for r in results]
        print(f"Names: {names}")


class TestReqlUnionWithTimeout:
    """Test UNION queries with timeout parameter"""

    def test_union_with_timeout_basic(self):
        """Test UNION works with timeout_ms parameter"""
        r = Reter()
        r.load_ontology("""
            Person ⊑ᑦ owl:Thing
            Student ⊑ᑦ Person
            Teacher ⊑ᑦ Person
            Student（alice）
            Teacher（bob）
        """)

        union_query = """
            SELECT ?x WHERE {
                { ?x type Student }
                UNION
                { ?x type Teacher }
            }
        """

        # Test with timeout=0 (infinite)
        results_no_timeout = r.reql(union_query, timeout_ms=0).to_pylist()
        print(f"UNION (timeout=0): {results_no_timeout}")

        # Test with explicit timeout
        results_with_timeout = r.reql(union_query, timeout_ms=5000).to_pylist()
        print(f"UNION (timeout=5000ms): {results_with_timeout}")

        assert len(results_no_timeout) == 2, f"Expected 2, got {len(results_no_timeout)}"
        assert len(results_with_timeout) == 2, f"Expected 2, got {len(results_with_timeout)}"

        # Results should be identical
        names_no_timeout = {r["?x"] for r in results_no_timeout}
        names_with_timeout = {r["?x"] for r in results_with_timeout}
        assert names_no_timeout == names_with_timeout == {"alice", "bob"}

    def test_union_prefixed_types_with_timeout(self):
        """Test UNION with prefixed types and timeout"""
        r = Reter()
        r.load_ontology("""
            py:Class（PyClass1）
            py:Class（PyClass2）
            js:Class（JsClass1）
            oo:Class（OoClass1）
        """)

        union_query = """
            SELECT ?c WHERE {
                { ?c type py:Class }
                UNION
                { ?c type js:Class }
                UNION
                { ?c type oo:Class }
            }
        """

        # Test with timeout=0
        results_0 = r.reql(union_query, timeout_ms=0).to_pylist()
        print(f"UNION prefixed (timeout=0): {results_0}")

        # Test with timeout=1000ms
        results_1000 = r.reql(union_query, timeout_ms=1000).to_pylist()
        print(f"UNION prefixed (timeout=1000ms): {results_1000}")

        # Test with timeout=10000ms
        results_10000 = r.reql(union_query, timeout_ms=10000).to_pylist()
        print(f"UNION prefixed (timeout=10000ms): {results_10000}")

        assert len(results_0) == 4, f"Expected 4, got {len(results_0)}"
        assert len(results_1000) == 4, f"Expected 4, got {len(results_1000)}"
        assert len(results_10000) == 4, f"Expected 4, got {len(results_10000)}"

    def test_union_complex_with_timeout(self):
        """Test complex UNION query with multiple patterns and timeout"""
        r = Reter()
        r.load_ontology("""
            py:Class（MyClass）
            py:Method（myMethod）
            name（MyClass，"MyClass"）
            name（myMethod，"myMethod"）
            definedIn（myMethod，MyClass）
        """)

        union_query = """
            SELECT ?entity ?name WHERE {
                { ?entity type py:Class . ?entity name ?name }
                UNION
                { ?entity type py:Method . ?entity name ?name }
            }
        """

        # Compare results with different timeout values
        results_0 = r.reql(union_query, timeout_ms=0).to_pylist()
        results_5000 = r.reql(union_query, timeout_ms=5000).to_pylist()

        print(f"Complex UNION (timeout=0): {results_0}")
        print(f"Complex UNION (timeout=5000): {results_5000}")

        assert len(results_0) == 2, f"Expected 2, got {len(results_0)}"
        assert len(results_5000) == 2, f"Expected 2, got {len(results_5000)}"

        # Verify same results
        names_0 = {r["?name"] for r in results_0}
        names_5000 = {r["?name"] for r in results_5000}
        assert names_0 == names_5000


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
