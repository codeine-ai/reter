"""
Test Query Production Builder
Week 1, Day 3-4 of IMPLEMENTATION_PLAN.md
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'rete_cpp'))
from reter import owl_rete_cpp


def test_build_query_pattern():
    """Test building a query production"""
    network = owl_rete_cpp.ReteNetwork()

    # Add facts using DL notation
    network.load_ontology_from_string("""
        Person（john）
        Person（mary）
    """)

    # Build query: Find all persons
    conditions = [
        owl_rete_cpp.Condition("?f", "type", "instance_of"),
        owl_rete_cpp.Condition("?f", "concept", "Person"),
        owl_rete_cpp.Condition("?f", "individual", "?x")
    ]

    cache_key = "test_persons"
    production = network.build_query_pattern(cache_key, conditions)
    assert production is not None

    # Get results using cache_key
    tokens = network.get_query_results(cache_key)
    print(f"Found {len(tokens)} tokens")

    # Extract bindings using cache_key
    for i, token in enumerate(tokens):
        bindings = network.extract_bindings(cache_key, token)
        print(f"Token {i}: {bindings}")
        # Check that we got the individual name
        assert "?x" in bindings
        assert bindings["?x"] in ["john", "mary"]

    print("Query methods work correctly!")


def test_condition_creation():
    """Test creating Condition objects"""
    # Create conditions
    c1 = owl_rete_cpp.Condition("?f1", "type", "instance_of")
    c2 = owl_rete_cpp.Condition("?f1", "concept", "Person")
    c3 = owl_rete_cpp.Condition("?f1", "individual", "?x")

    assert c1.id_pattern == "?f1"
    assert c1.attr_pattern == "type"
    assert c1.val_pattern == "instance_of"

    print(f"Condition: {c1}")
    print("Condition creation works")


def test_query_caching():
    """Test that queries are cached"""
    network = owl_rete_cpp.ReteNetwork()

    conditions = [owl_rete_cpp.Condition("?x", "type", "Person")]

    # First call - should create and cache
    prod1 = network.build_query_pattern("cache_test", conditions)
    assert prod1 is not None
    print(f"First call returned: {prod1}")

    # Second call - should return cached
    prod2 = network.build_query_pattern("cache_test", conditions)
    assert prod2 is not None
    print(f"Second call returned: {prod2}")

    # They should be the same object
    assert prod1 == prod2
    print("Query caching works - same production returned")

    # Can retrieve from cache
    prod3 = network.get_cached_query("cache_test")
    assert prod3 is not None
    assert prod3 == prod1
    print("Cache retrieval works")


if __name__ == "__main__":
    print("Testing Query Production Builder...")

    test_condition_creation()
    print("\n" + "="*50 + "\n")

    test_query_caching()
    print("\n" + "="*50 + "\n")

    test_build_query_pattern()
    print("\n" + "="*50 + "\n")

    print("\nAll Day 3-4 tests passed!")
    print("Next: Week 1, Day 5-7 - Python Pattern API")
