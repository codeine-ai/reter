"""
Test Suite for REQL Double UNION Bug (BUG-001)

This test file reproduces the bug where a REQL query containing two separate
UNION blocks returns empty results even though data exists.

Bug: When a query has structure like:
    { ?caller type Method } UNION { ?caller type Function }
    ?caller name ?caller_name .
    ?caller calls ?callee .
    { ?callee type Method } UNION { ?callee type Function }
    ?callee name ?callee_name .

The first UNION works correctly, but adding the second UNION causes
the entire query to return empty results.

See: reter/docs/bugs/BUG-001-double-union-reql.md
"""

import pytest
from reter import Reter


class TestDoubleUnionBug:
    """Test cases that reproduce BUG-001: Double UNION in REQL"""

    @pytest.fixture
    def reasoner_with_calls(self):
        """Create a Reter instance with call graph data"""
        r = Reter()
        # Use Unicode parentheses and comma as required by DL parser
        r.load_ontology("""
            Method ⊑ᑦ owl:Thing
            Function ⊑ᑦ owl:Thing

            Method（m1）
            Method（m2）
            Function（f1）
            Function（f2）

            name（m1，method_one）
            name（m2，method_two）
            name（f1，func_one）
            name（f2，func_two）

            calls（m1，f1）
            calls（f1，m2）
            calls（m2，f2）
        """)
        return r

    def test_single_union_works(self, reasoner_with_calls):
        """Single UNION block with patterns outside should work"""
        r = reasoner_with_calls

        # Query with ONE UNION block - should work
        query = """
        SELECT ?caller ?caller_name ?callee WHERE {
            { ?caller type Method } UNION { ?caller type Function }
            ?caller name ?caller_name .
            ?caller calls ?callee .
        }
        """

        result = r.reql(query)
        result_list = result.to_pylist()

        print(f"\nSingle UNION results: {len(result_list)}")
        for row in result_list:
            print(f"  {row}")

        # Should get 3 results: m1->f1, f1->m2, m2->f2
        assert len(result_list) == 3, (
            f"Single UNION should return 3 results, got {len(result_list)}"
        )

    @pytest.mark.xfail(reason="BUG-001: Double UNION returns empty results")
    def test_double_union_bug(self, reasoner_with_calls):
        """BUG: Two UNION blocks in same query returns empty"""
        r = reasoner_with_calls

        # Query with TWO UNION blocks - currently returns empty (BUG)
        query = """
        SELECT ?caller ?caller_name ?callee ?callee_name WHERE {
            { ?caller type Method } UNION { ?caller type Function }
            ?caller name ?caller_name .
            ?caller calls ?callee .
            { ?callee type Method } UNION { ?callee type Function }
            ?callee name ?callee_name .
        }
        """

        result = r.reql(query)
        result_list = result.to_pylist()

        print(f"\nDouble UNION results: {len(result_list)}")
        for row in result_list:
            print(f"  {row}")

        # Should get 3 results, but currently gets 0
        assert len(result_list) == 3, (
            f"Double UNION should return 3 results, got {len(result_list)}"
        )

        # Verify the expected relationships are present
        callers = {row["?caller"] for row in result_list}
        callees = {row["?callee"] for row in result_list}

        assert "m1" in callers, "m1 should be a caller"
        assert "f1" in callees, "f1 should be a callee"

    @pytest.mark.xfail(reason="BUG-001: Double UNION returns empty results")
    def test_triple_union_bug(self, reasoner_with_calls):
        """Three UNION blocks should also work"""
        r = reasoner_with_calls

        # Add a third UNION for an intermediate check
        query = """
        SELECT ?a ?b ?c WHERE {
            { ?a type Method } UNION { ?a type Function }
            ?a calls ?b .
            { ?b type Method } UNION { ?b type Function }
            ?b calls ?c .
            { ?c type Method } UNION { ?c type Function }
        }
        """

        result = r.reql(query)
        result_list = result.to_pylist()

        print(f"\nTriple UNION results: {len(result_list)}")
        for row in result_list:
            print(f"  {row}")

        # Should get 2 results: m1->f1->m2 and f1->m2->f2
        assert len(result_list) == 2, (
            f"Triple UNION should return 2 results, got {len(result_list)}"
        )


