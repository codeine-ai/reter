"""
Test for C++ bug: GROUP BY OPTIONAL variable + aggregate causes failure

BUG DESCRIPTION:
When using GROUP BY on a variable that comes from an OPTIONAL pattern,
combined with an aggregate function (COUNT, SUM, etc.), the C++ RETER
engine fails with "list index out of range" or similar errors during
ORDER BY processing.

ROOT CAUSE (hypothesis):
The Arrow table's group_by operation doesn't properly handle NULL values
in the grouping columns. When OPTIONAL patterns introduce NULLs, the
aggregation produces a corrupted result table that causes index errors
in subsequent operations like ORDER BY.

WORKAROUND:
Don't GROUP BY variables that come from OPTIONAL patterns. Either:
1. Move the OPTIONAL variable to an aggregate function instead
2. Use a required pattern instead of OPTIONAL
3. Restructure the query to avoid GROUP BY on nullable columns

AFFECTED TOOLS:
- get_complexity (fixed by removing line_count from GROUP BY)
- inline_method (crashes - uses OPTIONAL caller + GROUP BY)
- introduce_parameter_object (crashes - similar pattern)
- duplicate_parameter_lists (crashes - similar pattern)

Created: 2025-12-26
"""

import pytest
from reter import Reter


class TestGroupByOptionalAggregateBug:
    """Tests for GROUP BY OPTIONAL + aggregate bug."""

    @pytest.fixture
    def reter_with_data(self):
        """Create a Reter instance with test data."""
        reter = Reter("ai")

        # Load test data: some persons have optional properties
        reter.load_ontology("""
Person(Alice)
Person(Bob)
Person(Charlie)
Person(David)
Person(Eve)

# Department assignment (required)
department(Alice, Engineering)
department(Bob, Engineering)
department(Charlie, Sales)
department(David, Sales)
department(Eve, Marketing)

# Age (optional - not everyone has it)
age(Alice, 30)
age(Bob, 25)
age(Charlie, 35)
# David and Eve have no age

# Salary (optional - not everyone has it)
salary(Alice, 100000)
salary(Charlie, 80000)
salary(Eve, 90000)
# Bob and David have no salary
        """, "test.groupby.optional")

        return reter

    def test_groupby_required_var_no_aggregate(self, reter_with_data):
        """Test GROUP BY required variable without aggregate - WORKS"""
        reter = reter_with_data

        result = reter.reql("""
            SELECT ?dept ?person WHERE {
                ?person type Person .
                ?person department ?dept .
            }
            GROUP BY ?dept ?person
        """)

        assert result.num_rows == 5

    def test_groupby_required_var_with_aggregate(self, reter_with_data):
        """Test GROUP BY required variable with aggregate - WORKS"""
        reter = reter_with_data

        result = reter.reql("""
            SELECT ?dept (COUNT(?person) AS ?count) WHERE {
                ?person type Person .
                ?person department ?dept .
            }
            GROUP BY ?dept
            ORDER BY DESC(?count)
        """)

        df = result.to_pandas()
        assert result.num_rows == 3  # 3 departments

        # Engineering and Sales each have 2, Marketing has 1
        counts = list(df['?count'])
        assert sorted(counts, reverse=True) == [2, 2, 1]

    def test_groupby_optional_var_no_aggregate(self, reter_with_data):
        """Test GROUP BY OPTIONAL variable without aggregate - WORKS"""
        reter = reter_with_data

        result = reter.reql("""
            SELECT ?person ?age WHERE {
                ?person type Person .
                OPTIONAL { ?person age ?age }
            }
            GROUP BY ?person ?age
        """)

        # All 5 persons returned
        assert result.num_rows == 5

    @pytest.mark.xfail(
        reason="BUG: GROUP BY OPTIONAL var + aggregate causes C++ engine failure",
        raises=Exception,
        strict=False  # May fail or pass depending on data size
    )
    def test_groupby_optional_var_with_aggregate_bug(self, reter_with_data):
        """Test GROUP BY OPTIONAL variable with aggregate - BUG: FAILS

        This test demonstrates the bug. When:
        1. An OPTIONAL pattern introduces a variable with NULL values
        2. That variable is used in GROUP BY
        3. An aggregate function is also used

        The result is a corrupted Arrow table that causes errors.
        """
        reter = reter_with_data

        # This query uses OPTIONAL age in GROUP BY with COUNT aggregate
        # It should work but fails with "list index out of range"
        result = reter.reql("""
            SELECT ?age (COUNT(?person) AS ?count) WHERE {
                ?person type Person .
                OPTIONAL { ?person age ?age }
            }
            GROUP BY ?age
            ORDER BY DESC(?count)
        """)

        # If the bug is fixed, we should get results:
        # - age NULL: 2 persons (David, Eve)
        # - age 25: 1 person (Bob)
        # - age 30: 1 person (Alice)
        # - age 35: 1 person (Charlie)
        df = result.to_pandas()
        assert result.num_rows >= 3

    @pytest.mark.xfail(
        reason="BUG: GROUP BY OPTIONAL var + aggregate causes C++ engine failure",
        raises=Exception,
        strict=False
    )
    def test_groupby_multiple_optional_vars_with_aggregate(self, reter_with_data):
        """Test GROUP BY multiple OPTIONAL variables with aggregate - BUG: FAILS

        This is an even more problematic case with multiple OPTIONAL vars.
        """
        reter = reter_with_data

        result = reter.reql("""
            SELECT ?age ?salary (COUNT(?person) AS ?count) WHERE {
                ?person type Person .
                OPTIONAL { ?person age ?age }
                OPTIONAL { ?person salary ?salary }
            }
            GROUP BY ?age ?salary
            ORDER BY ?age ?salary
        """)

        df = result.to_pandas()
        assert result.num_rows > 0


