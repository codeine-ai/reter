"""
Test for OPTIONAL column preservation bug.

When OPTIONAL pattern has no matches for some rows, the optional columns
should still be present with NULL values, not missing entirely.
"""

import pytest
from reter_core import ReteNetwork


def test_optional_columns_many_facts():
    """Test OPTIONAL with many facts (like production snapshot)."""
    from reter import Reter

    reter = Reter("ai")

    # Add many oo:Class individuals to simulate production data
    ontology_parts = []
    num_classes = 1000  # Simulate a medium-sized codebase

    for i in range(num_classes):
        class_name = f"Class_{i:04d}"
        ontology_parts.append(f"oo:Class({class_name})")
        ontology_parts.append(f'name({class_name}, "{class_name}")')

        # Only 10% have parents
        if i % 10 == 0 and i > 0:
            parent_name = f"Class_{i-10:04d}"
            ontology_parts.append(f"inheritsFrom({class_name}, {parent_name})")

    reter.load_ontology("\n".join(ontology_parts), "test.many_facts")
    print(f"\nLoaded ontology with {num_classes} classes")

    # Query with OPTIONAL
    result = reter.reql("""
        SELECT ?class_name ?parent_name WHERE {
            ?class type oo:Class .
            ?class name ?class_name .
            OPTIONAL { ?class inheritsFrom ?parent . ?parent name ?parent_name }
        }
        LIMIT 20
    """)

    print(f"Columns: {result.column_names}")
    print(f"Rows: {result.num_rows}")
    for row in result.to_pylist()[:10]:
        print(f"  {row}")

    # Both columns should be present
    assert '?class_name' in result.column_names, "?class_name should be in columns"
    assert '?parent_name' in result.column_names, "?parent_name should be in columns (even if NULL)"


def test_optional_after_save_load():
    """Test that OPTIONAL works correctly after save/load cycle.

    This is the core bug: OPTIONAL works with fresh data but fails after
    serialization/deserialization.
    """
    from reter import Reter
    import tempfile
    import os

    reter = Reter('ai')
    reter.load_ontology('''
Class(Animal)
Class(Dog)
Class(Person)
inheritsFrom(Dog, Animal)
name(Animal, "Animal")
name(Dog, "Dog")
name(Person, "Person")
    ''', 'test')

    # Save to temp file
    snapshot_path = tempfile.mktemp(suffix='.reter')
    reter.network.save(snapshot_path)

    # Load into new network
    reter2 = ReteNetwork()
    reter2.load(snapshot_path)

    # Test OPTIONAL
    result = reter2.reql_query('''
        SELECT ?class_name ?parent_name WHERE {
            ?class type Class .
            ?class name ?class_name .
            OPTIONAL { ?class inheritsFrom ?parent . ?parent name ?parent_name }
        }
    ''', 30000)

    print(f"\nAfter save/load OPTIONAL query:")
    print(f"  Columns: {result.column_names}")
    for row in result.to_pylist():
        print(f"  {row}")

    os.remove(snapshot_path)

    # Both columns should be present
    assert '?class_name' in result.column_names, "?class_name should be in columns"
    assert '?parent_name' in result.column_names, "?parent_name should be in columns (BUG: missing after save/load)"


def test_optional_columns_present_from_snapshot():
    """Test that OPTIONAL columns are preserved when loading from snapshot."""
    import os
    snapshot_path = 'D:/ROOT/reter_root/.reter_code/.default.reter'

    if not os.path.exists(snapshot_path):
        pytest.skip("Snapshot file not found")

    reter = ReteNetwork()
    reter.load(snapshot_path)
    print(f"\nLoaded snapshot with {reter.fact_count()} facts")

    # First verify inheritance exists
    result_no_opt = reter.reql_query("""
        SELECT ?class ?parent WHERE {
            ?class type oo:Class .
            ?class inheritsFrom ?parent
        }
        LIMIT 5
    """, 30000)

    print("\nWithout OPTIONAL:")
    print(f"  Columns: {result_no_opt.column_names}")
    print(f"  Rows: {result_no_opt.num_rows}")
    for row in result_no_opt.to_pylist():
        print(f"  {row}")

    assert result_no_opt.num_rows > 0, "Should have some classes with inheritance"

    # Now test with OPTIONAL
    result_with_opt = reter.reql_query("""
        SELECT ?class_name ?parent_name WHERE {
            ?class type oo:Class .
            ?class name ?class_name .
            OPTIONAL { ?class inheritsFrom ?parent . ?parent name ?parent_name }
        }
        LIMIT 10
    """, 30000)

    print("\nWith OPTIONAL:")
    print(f"  Columns: {result_with_opt.column_names}")
    print(f"  Rows: {result_with_opt.num_rows}")
    for row in result_with_opt.to_pylist():
        print(f"  {row}")

    # The key assertion: both columns should be present
    assert '?class_name' in result_with_opt.column_names, "?class_name should be in columns"
    assert '?parent_name' in result_with_opt.column_names, "?parent_name should be in columns (even if NULL)"


def test_optional_columns_with_fresh_data():
    """Test OPTIONAL with fresh ontology data (no snapshot)."""
    from reter import Reter

    reter = Reter("ai")
    reter.load_ontology("""
oo:Class(Animal)
oo:Class(Dog)
oo:Class(Person)
inheritsFrom(Dog, Animal)
name(Animal, "Animal")
name(Dog, "Dog")
name(Person, "Person")
    """, "test")

    result = reter.reql("""
        SELECT ?class_name ?parent_name WHERE {
            ?class type oo:Class .
            ?class name ?class_name .
            OPTIONAL { ?class inheritsFrom ?parent . ?parent name ?parent_name }
        }
    """)

    print("\nFresh ontology with OPTIONAL:")
    print(f"  Columns: {result.column_names}")
    df = result.to_pandas()
    print(df)

    # Both columns should be present
    assert '?class_name' in result.column_names
    assert '?parent_name' in result.column_names

    # Should have 3 rows (Animal, Dog, Person)
    assert result.num_rows == 3

    # Dog should have parent, Animal and Person should have None
    for row in result.to_pylist():
        if row['?class_name'] == 'Dog':
            assert row['?parent_name'] == 'Animal'
        else:
            assert row['?parent_name'] is None


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
