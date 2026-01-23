"""
Tests for LEVENSHTEIN function in REQL.

LEVENSHTEIN(?str1, ?str2) computes the edit distance between two strings.
It returns an integer representing the minimum number of single-character
edits (insertions, deletions, substitutions) required to transform str1 into str2.
"""

import pytest
from reter import Reter


@pytest.fixture
def reasoner():
    """Create a fresh reasoner instance for each test."""
    return Reter()


@pytest.fixture
def reasoner_with_methods(reasoner):
    """Reasoner with test method data loaded."""
    # Methods with similar names
    reasoner.add_triple('m1', 'type', 'oo:Method')
    reasoner.add_triple('m1', 'name', 'getUserName')

    reasoner.add_triple('m2', 'type', 'oo:Method')
    reasoner.add_triple('m2', 'name', 'getUserNames')  # distance 1 from m1

    reasoner.add_triple('m3', 'type', 'oo:Method')
    reasoner.add_triple('m3', 'name', 'setUserName')  # distance 1 from m1

    reasoner.add_triple('m4', 'type', 'oo:Method')
    reasoner.add_triple('m4', 'name', 'deleteUser')  # distance 7 from m1

    reasoner.add_triple('m5', 'type', 'oo:Method')
    reasoner.add_triple('m5', 'name', 'execute')

    reasoner.add_triple('m6', 'type', 'oo:Method')
    reasoner.add_triple('m6', 'name', 'executes')  # distance 1 from m5

    reasoner.add_triple('m7', 'type', 'oo:Method')
    reasoner.add_triple('m7', 'name', 'run')  # distance 7 from m5

    return reasoner


class TestLevenshteinBasic:
    """Basic LEVENSHTEIN function tests."""

    def test_levenshtein_identical_strings(self, reasoner):
        """LEVENSHTEIN of identical strings should be 0."""
        reasoner.add_triple('a', 'type', 'oo:Method')
        reasoner.add_triple('a', 'name', 'test')

        result = reasoner.reql('''
            SELECT ?m ?name WHERE {
                ?m type oo:Method . ?m name ?name .
                FILTER(LEVENSHTEIN(?name, "test") = 0)
            }
        ''')

        assert result.num_rows == 1
        assert result.column('?name').to_pylist()[0] == 'test'

    def test_levenshtein_one_char_difference(self, reasoner):
        """LEVENSHTEIN with one character difference should be 1."""
        reasoner.add_triple('a', 'type', 'oo:Method')
        reasoner.add_triple('a', 'name', 'test')
        reasoner.add_triple('b', 'type', 'oo:Method')
        reasoner.add_triple('b', 'name', 'tests')  # one char added
        reasoner.add_triple('c', 'type', 'oo:Method')
        reasoner.add_triple('c', 'name', 'best')   # one char changed
        reasoner.add_triple('d', 'type', 'oo:Method')
        reasoner.add_triple('d', 'name', 'est')    # one char removed

        result = reasoner.reql('''
            SELECT ?m ?name WHERE {
                ?m type oo:Method . ?m name ?name .
                FILTER(LEVENSHTEIN(?name, "test") = 1)
            }
            ORDER BY ?name
        ''')

        names = result.column('?name').to_pylist()
        assert len(names) == 3
        assert 'tests' in names  # insertion
        assert 'best' in names   # substitution
        assert 'est' in names    # deletion

    def test_levenshtein_empty_string(self, reasoner):
        """LEVENSHTEIN with empty string should equal string length."""
        reasoner.add_triple('a', 'type', 'oo:Method')
        reasoner.add_triple('a', 'name', 'hello')

        result = reasoner.reql('''
            SELECT ?m ?name WHERE {
                ?m type oo:Method . ?m name ?name .
                FILTER(LEVENSHTEIN(?name, "") = 5)
            }
        ''')

        assert result.num_rows == 1
        assert result.column('?name').to_pylist()[0] == 'hello'


