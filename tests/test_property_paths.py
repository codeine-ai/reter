"""
Test Suite for Property Path Support (Week 5, Day 6-7)

Tests transitive relationship queries using property paths (e.g., hasParent*).
Expected behavior: Finds all reachable nodes through transitive closure.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from reter import Reter


def test_property_path_basic():
    """Test basic transitive property path"""
    print("\n=== Test 1: Basic property path ===")

    r = Reter()
    r.load_ontology("""
        Person（alice）
        Person（bob）
        Person（charlie）
        hasParent（alice，bob）
        hasParent（bob，charlie）
    """)

    # Find all ancestors of alice (transitive)
    results = r.property_path("alice", "hasParent*", "?ancestor")
    result_list = results.to_list()

    print(f"Results: {len(result_list)} ancestors")
    for r in result_list:
        print(f"  {r}")

    # Should find bob (direct parent) and charlie (grandparent)
    assert len(result_list) >= 2, f"Expected at least 2 results, got {len(result_list)}"

    ancestors = {r["?ancestor"] for r in result_list}
    assert "bob" in ancestors, "Should find bob (direct parent)"
    assert "charlie" in ancestors, "Should find charlie (grandparent)"

    print("✓ Basic property path test passed")


def test_property_path_variable_start():
    """Test property path with variable as start"""
    print("\n=== Test 2: Property path with variable start ===")

    r = Reter()
    r.load_ontology("""
        Person（alice）
        Person（bob）
        Person（charlie）
        hasParent（alice，bob）
        hasParent（bob，charlie）
    """)

    # Find all (person, ancestor) pairs
    results = r.property_path("?person", "hasParent*", "?ancestor")
    result_list = results.to_list()

    print(f"Results: {len(result_list)} (person, ancestor) pairs")

    # Should find: (alice, bob), (alice, charlie), (bob, charlie)
    assert len(result_list) >= 3, f"Expected at least 3 results, got {len(result_list)}"

    pairs = {(r["?person"], r["?ancestor"]) for r in result_list}
    assert ("alice", "bob") in pairs
    assert ("alice", "charlie") in pairs
    assert ("bob", "charlie") in pairs

    print("✓ Variable start test passed")


def test_property_path_max_depth():
    """Test property path with max depth limit"""
    print("\n=== Test 3: Property path with max depth ===")

    r = Reter()
    r.load_ontology("""
        Person（a）
        Person（b）
        Person（c）
        Person（d）
        hasParent（a，b）
        hasParent（b，c）
        hasParent（c，d）
    """)

    # Find ancestors with max depth=1 (only direct parents)
    results = r.property_path("a", "hasParent*", "?ancestor", max_depth=1)
    result_list = results.to_list()

    print(f"Results: {len(result_list)} ancestors (max_depth=1)")

    # Should only find b (direct parent), not c or d
    assert len(result_list) == 1, f"Expected 1 result, got {len(result_list)}"
    assert result_list[0]["?ancestor"] == "b"

    # Now with max_depth=2 (parents and grandparents)
    results = r.property_path("a", "hasParent*", "?ancestor", max_depth=2)
    result_list = results.to_list()

    print(f"Results: {len(result_list)} ancestors (max_depth=2)")

    # Should find b and c, but not d
    assert len(result_list) == 2, f"Expected 2 results, got {len(result_list)}"
    ancestors = {r["?ancestor"] for r in result_list}
    assert ancestors == {"b", "c"}

    print("✓ Max depth test passed")


def test_property_path_cycle():
    """Test property path with cycles in graph"""
    print("\n=== Test 4: Property path with cycles ===")

    r = Reter()
    r.load_ontology("""
        Person（a）
        Person（b）
        Person（c）
        knows（a，b）
        knows（b，c）
        knows（c，a）
    """)

    # Find all people reachable from a via knows relationship
    # Should handle cycle gracefully
    results = r.property_path("a", "knows*", "?person")
    result_list = results.to_list()

    print(f"Results: {len(result_list)} reachable people")

    # Should find b and c (and possibly a itself)
    people = {r["?person"] for r in result_list}
    assert "b" in people
    assert "c" in people

    # Result count should be finite despite cycle
    assert len(result_list) <= 10, "Should not loop infinitely"

    print("✓ Cycle handling test passed")


def test_property_path_no_results():
    """Test property path with no transitive connections"""
    print("\n=== Test 5: Property path with no results ===")

    r = Reter()
    r.load_ontology("""
        Person（alice）
        Person（bob）
    """)

    # Alice has no parents
    results = r.property_path("alice", "hasParent*", "?ancestor")
    result_list = results.to_list()

    print(f"Results: {len(result_list)} ancestors")

    # Should return empty (or just alice if reflexive closure is included)
    assert len(result_list) == 0, f"Expected 0 results, got {len(result_list)}"

    print("✓ No results test passed")


def test_property_path_single_hop():
    """Test property path with single hop"""
    print("\n=== Test 6: Property path single hop ===")

    r = Reter()
    r.load_ontology("""
        Person（alice）
        Person（bob）
        hasParent（alice，bob）
    """)

    # Only one level of parent
    results = r.property_path("alice", "hasParent*", "?ancestor")
    result_list = results.to_list()

    print(f"Results: {len(result_list)} ancestors")

    assert len(result_list) == 1, f"Expected 1 result, got {len(result_list)}"
    assert result_list[0]["?ancestor"] == "bob"

    print("✓ Single hop test passed")


def test_property_path_branching():
    """Test property path with branching relationships"""
    print("\n=== Test 7: Property path with branching ===")

    r = Reter()
    r.load_ontology("""
        Person（alice）
        Person（bob）
        Person（charlie）
        Person（david）
        Person（eve）
        hasParent（alice，bob）
        hasParent（alice，charlie）
        hasParent（bob，david）
        hasParent（charlie，eve）
    """)

    # Alice has two parents, each with their own parents
    results = r.property_path("alice", "hasParent*", "?ancestor")
    result_list = results.to_list()

    print(f"Results: {len(result_list)} ancestors")

    # Should find all 4 ancestors: bob, charlie, david, eve
    assert len(result_list) >= 4, f"Expected at least 4 results, got {len(result_list)}"

    ancestors = {r["?ancestor"] for r in result_list}
    assert ancestors >= {"bob", "charlie", "david", "eve"}

    print("✓ Branching test passed")


def test_property_path_iteration():
    """Test iteration over property path results"""
    print("\n=== Test 8: Property path iteration ===")

    r = Reter()
    r.load_ontology("""
        Person（a）
        Person（b）
        Person（c）
        hasParent（a，b）
        hasParent（b，c）
    """)

    results = r.property_path("a", "hasParent*", "?ancestor")

    # Test __iter__
    count = 0
    ancestors = set()
    for binding in results:
        count += 1
        ancestors.add(binding["?ancestor"])
        print(f"  Found: {binding['?ancestor']}")

    assert count >= 2, f"Expected at least 2 iterations, got {count}"
    assert ancestors >= {"b", "c"}

    # Test __len__
    assert len(results) >= 2, f"Expected len>=2, got {len(results)}"

    print("✓ Iteration test passed")


def test_property_path_pandas():
    """Test pandas conversion with property paths"""
    print("\n=== Test 9: Property path with pandas ===")

    try:
        import pandas as pd
    except ImportError:
        print("⊘ pandas not installed, skipping test")
        return

    r = Reter()
    r.load_ontology("""
        Person（alice）
        Person（bob）
        Person（charlie）
        hasParent（alice，bob）
        hasParent（bob，charlie）
    """)

    results = r.property_path("alice", "hasParent*", "?ancestor")

    # Convert to pandas
    df = results.to_pandas()
    print(f"DataFrame shape: {df.shape}")
    print(df)

    assert "?ancestor" in df.columns
    assert len(df) >= 2

    ancestors = set(df["?ancestor"].values)
    assert ancestors >= {"bob", "charlie"}

    print("✓ Pandas test passed")


def test_property_path_deep_hierarchy():
    """Test property path with deep hierarchy"""
    print("\n=== Test 10: Property path with deep hierarchy ===")

    r = Reter()

    # Create a deep ancestor chain
    ontology = ["Person（person0）"]
    for i in range(1, 10):
        ontology.append(f"Person（person{i}）")
        ontology.append(f"hasParent（person{i-1}，person{i}）")

    r.load_ontology("\n".join(ontology))

    # Find all ancestors of person0 (should be person1 through person9)
    results = r.property_path("person0", "hasParent*", "?ancestor")
    result_list = results.to_list()

    print(f"Results: {len(result_list)} ancestors in deep hierarchy")

    # Should find 9 ancestors (person1 through person9)
    assert len(result_list) == 9, f"Expected 9 results, got {len(result_list)}"

    ancestors = {r["?ancestor"] for r in result_list}
    expected = {f"person{i}" for i in range(1, 10)}
    assert ancestors == expected, f"Expected {expected}, got {ancestors}"

    print("✓ Deep hierarchy test passed")


def run_all_tests():
    """Run all property path tests"""
    print("=" * 70)
    print("Property Path Support Test Suite (Week 5, Day 6-7)")
    print("=" * 70)

    tests = [
        test_property_path_basic,
        test_property_path_variable_start,
        test_property_path_max_depth,
        test_property_path_cycle,
        test_property_path_no_results,
        test_property_path_single_hop,
        test_property_path_branching,
        test_property_path_iteration,
        test_property_path_pandas,
        test_property_path_deep_hierarchy,
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

    print("\n" + "=" * 70)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
