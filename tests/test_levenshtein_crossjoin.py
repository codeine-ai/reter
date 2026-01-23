"""
Tests for LEVENSHTEIN cross-join queries.

These tests verify that cross-join queries (comparing two different entities
of the same type) work correctly with LEVENSHTEIN.
"""

import pytest
from reter import Reter


@pytest.fixture
def reasoner():
    """Create a fresh reasoner instance for each test."""
    return Reter()


@pytest.fixture
def reasoner_with_similar_methods(reasoner):
    """Reasoner with methods that have similar names."""
    # Methods with similar names (distance 1-2)
    reasoner.add_triple('m1', 'type', 'oo:Method')
    reasoner.add_triple('m1', 'name', 'validate')

    reasoner.add_triple('m2', 'type', 'oo:Method')
    reasoner.add_triple('m2', 'name', 'validete')  # typo - distance 1

    reasoner.add_triple('m3', 'type', 'oo:Method')
    reasoner.add_triple('m3', 'name', 'validated')  # distance 1

    reasoner.add_triple('m4', 'type', 'oo:Method')
    reasoner.add_triple('m4', 'name', 'execute')  # distance 4+ from validate

    reasoner.add_triple('m5', 'type', 'oo:Method')
    reasoner.add_triple('m5', 'name', 'executes')  # distance 1 from execute

    return reasoner


class TestCrossJoinBasic:
    """Basic cross-join tests without LEVENSHTEIN."""

    def test_cross_join_same_name(self, reasoner):
        """Cross-join should find pairs with same name."""
        reasoner.add_triple('m1', 'type', 'oo:Method')
        reasoner.add_triple('m1', 'name', 'foo')
        reasoner.add_triple('m2', 'type', 'oo:Method')
        reasoner.add_triple('m2', 'name', 'foo')
        reasoner.add_triple('m3', 'type', 'oo:Method')
        reasoner.add_triple('m3', 'name', 'bar')

        result = reasoner.reql('''
            SELECT ?m1 ?m2 ?n1 ?n2 WHERE {
                ?m1 type oo:Method . ?m1 name ?n1 .
                ?m2 type oo:Method . ?m2 name ?n2 .
                FILTER(?m1 != ?m2)
                FILTER(?n1 = ?n2)
            }
        ''')

        # Should find m1-m2 and m2-m1 (both have name 'foo')
        assert result.num_rows == 2

    def test_cross_join_all_pairs(self, reasoner):
        """Cross-join should generate all pairs."""
        reasoner.add_triple('m1', 'type', 'oo:Method')
        reasoner.add_triple('m1', 'name', 'a')
        reasoner.add_triple('m2', 'type', 'oo:Method')
        reasoner.add_triple('m2', 'name', 'b')
        reasoner.add_triple('m3', 'type', 'oo:Method')
        reasoner.add_triple('m3', 'name', 'c')

        result = reasoner.reql('''
            SELECT ?m1 ?m2 WHERE {
                ?m1 type oo:Method .
                ?m2 type oo:Method .
                FILTER(?m1 != ?m2)
            }
        ''')

        # 3 methods, each paired with 2 others = 6 pairs
        assert result.num_rows == 6


class TestCrossJoinWithLevenshtein:
    """Cross-join tests with LEVENSHTEIN."""

    def test_cross_join_levenshtein_distance_1(self, reasoner_with_similar_methods):
        """Find pairs with Levenshtein distance exactly 1."""
        result = reasoner_with_similar_methods.reql('''
            SELECT ?m1 ?m2 ?n1 ?n2 WHERE {
                ?m1 type oo:Method . ?m1 name ?n1 .
                ?m2 type oo:Method . ?m2 name ?n2 .
                FILTER(?m1 != ?m2)
                FILTER(LEVENSHTEIN(?n1, ?n2) = 1)
            }
        ''')

        # Expected pairs (bidirectional):
        # validate <-> validete (distance 1)
        # validate <-> validated (distance 1)
        # execute <-> executes (distance 1)
        # Total: 6 pairs (3 unique pairs × 2 directions)
        assert result.num_rows == 6

    def test_cross_join_levenshtein_distance_lte_2(self, reasoner_with_similar_methods):
        """Find pairs with Levenshtein distance <= 2."""
        result = reasoner_with_similar_methods.reql('''
            SELECT ?m1 ?m2 ?n1 ?n2 WHERE {
                ?m1 type oo:Method . ?m1 name ?n1 .
                ?m2 type oo:Method . ?m2 name ?n2 .
                FILTER(?m1 != ?m2)
                FILTER(LEVENSHTEIN(?n1, ?n2) <= 2)
            }
        ''')

        # Should find all pairs with distance 1 + validete<->validated (distance 2)
        # validate <-> validete (1), validate <-> validated (1), validete <-> validated (2)
        # execute <-> executes (1)
        # Total unique pairs: 4, so 8 bidirectional
        assert result.num_rows == 8

    def test_cross_join_levenshtein_with_limit(self, reasoner_with_similar_methods):
        """Cross-join with LEVENSHTEIN respects LIMIT."""
        result = reasoner_with_similar_methods.reql('''
            SELECT ?m1 ?m2 ?n1 ?n2 WHERE {
                ?m1 type oo:Method . ?m1 name ?n1 .
                ?m2 type oo:Method . ?m2 name ?n2 .
                FILTER(?m1 != ?m2)
                FILTER(LEVENSHTEIN(?n1, ?n2) <= 2)
            } LIMIT 3
        ''')

        # LIMIT should return exactly 3 results (there are 8 total matches)
        assert result.num_rows == 3

    def test_cross_join_limit_1_regression(self, reasoner):
        """Regression test: LIMIT 1 with FILTER should return 1 result, not 0.

        This was a bug where LIMIT was applied before FILTER evaluation,
        causing cross-join queries with LIMIT 1 to return 0 results.
        """
        reasoner.add_triple('m1', 'type', 'oo:Method')
        reasoner.add_triple('m1', 'name', 'foo')
        reasoner.add_triple('m2', 'type', 'oo:Method')
        reasoner.add_triple('m2', 'name', 'foos')  # distance 1

        result = reasoner.reql('''
            SELECT ?m1 ?m2 WHERE {
                ?m1 type oo:Method .
                ?m2 type oo:Method .
                FILTER(?m1 != ?m2)
            } LIMIT 1
        ''')

        # Must return exactly 1 result, not 0
        assert result.num_rows == 1

    def test_cross_join_levenshtein_no_matches(self, reasoner):
        """Cross-join returns empty when no pairs match threshold."""
        reasoner.add_triple('m1', 'type', 'oo:Method')
        reasoner.add_triple('m1', 'name', 'apple')
        reasoner.add_triple('m2', 'type', 'oo:Method')
        reasoner.add_triple('m2', 'name', 'banana')

        result = reasoner.reql('''
            SELECT ?m1 ?m2 ?n1 ?n2 WHERE {
                ?m1 type oo:Method . ?m1 name ?n1 .
                ?m2 type oo:Method . ?m2 name ?n2 .
                FILTER(?m1 != ?m2)
                FILTER(LEVENSHTEIN(?n1, ?n2) <= 2)
            }
        ''')

        # apple and banana have distance 6, so no matches
        assert result.num_rows == 0


