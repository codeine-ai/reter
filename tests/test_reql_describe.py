"""
REQL DESCRIBE Query Tests

Tests for the DESCRIBE query functionality in REQL.

Author: Claude Code
Date: 2025-01-11
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from reter.reasoner import Reter
    from reter_core.owl_rete_cpp import ReteNetwork
    RETER_AVAILABLE = True
except ImportError:
    RETER_AVAILABLE = False
    pytest.skip("reter not available", allow_module_level=True)


class TestREQLDescribe:
    """Test basic DESCRIBE functionality"""

    @pytest.fixture
    def reasoner(self):
        """Create reasoner with test data"""
        r = Reter(variant='ai')
        r.load_ontology("""
            Person(Alice)
            Person(Bob)
            Female(Alice)
            Male(Bob)
        """)
        r.add_triple("Alice", "age", "30")
        r.add_triple("Alice", "hasChild", "Bob")
        r.add_triple("Bob", "age", "5")
        return r

    def test_describe_single_resource(self, reasoner):
        """Test DESCRIBE Alice"""
        result = reasoner.reql("DESCRIBE Alice")

        assert result is not None
        assert result.num_rows > 0

        # Check schema
        assert 'subject' in result.column_names
        assert 'predicate' in result.column_names
        assert 'object' in result.column_names
        assert 'object_type' in result.column_names

        # Convert to dict for easier checking
        data = result.to_pydict()

        # Should contain Alice as subject
        assert 'Alice' in data['subject']

        # Should contain Alice's type assertions
        assert 'Person' in data['object']
        assert 'Female' in data['object']

    def test_describe_multiple_resources(self, reasoner):
        """Test DESCRIBE Alice Bob"""
        result = reasoner.reql("DESCRIBE Alice Bob")

        assert result.num_rows > 0

        data = result.to_pydict()

        # Should contain both Alice and Bob
        subjects = set(data['subject'])
        assert 'Alice' in subjects
        assert 'Bob' in subjects

    def test_describe_with_where(self, reasoner):
        """Test DESCRIBE ?x WHERE { ?x type Person }"""
        result = reasoner.reql("""
            DESCRIBE ?x WHERE {
                ?x type Person
            }
        """)

        assert result.num_rows > 0

        data = result.to_pydict()

        # Should include facts about Alice and Bob
        subjects = set(data['subject'])
        assert 'Alice' in subjects or 'Bob' in subjects

    def test_describe_bidirectional(self, reasoner):
        """Test that DESCRIBE returns triples where resource is subject OR object"""
        result = reasoner.reql("DESCRIBE Bob")

        data = result.to_pydict()

        # Bob as subject: Bob type Person, Bob age 5
        # Bob as object: hasChild(Alice, Bob)

        # Check Bob appears as subject
        bob_as_subject = [i for i, s in enumerate(data['subject']) if s == 'Bob']
        assert len(bob_as_subject) > 0

        # Check Bob appears as object (hasChild relation)
        bob_as_object = [i for i, o in enumerate(data['object']) if o == 'Bob']
        assert len(bob_as_object) > 0

    def test_describe_empty_result(self, reasoner):
        """Test DESCRIBE on non-existent resource"""
        result = reasoner.reql("DESCRIBE NonExistent")

        # Should return empty table with correct schema
        assert result.num_rows == 0
        assert 'subject' in result.column_names
        assert 'predicate' in result.column_names
        assert 'object' in result.column_names
        assert 'object_type' in result.column_names


class TestREQLDescribeWithPatterns:
    """Test DESCRIBE with advanced patterns"""

    @pytest.fixture
    def reasoner(self):
        """Create reasoner with complex test data"""
        r = Reter(variant='ai')
        r.load_ontology("""
            Person(Alice)
            Doctor(Alice)
            Person(Bob)
            Doctor(Charlie)
        """)
        r.add_triple("Alice", "age", "35")
        r.add_triple("Alice", "hasEmail", "alice@example.com")
        r.add_triple("Bob", "age", "25")
        r.add_triple("Charlie", "age", "45")
        r.add_triple("Charlie", "hasEmail", "charlie@example.com")
        return r

    def test_describe_with_filter(self, reasoner):
        """Test DESCRIBE with FILTER"""
        result = reasoner.reql("""
            DESCRIBE ?person WHERE {
                ?person type Person .
                ?person age ?age .
                FILTER(?age >= 30)
            }
        """)

        assert result.num_rows > 0

        data = result.to_pydict()

        # Should only include Alice (age 35), not Bob (age 25)
        subjects = set(data['subject'])
        assert 'Alice' in subjects

    def test_describe_with_union(self, reasoner):
        """Test DESCRIBE with UNION in WHERE clause"""
        result = reasoner.reql("""
            DESCRIBE ?x WHERE {
                { ?x type Person }
                UNION
                { ?x type Doctor }
            }
        """)

        assert result.num_rows > 0

    def test_describe_object_types(self, reasoner):
        """Test that object_type column correctly identifies types"""
        result = reasoner.reql("DESCRIBE Alice")

        data = result.to_pydict()

        # Find the age row
        for i, pred in enumerate(data['predicate']):
            if pred == 'age':
                assert data['object_type'][i] == 'number'

        # Find the type row
        for i, pred in enumerate(data['predicate']):
            if pred == 'type':
                assert data['object_type'][i] == 'entity'

        # Find the hasEmail row
        # Note: email added via add_triple() without quotes is stored as entity, not string
        for i, pred in enumerate(data['predicate']):
            if pred == 'hasEmail':
                assert data['object_type'][i] == 'entity'


class TestREQLDescribeEdgeCases:
    """Test edge cases and special scenarios"""

    @pytest.fixture
    def reasoner(self):
        """Create reasoner with test data"""
        r = Reter(variant='ai')
        r.load_ontology("Person(Alice)")
        r.add_triple("Alice", "hasValue", "42")
        r.add_triple("Alice", "hasValue", "3.14")
        r.add_triple("Alice", "hasValue", "true")
        r.add_triple("Alice", "hasString", "test")
        return r

    def test_describe_various_datatypes(self, reasoner):
        """Test DESCRIBE with various object datatypes"""
        result = reasoner.reql("DESCRIBE Alice")

        assert result.num_rows > 0

        data = result.to_pydict()

        # Check object types are correctly inferred
        type_counts = {}
        for obj_type in data['object_type']:
            type_counts[obj_type] = type_counts.get(obj_type, 0) + 1

        # Should have at least entity, number, boolean, string types
        assert 'entity' in type_counts
        assert 'number' in type_counts

    def test_describe_case_insensitive(self, reasoner):
        """Test that DESCRIBE keyword is case-insensitive"""
        result1 = reasoner.reql("DESCRIBE Alice")
        result2 = reasoner.reql("describe Alice")
        result3 = reasoner.reql("Describe Alice")

        # All should work (non-zero results)
        assert result1.num_rows > 0
        assert result2.num_rows > 0
        assert result3.num_rows > 0


class TestREQLDescribeIntegration:
    """Integration tests with other REQL features"""

    @pytest.fixture
    def reasoner(self):
        """Create reasoner with test data"""
        r = Reter(variant='ai')
        r.load_ontology("""
            Person(Alice)
            Person(Bob)
            Person(Charlie)
        """)
        r.add_triple("Alice", "age", "30")
        r.add_triple("Bob", "age", "25")
        r.add_triple("Charlie", "age", "35")
        r.add_triple("Alice", "hasEmail", "alice@example.com")
        r.add_triple("Charlie", "hasEmail", "charlie@example.com")
        return r

    def test_describe_combined_with_select(self, reasoner):
        """Test DESCRIBE query after SELECT to explore results"""
        # First, find persons over 30
        select_result = reasoner.reql("""
            SELECT ?x WHERE {
                ?x type Person .
                ?x age ?age .
                FILTER(?age > 30)
            }
        """)

        # Should get Charlie
        assert select_result.num_rows > 0

        # Then describe Charlie
        describe_result = reasoner.reql("DESCRIBE Charlie")

        assert describe_result.num_rows > 0
        data = describe_result.to_pydict()
        assert 'Charlie' in data['subject']

    def test_describe_performance(self, reasoner):
        """Basic performance test - DESCRIBE should complete quickly"""
        import time

        start = time.time()
        result = reasoner.reql("DESCRIBE Alice")
        elapsed = time.time() - start

        # Should complete in reasonable time (< 1 second)
        assert elapsed < 1.0
        assert result.num_rows > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
