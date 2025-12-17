"""
Python integration tests for REQL MINUS pattern support

Tests the MINUS graph pattern functionality (negation/set difference).
MINUS patterns should filter out rows that match the minus pattern.
"""

import pytest
from reter import Reter


def test_minus_basic():
    """Test basic MINUS pattern (negation)"""
    reter = Reter("ai")

    # Load test data: some persons have email, some don't
    reter.load_ontology("""
Person(Alice)
Person(Bob)
Person(Charlie)
hasEmail(Alice, 'alice@example.com')
hasEmail(Charlie, 'charlie@example.com')
    """, "test.minus.basic")

    # Query: persons WITHOUT email
    result = reter.reql("""
        SELECT ?person WHERE {
            ?person type Person .
            MINUS { ?person hasEmail ?email }
        }
    """)

    # Should return only Bob (person without email)
    assert result.num_rows == 1

    df = result.to_pandas()
    assert df['?person'].iloc[0] == 'Bob'


def test_minus_multiple_patterns():
    """Test MINUS with multiple conditions in the minus pattern"""
    reter = Reter("ai")

    # Load test data
    reter.load_ontology("""
Person(Alice)
Person(Bob)
Person(Charlie)
hasEmail(Alice, 'alice@example.com')
hasPhone(Alice, '555-1234')
hasEmail(Bob, 'bob@example.com')
hasPhone(Charlie, '555-5678')
    """, "test.minus.multiple")

    # Query: persons who DON'T have BOTH email AND phone
    result = reter.reql("""
        SELECT ?person WHERE {
            ?person type Person .
            MINUS {
                ?person hasEmail ?email .
                ?person hasPhone ?phone
            }
        }
    """)

    # Should return Bob and Charlie (Alice has both)
    assert result.num_rows == 2

    df = result.to_pandas()
    persons = set(df['?person'])
    assert persons == {'Bob', 'Charlie'}


def test_minus_with_filter():
    """Test MINUS combined with FILTER"""
    reter = Reter("ai")

    # Load test data
    reter.load_ontology("""
Person(Alice)
Person(Bob)
Person(Charlie)
Person(David)
age(Alice, 25)
age(Bob, 30)
age(Charlie, 18)
age(David, 35)
hasEmail(Bob, 'bob@example.com')
hasEmail(David, 'david@example.com')
    """, "test.minus.filter")

    # Query: adults (age > 21) without email
    result = reter.reql("""
        SELECT ?person ?age WHERE {
            ?person age ?age .
            FILTER(?age > 21)
            MINUS { ?person hasEmail ?email }
        }
    """)

    # Should return only Alice (adult without email)
    # Bob and David have emails, Charlie is not an adult
    assert result.num_rows == 1

    df = result.to_pandas()
    assert df['?person'].iloc[0] == 'Alice'
    assert int(df['?age'].iloc[0]) == 25


def test_minus_empty_result():
    """Test MINUS when all rows are filtered out"""
    reter = Reter("ai")

    # Load test data: all persons have emails
    reter.load_ontology("""
Person(Alice)
Person(Bob)
hasEmail(Alice, 'alice@example.com')
hasEmail(Bob, 'bob@example.com')
    """, "test.minus.empty")

    # Query: persons without email (should be empty)
    result = reter.reql("""
        SELECT ?person WHERE {
            ?person type Person .
            MINUS { ?person hasEmail ?email }
        }
    """)

    # Should return 0 results
    assert result.num_rows == 0


def test_minus_no_match():
    """Test MINUS when minus pattern never matches (returns all)"""
    reter = Reter("ai")

    # Load test data: no emails at all
    reter.load_ontology("""
Person(Alice)
Person(Bob)
    """, "test.minus.nomatch")

    # Query: persons without email
    result = reter.reql("""
        SELECT ?person WHERE {
            ?person type Person .
            MINUS { ?person hasEmail ?email }
        }
    """)

    # Should return all persons (no one has email to be filtered)
    assert result.num_rows == 2

    df = result.to_pandas()
    persons = set(df['?person'])
    assert persons == {'Alice', 'Bob'}


def test_minus_with_property_chain():
    """Test MINUS with property chains"""
    reter = Reter("ai")

    # Load test data
    reter.load_ontology("""
Person(Alice)
Person(Bob)
Person(Charlie)
Organization(ACME)
Organization(TechCorp)
worksAt(Alice, ACME)
worksAt(Bob, TechCorp)
hasCEO(ACME, Alice)
    """, "test.minus.chain")

    # Query: persons who work at an org that they don't lead
    result = reter.reql("""
        SELECT ?person WHERE {
            ?person worksAt ?org .
            MINUS {
                ?org hasCEO ?person
            }
        }
    """)

    # Should return only Bob (Alice is CEO of ACME)
    assert result.num_rows == 1

    df = result.to_pandas()
    assert df['?person'].iloc[0] == 'Bob'


def test_minus_order_by():
    """Test MINUS with ORDER BY"""
    reter = Reter("ai")

    # Load test data
    reter.load_ontology("""
Person(Alice)
Person(Bob)
Person(Charlie)
age(Alice, 30)
age(Bob, 25)
age(Charlie, 35)
hasEmail(Charlie, 'charlie@example.com')
    """, "test.minus.orderby")

    # Query: persons without email, ordered by age
    result = reter.reql("""
        SELECT ?person ?age WHERE {
            ?person age ?age .
            MINUS { ?person hasEmail ?email }
        }
        ORDER BY ?age
    """)

    # Should return Alice and Bob, ordered by age
    assert result.num_rows == 2

    df = result.to_pandas()

    # Should be ordered: Bob (25), Alice (30)
    ages = [int(age) for age in df['?age']]
    assert ages == [25, 30]

    persons = list(df['?person'])
    assert persons == ['Bob', 'Alice']


def test_minus_limit():
    """Test MINUS with LIMIT"""
    reter = Reter("ai")

    # Load test data
    reter.load_ontology("""
Person(Alice)
Person(Bob)
Person(Charlie)
hasEmail(Alice, 'alice@example.com')
    """, "test.minus.limit")

    # Query: persons without email, limited to 1
    result = reter.reql("""
        SELECT ?person WHERE {
            ?person type Person .
            MINUS { ?person hasEmail ?email }
        }
        LIMIT 1
    """)

    # Should return only 1 result (Bob or Charlie)
    assert result.num_rows == 1


def test_minus_distinct():
    """Test MINUS with DISTINCT"""
    reter = Reter("ai")

    # Load test data (with potential duplicates)
    reter.load_ontology("""
Person(Alice)
Person(Bob)
worksAt(Bob, ACME)
worksAt(Bob, TechCorp)
hasEmail(Alice, 'alice@example.com')
    """, "test.minus.distinct")

    # Query: persons without email (with DISTINCT)
    result = reter.reql("""
        SELECT DISTINCT ?person WHERE {
            ?person type Person .
            MINUS { ?person hasEmail ?email }
        }
    """)

    # Should return only Bob (once, even if he has multiple work relationships)
    assert result.num_rows == 1

    df = result.to_pandas()
    assert df['?person'].iloc[0] == 'Bob'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
