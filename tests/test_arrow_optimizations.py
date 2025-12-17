"""
Test Arrow optimizations for DLReasoner methods

This test verifies that all the Arrow-optimized methods work correctly:
- get_all_facts()
- get_inferred_facts()
- get_instances()
- get_subsumers()
- get_subsumed()
- get_role_assertions()
"""

from reter import Reter


def test_arrow_optimizations():
    print("Creating DLReasoner...")
    reasoner = Reter()

    # Add some simple test data
    print("\nAdding test ontology data...")

    ontology = """
    Dog ⊑ᑦ Animal
    Cat ⊑ᑦ Animal
    Dog（Fido）
    Cat（Whiskers）
    owns（John，Fido）
    owns（Jane，Whiskers）
    """

    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Test 1: get_all_facts() - should return Arrow table
    print("\n=== Test 1: get_all_facts() ===")
    all_facts = reasoner.get_all_facts()
    print(f"Type: {type(all_facts)}")
    print(f"Number of facts: {all_facts.num_rows}")
    print(f"Columns: {all_facts.column_names}")
    print(f"First 5 rows:\n{all_facts.slice(0, min(5, all_facts.num_rows))}")

    # Test 2: get_inferred_facts() - should return filtered Arrow table
    print("\n=== Test 2: get_inferred_facts() ===")
    inferred = reasoner.get_inferred_facts()
    print(f"Type: {type(inferred)}")
    print(f"Number of inferred facts: {inferred.num_rows}")
    if inferred.num_rows > 0:
        print(f"First 5 inferred:\n{inferred.slice(0, min(5, inferred.num_rows))}")

    # Test 3: get_instances() - should return list
    print("\n=== Test 3: get_instances() ===")
    dog_instances = reasoner.get_instances("Dog")
    print(f"Dog instances: {dog_instances}")

    animal_instances = reasoner.get_instances("Animal")
    print(f"Animal instances (should include Fido): {animal_instances}")

    # Test 4: get_subsumers() - should return list
    print("\n=== Test 4: get_subsumers() ===")
    dog_subsumers = reasoner.get_subsumers("Dog")
    print(f"Subsumers of Dog (should include Animal): {dog_subsumers}")

    # Test 5: get_subsumed() - should return list
    print("\n=== Test 5: get_subsumed() ===")
    animal_subsumed = reasoner.get_subsumed("Animal")
    print(f"Subsumed by Animal (should include Dog, Cat): {animal_subsumed}")

    # Test 6: get_role_assertions() - should return list of tuples
    print("\n=== Test 6: get_role_assertions() ===")

    # All role assertions
    all_roles = reasoner.get_role_assertions()
    print(f"All role assertions: {all_roles}")

    # Filter by role
    owns_assertions = reasoner.get_role_assertions(role="owns")
    print(f"'owns' role assertions: {owns_assertions}")

    # Filter by subject
    john_assertions = reasoner.get_role_assertions(subject="John")
    print(f"John's assertions: {john_assertions}")

    # Filter by object
    fido_assertions = reasoner.get_role_assertions(object="Fido")
    print(f"Assertions about Fido: {fido_assertions}")

    print("\n=== All tests completed successfully! ===")


if __name__ == "__main__":
    test_arrow_optimizations()