class TestLevenshteinWithVariables:
    """Tests for LEVENSHTEIN with two variable arguments."""

    def test_levenshtein_two_variables_distance_1(self, reasoner_with_methods):
        """Find pairs with edit distance exactly 1."""
        result = reasoner_with_methods.reql('''
            SELECT ?m1 ?name1 ?m2 ?name2 WHERE {
                ?m1 type oo:Method . ?m1 name ?name1 .
                ?m2 type oo:Method . ?m2 name ?name2 .
                FILTER(?m1 != ?m2)
                FILTER(LEVENSHTEIN(?name1, ?name2) = 1)
            }
        ''')

        # Should find pairs: getUserName<->getUserNames, getUserName<->setUserName, execute<->executes
        assert result.num_rows >= 4  # At least 2 pairs * 2 directions

        pairs = set()
        for i in range(result.num_rows):
            n1 = result.column('?name1').to_pylist()[i]
            n2 = result.column('?name2').to_pylist()[i]
            pairs.add((min(n1, n2), max(n1, n2)))

        assert ('getUserName', 'getUserNames') in pairs
        assert ('getUserName', 'setUserName') in pairs
        assert ('execute', 'executes') in pairs

    def test_levenshtein_two_variables_threshold(self, reasoner_with_methods):
        """Find pairs with edit distance <= 2."""
        result = reasoner_with_methods.reql('''
            SELECT ?m1 ?name1 ?m2 ?name2 WHERE {
                ?m1 type oo:Method . ?m1 name ?name1 .
                ?m2 type oo:Method . ?m2 name ?name2 .
                FILTER(?m1 != ?m2)
                FILTER(LEVENSHTEIN(?name1, ?name2) <= 2)
            }
        ''')

        # With distance <= 2, should include getUserNames<->setUserName (distance 2)
        pairs = set()
        for i in range(result.num_rows):
            n1 = result.column('?name1').to_pylist()[i]
            n2 = result.column('?name2').to_pylist()[i]
            pairs.add((min(n1, n2), max(n1, n2)))

        assert ('getUserNames', 'setUserName') in pairs

    def test_levenshtein_excludes_distant_pairs(self, reasoner_with_methods):
        """Verify distant pairs are excluded."""
        result = reasoner_with_methods.reql('''
            SELECT ?m1 ?name1 ?m2 ?name2 WHERE {
                ?m1 type oo:Method . ?m1 name ?name1 .
                ?m2 type oo:Method . ?m2 name ?name2 .
                FILTER(?m1 != ?m2)
                FILTER(LEVENSHTEIN(?name1, ?name2) <= 3)
            }
        ''')

        pairs = set()
        for i in range(result.num_rows):
            n1 = result.column('?name1').to_pylist()[i]
            n2 = result.column('?name2').to_pylist()[i]
            pairs.add((min(n1, n2), max(n1, n2)))

        # deleteUser and run should not be paired with anything (too distant)
        for p in pairs:
            assert 'deleteUser' not in p or p == ('deleteUser', 'deleteUser')
            assert 'run' not in p or p == ('run', 'run')


