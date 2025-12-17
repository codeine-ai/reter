"""
Test PyArrow aggregation functionality with RETE query results

This test suite verifies:
1. Basic aggregation (no GROUP BY)
2. GROUP BY with single column
3. GROUP BY with multiple columns
4. Multiple aggregation functions
5. Integration with RETE query results
"""

import pyarrow as pa
from reter import Reter


def test_basic_aggregation_no_groupby():
    """Test 1: Simple aggregation without GROUP BY"""
    print("=" * 60)
    print("Test 1: Basic aggregation (no GROUP BY)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Person ⊑ᑦ owl:Thing
    Person（Alice）
    Person（Bob）
    Person（Charlie）
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Get all facts as Arrow table
    table = reasoner.get_all_facts()
    print(f"  Total facts: {table.num_rows}")

    # Simple aggregation: count all facts
    result = table.group_by([]).aggregate([
        ('type', 'count')
    ])

    print(f"  Total count: {result.to_pandas()}")
    assert result.num_rows == 1, "Should have 1 row for global aggregation"
    print("  ✓ Basic aggregation works\n")


def test_groupby_single_column():
    """Test 2: GROUP BY single column"""
    print("=" * 60)
    print("Test 2: GROUP BY single column")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Dog ⊑ᑦ Animal
    Cat ⊑ᑦ Animal
    Dog（Fido）
    Dog（Rex）
    Dog（Max）
    Cat（Whiskers）
    Cat（Felix）
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Get instance_of facts
    table = reasoner.network.query({'type': 'instance_of'})
    print(f"  Instance facts: {table.num_rows}")

    # Group by concept and count
    result = table.group_by(['concept']).aggregate([
        ('individual', 'count')
    ])

    df = result.to_pandas()
    print(f"\n  Grouped by concept:")
    print(df)

    # Verify we have groups for Dog and Cat
    assert len(df) >= 2, "Should have at least 2 concept groups"
    print("  ✓ GROUP BY single column works\n")


def test_groupby_multiple_aggregates():
    """Test 3: Multiple aggregation functions"""
    print("=" * 60)
    print("Test 3: Multiple aggregation functions")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Dog ⊑ᑦ Animal
    Cat ⊑ᑦ Animal
    Dog（Fido）
    Dog（Rex）
    Cat（Whiskers）
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Get all facts
    table = reasoner.get_all_facts()
    print(f"  Total facts: {table.num_rows}")

    # Group by type and apply multiple aggregations
    result = table.group_by(['type']).aggregate([
        ('concept', 'count'),
        ('individual', 'count')
    ])

    df = result.to_pandas()
    print(f"\n  Grouped by type:")
    print(df)

    assert len(df) > 0, "Should have aggregation results"
    print("  ✓ Multiple aggregations work\n")


def test_filter_then_aggregate():
    """Test 4: Filter query results then aggregate"""
    print("=" * 60)
    print("Test 4: Filter then aggregate")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Dog ⊑ᑦ Animal
    Cat ⊑ᑦ Animal
    Dog（Fido）
    Dog（Rex）
    Dog（Max）
    Cat（Whiskers）
    Cat（Felix）
    Cat（Tom）
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Query for Dog instances only
    table = reasoner.network.query({
        'type': 'instance_of',
        'concept': 'Dog'
    })
    print(f"  Dog instances: {table.num_rows}")

    # Count them
    result = table.group_by([]).aggregate([
        ('individual', 'count')
    ])

    count = result.to_pandas()['individual_count'][0]
    print(f"  Dog count: {count}")

    assert count == 3, "Should have 3 dogs"
    print("  ✓ Filter then aggregate works\n")


def test_complex_groupby():
    """Test 5: Complex GROUP BY with ontology reasoning"""
    print("=" * 60)
    print("Test 5: Complex GROUP BY scenario")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Mammal ⊑ᑦ Animal
    Dog ⊑ᑦ Mammal
    Cat ⊑ᑦ Mammal
    Dog（Fido）
    Dog（Rex）
    Cat（Whiskers）
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Get all subsumption facts
    table = reasoner.network.query({'type': 'subsumption'})
    print(f"  Subsumption facts: {table.num_rows}")

    if table.num_rows > 0:
        # Group by sub (subclass column is called 'sub')
        result = table.group_by(['sub']).aggregate([
            ('sup', 'count')
        ])

        df = result.to_pandas()
        print(f"\n  Subsumptions grouped by sub:")
        print(df)

        assert len(df) > 0, "Should have subsumption groups"
        print("  ✓ Complex GROUP BY works\n")
    else:
        print("  ⚠ No subsumption facts\n")


def test_aggregation_with_pandas_conversion():
    """Test 6: Aggregation results convert to pandas correctly"""
    print("=" * 60)
    print("Test 6: Pandas conversion")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Dog ⊑ᑦ Animal
    Dog（Fido）
    Dog（Rex）
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Get facts and aggregate
    table = reasoner.get_all_facts()
    result = table.group_by(['type']).aggregate([
        ('concept', 'count')
    ])

    # Convert to pandas
    df = result.to_pandas()
    print(f"  Result as pandas DataFrame:")
    print(df)
    print(f"  Shape: {df.shape}")
    print(f"  Columns: {list(df.columns)}")

    assert df.shape[0] > 0, "Should have rows"
    assert df.shape[1] >= 2, "Should have at least type and count columns"
    print("  ✓ Pandas conversion works\n")


def run_all_tests():
    """Run all aggregation tests"""
    print("\n" + "=" * 60)
    print("ARROW AGGREGATION TEST SUITE")
    print("=" * 60 + "\n")

    tests = [
        test_basic_aggregation_no_groupby,
        test_groupby_single_column,
        test_groupby_multiple_aggregates,
        test_filter_then_aggregate,
        test_complex_groupby,
        test_aggregation_with_pandas_conversion,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"  ✗ FAILED: {e}")
            import traceback
            traceback.print_exc()
            print()

    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed == 0:
        print("\n✅ ALL AGGREGATION TESTS PASSED!")
    else:
        print(f"\n❌ {failed} test(s) failed")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