class TestGroupByOptionalWorkarounds:
    """Demonstrate workarounds for the GROUP BY OPTIONAL + aggregate bug."""

    @pytest.fixture
    def reter_with_data(self):
        """Create a Reter instance with test data."""
        reter = Reter("ai")

        reter.load_ontology("""
Person(Alice)
Person(Bob)
Person(Charlie)

age(Alice, 30)
age(Bob, 25)
# Charlie has no age
        """, "test.workaround")

        return reter

    def test_workaround_aggregate_the_optional(self, reter_with_data):
        """WORKAROUND: Move OPTIONAL var to aggregate, not GROUP BY"""
        reter = reter_with_data

        # Instead of GROUP BY ?optional_var (COUNT(...))
        # Use GROUP BY required_var (AVG(?optional_var))
        result = reter.reql("""
            SELECT ?person (COUNT(?person) AS ?exists) WHERE {
                ?person type Person .
                OPTIONAL { ?person age ?age }
            }
            GROUP BY ?person
        """)

        # This works because we're not grouping by the optional var
        assert result.num_rows == 3

    def test_workaround_filter_nulls_first(self, reter_with_data):
        """WORKAROUND: Filter out NULL values before aggregation"""
        reter = reter_with_data

        # Use required pattern instead of OPTIONAL
        result = reter.reql("""
            SELECT ?age (COUNT(?person) AS ?count) WHERE {
                ?person type Person .
                ?person age ?age .
            }
            GROUP BY ?age
            ORDER BY DESC(?count)
        """)

        # This works but excludes persons without age
        df = result.to_pandas()
        assert result.num_rows == 2  # Only ages 25 and 30

    def test_workaround_separate_queries(self, reter_with_data):
        """WORKAROUND: Run separate queries and combine results"""
        reter = reter_with_data

        # Query 1: Get persons with age
        with_age = reter.reql("""
            SELECT ?person ?age WHERE {
                ?person type Person .
                ?person age ?age .
            }
        """)

        # Query 2: Get all persons
        all_persons = reter.reql("""
            SELECT ?person WHERE {
                ?person type Person .
            }
        """)

        # Combine in Python
        df_age = with_age.to_pandas()
        df_all = all_persons.to_pandas()

        all_names = set(df_all['?person'])
        with_age_names = set(df_age['?person'])
        without_age_names = all_names - with_age_names

        assert len(all_names) == 3
        assert len(with_age_names) == 2
        assert len(without_age_names) == 1
        assert 'Charlie' in without_age_names


class TestReproduceCrashPattern:
    """Reproduce the exact patterns that crash the RETER C++ engine.

    WARNING: These tests cause C++ segfaults and are skipped by default.
    Run with: pytest --run-crash-tests to execute them.
    """

    @pytest.fixture
    def reter_with_methods(self):
        """Create a Reter instance with method data similar to inline_method query."""
        reter = Reter("ai")

        reter.load_ontology("""
Method(m1)
Method(m2)
Method(m3)
Method(m4)
Method(m5)

name(m1, 'helper1')
name(m2, 'helper2')
name(m3, 'process')
name(m4, 'main')
name(m5, 'unused')

lineCount(m1, 5)
lineCount(m2, 10)
lineCount(m3, 20)
# m4 and m5 have no lineCount (simulates OPTIONAL)

# Call relationships
calls(m3, m1)
calls(m3, m2)
calls(m4, m3)
calls(m4, m1)
# m2 has 1 caller (m3)
# m1 has 2 callers (m3, m4)
# m5 has 0 callers
        """, "test.crash.pattern")

        return reter

    # @pytest.mark.skip(reason="CRASH: Causes C++ segfault - run with --run-crash-tests")
    def test_crash_pattern_optional_groupby_count(self, reter_with_methods):
        """Reproduce inline_method crash pattern: OPTIONAL + GROUP BY + COUNT

        Original inline_method query:
        SELECT ?m ?name ?class_name ?file ?line ?line_count (COUNT(?caller) AS ?caller_count)
        WHERE {
            ?m type {Method} .
            ...
            OPTIONAL { ?caller calls ?m }
        }
        GROUP BY ?m ?name ?class_name ?file ?line ?line_count
        HAVING (?line_count <= {max_lines} && ?caller_count <= {max_callers})

        The crash occurs because:
        1. OPTIONAL { ?caller calls ?m } produces NULL for ?caller when no callers exist
        2. COUNT(?caller) aggregates over these NULLs
        3. The resulting table has corrupted indices
        """
        reter = reter_with_methods

        result = reter.reql("""
            SELECT ?m ?name ?line_count (COUNT(?caller) AS ?caller_count)
            WHERE {
                ?m type Method .
                ?m name ?name .
                OPTIONAL { ?m lineCount ?line_count }
                OPTIONAL { ?caller calls ?m }
            }
            GROUP BY ?m ?name ?line_count
            ORDER BY ?caller_count
        """)

        df = result.to_pandas()
        assert result.num_rows == 5

    # @pytest.mark.skip(reason="CRASH: Causes C++ segfault - run with --run-crash-tests")
    def test_crash_pattern_minimal(self, reter_with_methods):
        """Minimal reproduction of the crash pattern."""
        reter = reter_with_methods

        # Minimal case: OPTIONAL var in GROUP BY + any COUNT
        result = reter.reql("""
            SELECT ?m ?line_count (COUNT(?m) AS ?cnt)
            WHERE {
                ?m type Method .
                OPTIONAL { ?m lineCount ?line_count }
            }
            GROUP BY ?m ?line_count
            ORDER BY ?cnt
        """)

        df = result.to_pandas()
        assert result.num_rows == 5


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