class TestLevenshteinWithLiteral:
    """Tests for LEVENSHTEIN with one variable and one literal."""

    def test_levenshtein_find_similar_to_literal(self, reasoner_with_methods):
        """Find methods similar to a literal string."""
        result = reasoner_with_methods.reql('''
            SELECT ?m ?name WHERE {
                ?m type oo:Method . ?m name ?name .
                FILTER(LEVENSHTEIN(?name, "execute") <= 1)
            }
        ''')

        names = result.column('?name').to_pylist()
        assert 'execute' in names   # distance 0
        assert 'executes' in names  # distance 1
        assert 'run' not in names   # distance 7

    def test_levenshtein_find_typos(self, reasoner):
        """Use LEVENSHTEIN to find potential typos."""
        # Simulate a codebase with a typo
        reasoner.add_triple('c1', 'type', 'oo:Class')
        reasoner.add_triple('c1', 'name', 'UserService')
        reasoner.add_triple('c2', 'type', 'oo:Class')
        reasoner.add_triple('c2', 'name', 'UserSrevice')  # typo: Srevice
        reasoner.add_triple('c3', 'type', 'oo:Class')
        reasoner.add_triple('c3', 'name', 'OrderService')

        result = reasoner.reql('''
            SELECT ?c ?name WHERE {
                ?c type oo:Class . ?c name ?name .
                FILTER(LEVENSHTEIN(?name, "UserService") <= 2)
                FILTER(?name != "UserService")
            }
        ''')

        names = result.column('?name').to_pylist()
        assert 'UserSrevice' in names  # typo found
        assert 'OrderService' not in names  # too different


class TestLevenshteinComparisons:
    """Tests for LEVENSHTEIN with different comparison operators."""

    def test_levenshtein_less_than(self, reasoner):
        """Test LEVENSHTEIN with < operator."""
        reasoner.add_triple('a', 'type', 'oo:Method')
        reasoner.add_triple('a', 'name', 'abc')
        reasoner.add_triple('b', 'type', 'oo:Method')
        reasoner.add_triple('b', 'name', 'abcd')  # distance 1
        reasoner.add_triple('c', 'type', 'oo:Method')
        reasoner.add_triple('c', 'name', 'abcde')  # distance 2

        result = reasoner.reql('''
            SELECT ?m ?name WHERE {
                ?m type oo:Method . ?m name ?name .
                FILTER(LEVENSHTEIN(?name, "abc") < 2)
            }
        ''')

        names = result.column('?name').to_pylist()
        assert 'abc' in names    # distance 0
        assert 'abcd' in names   # distance 1
        assert 'abcde' not in names  # distance 2, excluded by < 2

    def test_levenshtein_greater_than(self, reasoner):
        """Test LEVENSHTEIN with > operator."""
        reasoner.add_triple('a', 'type', 'oo:Method')
        reasoner.add_triple('a', 'name', 'abc')
        reasoner.add_triple('b', 'type', 'oo:Method')
        reasoner.add_triple('b', 'name', 'xyz')  # distance 3

        result = reasoner.reql('''
            SELECT ?m ?name WHERE {
                ?m type oo:Method . ?m name ?name .
                FILTER(LEVENSHTEIN(?name, "abc") > 2)
            }
        ''')

        names = result.column('?name').to_pylist()
        assert 'abc' not in names  # distance 0
        assert 'xyz' in names      # distance 3

    def test_levenshtein_equals(self, reasoner):
        """Test LEVENSHTEIN with = operator."""
        reasoner.add_triple('a', 'type', 'oo:Method')
        reasoner.add_triple('a', 'name', 'cat')
        reasoner.add_triple('b', 'type', 'oo:Method')
        reasoner.add_triple('b', 'name', 'car')  # distance 1
        reasoner.add_triple('c', 'type', 'oo:Method')
        reasoner.add_triple('c', 'name', 'cap')  # distance 1
        reasoner.add_triple('d', 'type', 'oo:Method')
        reasoner.add_triple('d', 'name', 'dog')  # distance 3

        result = reasoner.reql('''
            SELECT ?m ?name WHERE {
                ?m type oo:Method . ?m name ?name .
                FILTER(LEVENSHTEIN(?name, "cat") = 1)
            }
            ORDER BY ?name
        ''')

        names = result.column('?name').to_pylist()
        assert names == ['cap', 'car']


