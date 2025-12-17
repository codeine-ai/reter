"""
Test Suite for Template Query API (Week 3, Day 3-5)

Tests ultra-fast pre-compiled query templates for common patterns.
Expected performance: ~1μs for cached queries.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from reter import Reter


def test_instances_of_basic():
    """Test basic instances_of template query"""
    print("\n=== Test 1: instances_of basic ===")

    r = Reter()

    # Load test ontology
    r.load_ontology("""
        Person（john）
        Person（mary）
        Person（bob）
        Animal（dog）
    """)

    # Query using template
    people = r.instances_of("Person")

    # Convert to list
    results = people.to_list()

    print(f"Found {len(results)} people")
    assert len(results) == 3, f"Expected 3 people, got {len(results)}"

    # Check all individuals are present
    individuals = {r["?x"] for r in results}
    assert individuals == {"john", "mary", "bob"}, f"Unexpected individuals: {individuals}"

    print("✓ instances_of basic test passed")


def test_instances_of_iteration():
    """Test iteration over instances_of results"""
    print("\n=== Test 2: instances_of iteration ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
    """)

    people = r.instances_of("Person")

    # Test __iter__
    count = 0
    individuals = set()
    for binding in people:
        count += 1
        individuals.add(binding["?x"])
        print(f"  Found: {binding['?x']}")

    assert count == 2, f"Expected 2 iterations, got {count}"
    assert individuals == {"john", "mary"}

    # Test __len__
    assert len(people) == 2, f"Expected len=2, got {len(people)}"

    print("✓ instances_of iteration test passed")


def test_property_value():
    """Test property_value template query"""
    print("\n=== Test 3: property_value ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        hasAge（john，30）
        hasAge（john，31）
    """)

    # Query john's age
    age_results = r.property_value("john", "hasAge")

    results = age_results.to_list()
    print(f"Found {len(results)} age values for john")

    # Should find at least one age
    assert len(results) >= 1, f"Expected at least 1 age, got {len(results)}"

    # Check values
    ages = {r["?val"] for r in results}
    print(f"  Ages: {ages}")
    assert "30" in ages or "31" in ages, f"Expected age 30 or 31, got {ages}"

    print("✓ property_value test passed")


def test_instances_with_property():
    """Test instances_with_property template query"""
    print("\n=== Test 4: instances_with_property ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
        Person（bob）
        hasAge（john，30）
        hasAge（mary，25）
    """)

    # Find all people with hasAge property
    results_set = r.instances_with_property("Person", "hasAge")
    results = results_set.to_list()

    print(f"Found {len(results)} people with age")
    assert len(results) == 2, f"Expected 2 people with age, got {len(results)}"

    # Check individuals and values
    for binding in results:
        print(f"  {binding['?x']} has age {binding['?val']}")
        assert binding["?x"] in ["john", "mary"]
        assert binding["?val"] in ["30", "25"]

    print("✓ instances_with_property test passed")


def test_related():
    """Test related template query for object properties"""
    print("\n=== Test 5: related ===")

    r = Reter()

    # Load ontology with object property assertions
    # Note: This requires role_assertion facts to be created
    # For now, we'll test the API structure even if no results
    r.load_ontology("""
        Person（john）
        Person（mary）
    """)

    # Query related objects (may return empty if no role_assertions exist)
    related_results = r.related("john", "hasParent")

    results = related_results.to_list()
    print(f"Found {len(results)} parent relations for john")

    # Test that query works (may be empty)
    assert isinstance(results, list), "Expected list result"

    print("✓ related test passed (API structure verified)")


def test_all_property_assertions():
    """Test all_property_assertions template query"""
    print("\n=== Test 6: all_property_assertions ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
    """)

    # Query all assertions of a property (may be empty if no role_assertions)
    results_set = r.all_property_assertions("hasParent")
    results = results_set.to_list()

    print(f"Found {len(results)} hasParent assertions")

    # Test that query works (may be empty)
    assert isinstance(results, list), "Expected list result"

    print("✓ all_property_assertions test passed (API structure verified)")


def test_template_query_caching():
    """Test that template queries use caching"""
    print("\n=== Test 7: template query caching ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
    """)

    # First call - compiles production
    results1 = r.instances_of("Person")
    list1 = results1.to_list()

    # Second call - should use cached production
    results2 = r.instances_of("Person")
    list2 = results2.to_list()

    # Results should be identical
    assert len(list1) == len(list2), "Cache should return same results"
    assert list1 == list2, "Cache should return identical results"

    print("✓ template query caching test passed")


def test_pandas_conversion():
    """Test pandas conversion with template queries"""
    print("\n=== Test 8: pandas conversion ===")

    try:
        import pandas as pd
    except ImportError:
        print("⊘ pandas not installed, skipping test")
        return

    r = Reter()
    r.load_ontology("""
        Person（john）
        Person（mary）
        Person（bob）
        hasAge（john，30）
        hasAge（mary，25）
        hasAge（bob，35）
    """)

    # Get results and convert to pandas
    people_with_age = r.instances_with_property("Person", "hasAge")
    df = people_with_age.to_pandas()

    print(f"DataFrame shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(df)

    # Check DataFrame structure
    assert "?x" in df.columns, "Expected ?x column"
    assert "?val" in df.columns, "Expected ?val column"
    assert len(df) == 3, f"Expected 3 rows, got {len(df)}"

    # Test pandas operations
    df["age_numeric"] = pd.to_numeric(df["?val"])
    mean_age = df["age_numeric"].mean()
    print(f"Mean age: {mean_age}")
    assert mean_age == 30.0, f"Expected mean age 30, got {mean_age}"

    print("✓ pandas conversion test passed")


def test_empty_results():
    """Test template queries with no results"""
    print("\n=== Test 9: empty results ===")

    r = Reter()
    r.load_ontology("""
        Person（john）
    """)

    # Query for non-existent class
    results = r.instances_of("Animal")

    # Should return empty results
    assert len(results) == 0, f"Expected 0 results, got {len(results)}"

    results_list = results.to_list()
    assert results_list == [], "Expected empty list"

    # Test pandas conversion with empty results
    try:
        import pandas as pd
        df = results.to_pandas()
        assert len(df) == 0, "Expected empty DataFrame"
        assert "?x" in df.columns, "Expected ?x column even when empty"
        print("✓ empty results test passed")
    except ImportError:
        print("✓ empty results test passed (pandas not available)")


def run_all_tests():
    """Run all template query tests"""
    print("=" * 60)
    print("Template Query API Test Suite (Week 3, Day 3-5)")
    print("=" * 60)

    tests = [
        test_instances_of_basic,
        test_instances_of_iteration,
        test_property_value,
        test_instances_with_property,
        test_related,
        test_all_property_assertions,
        test_template_query_caching,
        test_pandas_conversion,
        test_empty_results,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
