#!/usr/bin/env python3
"""
Test GROUP_CONCAT Aggregate Function in REQL

This test suite verifies:
1. Basic GROUP_CONCAT with GROUP BY
2. GROUP_CONCAT with DISTINCT modifier
3. GROUP_CONCAT with custom separator
4. GROUP_CONCAT without GROUP BY (global aggregation)
5. GROUP_CONCAT with multiple groups
6. GROUP_CONCAT combined with other aggregates (COUNT, SUM)
7. GROUP_CONCAT with empty groups
8. GROUP_CONCAT with alias (AS)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from reter import Reter


class TestGroupConcatBasic:
    """Test basic GROUP_CONCAT functionality"""

    def test_group_concat_with_group_by(self):
        """Test GROUP_CONCAT with GROUP BY clause"""
        reasoner = Reter()

        # Add test data: people with skills
        reasoner.add_triple("Alice", "hasSkill", "Python")
        reasoner.add_triple("Alice", "hasSkill", "Java")
        reasoner.add_triple("Alice", "hasSkill", "SQL")
        reasoner.add_triple("Bob", "hasSkill", "Python")
        reasoner.add_triple("Bob", "hasSkill", "JavaScript")
        reasoner.add_triple("Charlie", "hasSkill", "Python")

        query = """
        SELECT ?person (GROUP_CONCAT(?skill) AS ?skills)
        WHERE {
            ?person hasSkill ?skill .
        }
        GROUP BY ?person
        """

        results = reasoner.network.reql_query(query)

        assert results.num_rows == 3, f"Expected 3 groups, got {results.num_rows}"
        assert '?person' in results.schema.names
        assert '?skills' in results.schema.names

        # Convert to pandas for easier inspection
        df = results.to_pandas()
        alice_skills = df[df['?person'] == 'Alice']['?skills'].iloc[0]

        # Alice should have 3 skills concatenated
        assert 'Python' in alice_skills
        assert 'Java' in alice_skills
        assert 'SQL' in alice_skills

    def test_group_concat_distinct(self):
        """Test GROUP_CONCAT with DISTINCT modifier"""
        reasoner = Reter()

        # Add test data with duplicates
        reasoner.add_triple("Alice", "hasSkill", "Python")
        reasoner.add_triple("Alice", "hasSkill", "Python")  # Duplicate
        reasoner.add_triple("Alice", "hasSkill", "Java")
        reasoner.add_triple("Alice", "hasSkill", "Java")    # Duplicate

        query = """
        SELECT ?person (GROUP_CONCAT(DISTINCT ?skill) AS ?skills)
        WHERE {
            ?person hasSkill ?skill .
        }
        GROUP BY ?person
        """

        results = reasoner.network.reql_query(query)
        df = results.to_pandas()

        alice_skills = df[df['?person'] == 'Alice']['?skills'].iloc[0]

        # With DISTINCT, should only have unique values
        skill_list = alice_skills.split(',')
        assert len(skill_list) == 2, f"Expected 2 unique skills, got {len(skill_list)}: {skill_list}"

    def test_group_concat_custom_separator(self):
        """Test GROUP_CONCAT with custom separator"""
        reasoner = Reter()

        reasoner.add_triple("Alice", "hasSkill", "Python")
        reasoner.add_triple("Alice", "hasSkill", "Java")
        reasoner.add_triple("Alice", "hasSkill", "SQL")

        query = """
        SELECT ?person (GROUP_CONCAT(?skill; SEPARATOR=" | ") AS ?skills)
        WHERE {
            ?person hasSkill ?skill .
        }
        GROUP BY ?person
        """

        results = reasoner.network.reql_query(query)
        df = results.to_pandas()

        alice_skills = df[df['?person'] == 'Alice']['?skills'].iloc[0]

        # Should use custom separator
        assert ' | ' in alice_skills, f"Expected ' | ' separator, got: {alice_skills}"


class TestGroupConcatGlobal:
    """Test GROUP_CONCAT without GROUP BY (global aggregation)"""

    def test_group_concat_global(self):
        """Test GROUP_CONCAT without GROUP BY"""
        reasoner = Reter()

        reasoner.add_triple("Alice", "type", "Person")
        reasoner.add_triple("Bob", "type", "Person")
        reasoner.add_triple("Charlie", "type", "Person")

        query = """
        SELECT (GROUP_CONCAT(?person) AS ?all_people)
        WHERE {
            ?person type Person .
        }
        """

        results = reasoner.network.reql_query(query)

        assert results.num_rows == 1, f"Expected 1 row for global aggregation, got {results.num_rows}"

        df = results.to_pandas()
        all_people = df['?all_people'].iloc[0]

        assert 'Alice' in all_people
        assert 'Bob' in all_people
        assert 'Charlie' in all_people


class TestGroupConcatCombined:
    """Test GROUP_CONCAT combined with other aggregates"""

    def test_group_concat_with_count(self):
        """Test GROUP_CONCAT together with COUNT"""
        reasoner = Reter()

        reasoner.add_triple("Alice", "hasSkill", "Python")
        reasoner.add_triple("Alice", "hasSkill", "Java")
        reasoner.add_triple("Bob", "hasSkill", "Python")

        query = """
        SELECT ?person (COUNT(?skill) AS ?skill_count) (GROUP_CONCAT(?skill) AS ?skills)
        WHERE {
            ?person hasSkill ?skill .
        }
        GROUP BY ?person
        """

        results = reasoner.network.reql_query(query)
        df = results.to_pandas()

        alice_row = df[df['?person'] == 'Alice']
        assert alice_row['?skill_count'].iloc[0] == 2
        assert 'Python' in alice_row['?skills'].iloc[0]
        assert 'Java' in alice_row['?skills'].iloc[0]


class TestGroupConcatEdgeCases:
    """Test edge cases for GROUP_CONCAT"""

    def test_group_concat_empty_result(self):
        """Test GROUP_CONCAT with no matching results"""
        reasoner = Reter()

        reasoner.add_triple("Alice", "type", "Person")

        query = """
        SELECT ?person (GROUP_CONCAT(?skill) AS ?skills)
        WHERE {
            ?person hasSkill ?skill .
        }
        GROUP BY ?person
        """

        results = reasoner.network.reql_query(query)

        # Should return empty result set
        assert results.num_rows == 0

    def test_group_concat_single_value(self):
        """Test GROUP_CONCAT with single value per group"""
        reasoner = Reter()

        reasoner.add_triple("Alice", "hasSkill", "Python")
        reasoner.add_triple("Bob", "hasSkill", "Java")

        query = """
        SELECT ?person (GROUP_CONCAT(?skill) AS ?skills)
        WHERE {
            ?person hasSkill ?skill .
        }
        GROUP BY ?person
        """

        results = reasoner.network.reql_query(query)
        df = results.to_pandas()

        # Single value should have no separator
        alice_skills = df[df['?person'] == 'Alice']['?skills'].iloc[0]
        assert alice_skills == 'Python'
        assert ',' not in alice_skills


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