class TestLevenshteinEdgeCases:
    """Edge case tests for LEVENSHTEIN."""

    def test_levenshtein_case_sensitive(self, reasoner):
        """LEVENSHTEIN should be case-sensitive."""
        reasoner.add_triple('a', 'type', 'oo:Method')
        reasoner.add_triple('a', 'name', 'Test')
        reasoner.add_triple('b', 'type', 'oo:Method')
        reasoner.add_triple('b', 'name', 'test')

        result = reasoner.reql('''
            SELECT ?m ?name WHERE {
                ?m type oo:Method . ?m name ?name .
                FILTER(LEVENSHTEIN(?name, "Test") = 0)
            }
        ''')

        names = result.column('?name').to_pylist()
        assert names == ['Test']  # Only exact match, not 'test'

    def test_levenshtein_special_characters(self, reasoner):
        """LEVENSHTEIN should handle special characters."""
        reasoner.add_triple('a', 'type', 'oo:Method')
        reasoner.add_triple('a', 'name', '__init__')
        reasoner.add_triple('b', 'type', 'oo:Method')
        reasoner.add_triple('b', 'name', '__init')

        result = reasoner.reql('''
            SELECT ?m ?name WHERE {
                ?m type oo:Method . ?m name ?name .
                FILTER(LEVENSHTEIN(?name, "__init__") <= 2)
            }
        ''')

        names = result.column('?name').to_pylist()
        assert '__init__' in names
        assert '__init' in names  # distance 2

    def test_levenshtein_unicode(self, reasoner):
        """LEVENSHTEIN should handle unicode strings."""
        reasoner.add_triple('a', 'type', 'oo:Method')
        reasoner.add_triple('a', 'name', 'cafe')
        reasoner.add_triple('b', 'type', 'oo:Method')
        reasoner.add_triple('b', 'name', 'cafe')  # with accent would be different

        result = reasoner.reql('''
            SELECT ?m ?name WHERE {
                ?m type oo:Method . ?m name ?name .
                FILTER(LEVENSHTEIN(?name, "cafe") = 0)
            }
        ''')

        assert result.num_rows >= 1

    def test_levenshtein_no_matches(self, reasoner):
        """LEVENSHTEIN should return empty when no matches."""
        reasoner.add_triple('a', 'type', 'oo:Method')
        reasoner.add_triple('a', 'name', 'completely_different')

        result = reasoner.reql('''
            SELECT ?m ?name WHERE {
                ?m type oo:Method . ?m name ?name .
                FILTER(LEVENSHTEIN(?name, "xyz") <= 2)
            }
        ''')

        assert result.num_rows == 0


class TestLevenshteinPerformance:
    """Performance-related tests for LEVENSHTEIN."""

    def test_levenshtein_with_limit(self, reasoner):
        """LEVENSHTEIN should work with LIMIT."""
        for i in range(10):
            reasoner.add_triple(f'm{i}', 'type', 'oo:Method')
            reasoner.add_triple(f'm{i}', 'name', f'method{i}')

        result = reasoner.reql('''
            SELECT ?m ?name WHERE {
                ?m type oo:Method . ?m name ?name .
                FILTER(LEVENSHTEIN(?name, "method0") <= 1)
            }
            LIMIT 5
        ''')

        assert result.num_rows <= 5

    def test_levenshtein_with_order_by(self, reasoner):
        """LEVENSHTEIN should work with ORDER BY."""
        reasoner.add_triple('a', 'type', 'oo:Method')
        reasoner.add_triple('a', 'name', 'zzz')
        reasoner.add_triple('b', 'type', 'oo:Method')
        reasoner.add_triple('b', 'name', 'aaa')
        reasoner.add_triple('c', 'type', 'oo:Method')
        reasoner.add_triple('c', 'name', 'mmm')

        result = reasoner.reql('''
            SELECT ?m ?name WHERE {
                ?m type oo:Method . ?m name ?name .
                FILTER(LEVENSHTEIN(?name, "aaa") <= 10)
            }
            ORDER BY ?name
        ''')

        names = result.column('?name').to_pylist()
        assert names == ['aaa', 'mmm', 'zzz']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