class TestUnionWithPatternsOutside:
    """Test UNION blocks combined with patterns outside the UNION"""

    @pytest.fixture
    def reasoner_basic(self):
        """Create a Reter instance with basic data"""
        r = Reter()
        r.load_ontology("""
            TypeA（a1）
            TypeA（a2）
            TypeB（b1）
            TypeB（b2）

            name（a1，alpha）
            name（a2，beta）
            name（b1，gamma）
            name（b2，delta）

            rel（a1，b1）
            rel（a2，b2）
        """)
        return r

    def test_union_then_pattern(self, reasoner_basic):
        """UNION block followed by pattern should work"""
        r = reasoner_basic

        query = """
        SELECT ?x ?xname WHERE {
            { ?x type TypeA } UNION { ?x type TypeB }
            ?x name ?xname .
        }
        """

        result = r.reql(query)
        result_list = result.to_pylist()

        print(f"\nUNION then pattern: {len(result_list)}")

        # Should get 4 results (a1, a2, b1, b2)
        assert len(result_list) == 4

    def test_pattern_then_union(self, reasoner_basic):
        """Pattern followed by UNION block should work"""
        r = reasoner_basic

        query = """
        SELECT ?x ?xname WHERE {
            ?x name ?xname .
            { ?x type TypeA } UNION { ?x type TypeB }
        }
        """

        result = r.reql(query)
        result_list = result.to_pylist()

        print(f"\nPattern then UNION: {len(result_list)}")

        # Should get 4 results (a1, a2, b1, b2)
        assert len(result_list) == 4

    @pytest.mark.xfail(reason="BUG-001: Double UNION returns empty results")
    def test_union_pattern_union(self, reasoner_basic):
        """UNION block, then pattern, then UNION block"""
        r = reasoner_basic

        query = """
        SELECT ?x ?y WHERE {
            { ?x type TypeA } UNION { ?x type TypeB }
            ?x rel ?y .
            { ?y type TypeA } UNION { ?y type TypeB }
        }
        """

        result = r.reql(query)
        result_list = result.to_pylist()

        print(f"\nUNION-pattern-UNION: {len(result_list)}")

        # Should get 2 results (a1->b1, a2->b2)
        assert len(result_list) == 2


class TestWorkaround:
    """Test the workaround using FILTER with CONTAINS instead of UNION"""

    @pytest.fixture
    def reasoner_with_concepts(self):
        """Create Reter with concept-based type assertions"""
        r = Reter()
        r.load_ontology("""
            Method（m1）
            Function（f1）
            Method（m2）

            concept（m1，Method）
            concept（f1，Function）
            concept（m2，Method）

            name（m1，method_one）
            name（f1，func_one）
            name（m2，method_two）

            calls（m1，f1）
            calls（f1，m2）
        """)
        return r

    def test_workaround_with_filter_contains(self, reasoner_with_concepts):
        """FILTER with CONTAINS works as workaround for double UNION"""
        r = reasoner_with_concepts

        # Workaround: Use FILTER with CONTAINS instead of double UNION
        query = """
        SELECT ?caller ?caller_name ?callee ?callee_name WHERE {
            ?caller calls ?callee .
            ?caller name ?caller_name .
            ?caller concept ?caller_type .
            ?callee name ?callee_name .
            ?callee concept ?callee_type .
            FILTER(CONTAINS(?caller_type, "Method") || CONTAINS(?caller_type, "Function"))
            FILTER(CONTAINS(?callee_type, "Method") || CONTAINS(?callee_type, "Function"))
        }
        """

        result = r.reql(query)
        result_list = result.to_pylist()

        print(f"\nWorkaround results: {len(result_list)}")
        for row in result_list:
            print(f"  {row}")

        # Should get 2 results: m1->f1, f1->m2
        assert len(result_list) == 2


class TestMinimalReproduction:
    """Minimal reproduction cases for BUG-001"""

    def test_minimal_double_union_empty(self):
        """Minimal reproduction: simplest double UNION case"""
        r = Reter()
        r.load_ontology("""
            A（x）
            B（y）
            rel（x，y）
        """)

        # Single UNION - works
        q1 = """
        SELECT ?a ?b WHERE {
            { ?a type A } UNION { ?a type B }
            ?a rel ?b .
        }
        """
        r1 = r.reql(q1)
        print(f"Single UNION: {r1.num_rows} rows")
        assert r1.num_rows == 1, "Single UNION should find x->y"

        # Double UNION - BUG: returns empty or crashes with schema mismatch
        q2 = """
        SELECT ?a ?b WHERE {
            { ?a type A } UNION { ?a type B }
            ?a rel ?b .
            { ?b type A } UNION { ?b type B }
        }
        """
        try:
            r2 = r.reql(q2)
            print(f"Double UNION: {r2.num_rows} rows")

            # If we get here without error, check for empty results
            if r2.num_rows == 0:
                pytest.xfail("BUG-001: Double UNION returns empty instead of 1 row")
            else:
                assert r2.num_rows == 1
        except RuntimeError as e:
            # The bug can manifest as a schema mismatch when concatenating tables
            if "Schema at index" in str(e) or "concatenate tables" in str(e):
                pytest.xfail(f"BUG-001: Double UNION causes schema mismatch: {e}")
            else:
                raise

    def test_minimal_same_variable_double_union(self):
        """Double UNION on same variable - simpler case"""
        r = Reter()
        r.load_ontology("""
            A（x）
            B（x）
            C（x）
            prop（x，value1）
        """)

        # Two UNION blocks on same variable
        query = """
        SELECT ?x ?v WHERE {
            { ?x type A } UNION { ?x type B }
            ?x prop ?v .
            { ?x type B } UNION { ?x type C }
        }
        """
        try:
            result = r.reql(query)
            print(f"Same variable double UNION: {result.num_rows} rows")

            # x is both A and B, so both UNIONs should match
            # and prop(x, value1) should join
            if result.num_rows == 0:
                pytest.xfail("BUG-001: Double UNION on same variable returns empty")
            else:
                assert result.num_rows >= 1
        except RuntimeError as e:
            if "Schema" in str(e) or "concatenate" in str(e):
                pytest.xfail(f"BUG-001: Double UNION schema error: {e}")
            else:
                raise


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