class TestCrossJoinLargeDataset:
    """Test cross-join performance with larger datasets."""

    def test_cross_join_many_methods(self, reasoner):
        """Cross-join works with many methods."""
        # Add 20 methods with variations of 'process'
        names = [
            'process', 'processes', 'processed', 'processing',
            'precess', 'procss', 'proces', 'procesz',
            'handle', 'handles', 'handled', 'handling',
            'execute', 'executes', 'executed', 'executing',
            'validate', 'validates', 'validated', 'validating'
        ]

        for i, name in enumerate(names):
            reasoner.add_triple(f'm{i}', 'type', 'oo:Method')
            reasoner.add_triple(f'm{i}', 'name', name)

        result = reasoner.reql('''
            SELECT ?m1 ?m2 ?n1 ?n2 WHERE {
                ?m1 type oo:Method . ?m1 name ?n1 .
                ?m2 type oo:Method . ?m2 name ?n2 .
                FILTER(?m1 != ?m2)
                FILTER(LEVENSHTEIN(?n1, ?n2) <= 2)
            } LIMIT 50
        ''')

        # Should find many similar pairs
        assert result.num_rows > 0

    def test_cross_join_finds_typos(self, reasoner):
        """Cross-join can detect typos in method names."""
        # Common method names and their typos
        reasoner.add_triple('m1', 'type', 'oo:Method')
        reasoner.add_triple('m1', 'name', 'initialize')
        reasoner.add_triple('m2', 'type', 'oo:Method')
        reasoner.add_triple('m2', 'name', 'initalize')  # missing 'i'
        reasoner.add_triple('m3', 'type', 'oo:Method')
        reasoner.add_triple('m3', 'name', 'initialise')  # British spelling
        reasoner.add_triple('m4', 'type', 'oo:Method')
        reasoner.add_triple('m4', 'name', 'shutdown')  # unrelated

        result = reasoner.reql('''
            SELECT ?n1 ?n2 WHERE {
                ?m1 type oo:Method . ?m1 name ?n1 .
                ?m2 type oo:Method . ?m2 name ?n2 .
                FILTER(?m1 != ?m2)
                FILTER(LEVENSHTEIN(?n1, ?n2) <= 2)
            }
        ''')

        names = [(row['?n1'], row['?n2']) for row in result.to_pylist()]

        # Should find initialize<->initalize and initialize<->initialise
        assert result.num_rows >= 4  # At least 2 pairs bidirectional

        # Verify shutdown is NOT matched
        for n1, n2 in names:
            assert 'shutdown' not in (n1, n2)


class TestCrossJoinWithClasses:
    """Cross-join tests with classes instead of methods."""

    def test_cross_join_similar_class_names(self, reasoner):
        """Find classes with similar names."""
        reasoner.add_triple('c1', 'type', 'oo:Class')
        reasoner.add_triple('c1', 'name', 'UserService')
        reasoner.add_triple('c2', 'type', 'oo:Class')
        reasoner.add_triple('c2', 'name', 'UserServise')  # typo
        reasoner.add_triple('c3', 'type', 'oo:Class')
        reasoner.add_triple('c3', 'name', 'UserServices')
        reasoner.add_triple('c4', 'type', 'oo:Class')
        reasoner.add_triple('c4', 'name', 'OrderService')  # different

        result = reasoner.reql('''
            SELECT ?c1 ?c2 ?n1 ?n2 WHERE {
                ?c1 type oo:Class . ?c1 name ?n1 .
                ?c2 type oo:Class . ?c2 name ?n2 .
                FILTER(?c1 != ?c2)
                FILTER(LEVENSHTEIN(?n1, ?n2) <= 2)
            }
        ''')

        # UserService <-> UserServise (1), UserService <-> UserServices (1)
        # UserServise <-> UserServices (2)
        # Total: 6 bidirectional pairs
        assert result.num_rows == 6

        # OrderService should not be matched
        names = [(row['?n1'], row['?n2']) for row in result.to_pylist()]
        for n1, n2 in names:
            assert 'OrderService' not in (n1, n2)
