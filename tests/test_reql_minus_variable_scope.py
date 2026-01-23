#!/usr/bin/env python3
"""
Test MINUS Variable Scope Handling in REQL

This test suite verifies that MINUS patterns gracefully handle
filters that reference variables from the outer query (correlated subqueries).

Previously, such queries would fail with "Variable not found" errors.
The fix returns null arrays for missing variables, which causes
comparisons to evaluate to false/null (standard SQL/SPARQL semantics).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from reter import Reter


class TestMinusWithOuterVariables:
    """Test MINUS patterns that reference outer query variables"""

    def test_minus_with_filter_referencing_outer_variable(self):
        """
        Test MINUS pattern with FILTER that references outer variable.

        This pattern is common for "find methods only called within their class":
        - Outer query: ?m definedIn ?c (method in class)
        - MINUS: ?caller calls ?m, ?caller definedIn ?other_class, FILTER(?other_class != ?c)

        The FILTER references ?c from outer query, which doesn't exist in MINUS subquery.
        """
        reasoner = Reter()

        # Class A has method foo, called by bar (same class) and baz (different class)
        reasoner.add_triple("ClassA", "type", "Class")
        reasoner.add_triple("foo", "type", "Method")
        reasoner.add_triple("foo", "definedIn", "ClassA")
        reasoner.add_triple("bar", "type", "Method")
        reasoner.add_triple("bar", "definedIn", "ClassA")
        reasoner.add_triple("bar", "calls", "foo")  # Same class call

        reasoner.add_triple("ClassB", "type", "Class")
        reasoner.add_triple("baz", "type", "Method")
        reasoner.add_triple("baz", "definedIn", "ClassB")
        reasoner.add_triple("baz", "calls", "foo")  # Cross-class call

        # Class C has method qux, only called within ClassC
        reasoner.add_triple("ClassC", "type", "Class")
        reasoner.add_triple("qux", "type", "Method")
        reasoner.add_triple("qux", "definedIn", "ClassC")
        reasoner.add_triple("quux", "type", "Method")
        reasoner.add_triple("quux", "definedIn", "ClassC")
        reasoner.add_triple("quux", "calls", "qux")  # Same class only

        # Query that previously failed with "Variable not found: ?c"
        # Note: This tests that the query executes without error.
        # The results may vary depending on how correlated filters are handled.
        query = """
        SELECT ?m ?c
        WHERE {
            ?m type Method .
            ?m definedIn ?c .
            MINUS {
                ?caller calls ?m .
                ?caller definedIn ?other_class .
                FILTER(?other_class != ?c)
            }
        }
        """

        # Should not throw an error
        results = reasoner.network.reql_query(query)

        # Query should execute successfully
        assert results is not None
        assert '?m' in results.schema.names
        assert '?c' in results.schema.names

    def test_simple_minus_without_outer_reference(self):
        """Test that simple MINUS (no outer variable reference) still works correctly"""
        reasoner = Reter()

        reasoner.add_triple("Alice", "type", "Person")
        reasoner.add_triple("Bob", "type", "Person")
        reasoner.add_triple("Charlie", "type", "Person")
        reasoner.add_triple("Bob", "status", "inactive")

        # Find all persons that don't have status=inactive
        query = """
        SELECT ?person
        WHERE {
            ?person type Person .
            MINUS {
                ?person status "inactive" .
            }
        }
        """

        results = reasoner.network.reql_query(query)
        df = results.to_pandas()

        # Should have Alice and Charlie (not Bob who is inactive)
        persons = set(df['?person'].tolist())
        assert 'Alice' in persons
        assert 'Charlie' in persons
        assert 'Bob' not in persons

    def test_minus_with_shared_variable(self):
        """Test MINUS where patterns share a variable (join key)"""
        reasoner = Reter()

        # People who have skills
        reasoner.add_triple("Alice", "hasSkill", "Python")
        reasoner.add_triple("Alice", "hasSkill", "Java")
        reasoner.add_triple("Bob", "hasSkill", "Python")

        # People who are banned from using certain skills
        reasoner.add_triple("Alice", "bannedFrom", "Java")

        # Find person-skill pairs where the person isn't banned from that skill
        query = """
        SELECT ?person ?skill
        WHERE {
            ?person hasSkill ?skill .
            MINUS {
                ?person bannedFrom ?skill .
            }
        }
        """

        results = reasoner.network.reql_query(query)
        df = results.to_pandas()

        # Alice should have Python (not Java - banned)
        # Bob should have Python
        assert len(df) == 2

        alice_skills = df[df['?person'] == 'Alice']['?skill'].tolist()
        assert 'Python' in alice_skills
        assert 'Java' not in alice_skills

    def test_nested_minus_patterns(self):
        """Test multiple MINUS patterns in sequence"""
        reasoner = Reter()

        reasoner.add_triple("A", "type", "Item")
        reasoner.add_triple("B", "type", "Item")
        reasoner.add_triple("C", "type", "Item")
        reasoner.add_triple("A", "flag1", "true")
        reasoner.add_triple("B", "flag2", "true")

        # Items that don't have flag1 or flag2
        query = """
        SELECT ?item
        WHERE {
            ?item type Item .
            MINUS { ?item flag1 "true" . }
            MINUS { ?item flag2 "true" . }
        }
        """

        results = reasoner.network.reql_query(query)
        df = results.to_pandas()

        # Only C should remain (A has flag1, B has flag2)
        assert len(df) == 1
        assert df['?item'].iloc[0] == 'C'


class TestMinusEdgeCases:
    """Test edge cases for MINUS handling"""

    def test_minus_with_no_matches(self):
        """Test MINUS that matches nothing (all rows kept)"""
        reasoner = Reter()

        reasoner.add_triple("Alice", "type", "Person")
        reasoner.add_triple("Bob", "type", "Person")

        query = """
        SELECT ?person
        WHERE {
            ?person type Person .
            MINUS {
                ?person status "deleted" .
            }
        }
        """

        results = reasoner.network.reql_query(query)

        # Nothing matches the MINUS pattern, so all rows kept
        assert results.num_rows == 2

    def test_minus_excludes_all(self):
        """Test MINUS that excludes all results"""
        reasoner = Reter()

        reasoner.add_triple("Alice", "type", "Person")
        reasoner.add_triple("Bob", "type", "Person")
        reasoner.add_triple("Alice", "isActive", "true")
        reasoner.add_triple("Bob", "isActive", "true")

        query = """
        SELECT ?person
        WHERE {
            ?person type Person .
            MINUS {
                ?person isActive "true" .
            }
        }
        """

        results = reasoner.network.reql_query(query)

        # All persons have exists=true, so all excluded
        assert results.num_rows == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
