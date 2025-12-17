"""
Test Token bindings exposed to Python
Week 1, Day 1-2 of IMPLEMENTATION_PLAN.md
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'rete_cpp'))
from reter_core import owl_rete_cpp


def test_token_class_exists():
    """Test that Token class is accessible from Python"""
    # Token class should be available
    assert hasattr(owl_rete_cpp, 'Token')


def test_basic_network_creation():
    """Test that we can create a network and load ontology"""
    network = owl_rete_cpp.ReteNetwork()

    # Load simple ontology using the correct DL notation
    network.load_ontology_from_string("""
        Person（john）
        hasAge（john，30）
    """)

    # Verify facts were loaded
    assert network.fact_count() > 0
    print(f"Network created with {network.fact_count()} facts")


def test_token_bindings_placeholder():
    """
    Placeholder test for token binding extraction
    This will be fully implemented once we have query productions in Day 3-4
    """
    # For now, just verify the network works
    network = owl_rete_cpp.ReteNetwork()
    network.load_ontology_from_string("""
        Person（john）
        Person（mary）
        hasAge（john，30）
        hasAge（mary，25）
    """)

    assert network.fact_count() > 0
    print(f"Token bindings test prepared (will be completed in Day 3-4)")


if __name__ == "__main__":
    print("Testing Token bindings...")

    test_token_class_exists()
    print("Token class is accessible")

    test_basic_network_creation()
    print("Basic network creation works")

    test_token_bindings_placeholder()
    print("Placeholder test ready")

    print("\nAll Day 1-2 tests passed!")
    print("Next: Day 3-4 - Query Production Builder")
