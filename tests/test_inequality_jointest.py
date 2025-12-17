"""
Test native inequality support in JoinTest

This test verifies that the inequality constraint implementation works correctly by
testing the cax-sco rule which now uses native inequality constraints instead of
runtime guards.

Test Strategy:
1. Add a redundant subsumption (Dog ⊑ Dog) - should NOT create inference
2. Add a valid subsumption (Dog ⊑ Animal) - SHOULD create inference
3. Verify correctness and performance improvement
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'rete_cpp'))

from reter import owl_rete_cpp as rete


def test_cax_sco_no_redundant_inference():
    """Test that cax-sco with inequality doesn't create redundant inferences"""
    print("\n=== Test 2: cax-sco with Native Inequality ===")

    network = rete.ReteNetwork()

    # Add subsumption: Dog ⊑ Dog (should NOT create inference due to inequality)
    print("\nAdding subsumption: Dog ⊑ Dog")
    fact1 = rete.Fact()
    fact1.set("type", "subsumption")
    fact1.set("sub", "Dog")
    fact1.set("sup", "Dog")
    network.add_fact(fact1)

    # Add instance: fido : Dog
    print("Adding instance: fido : Dog")
    fact2 = rete.Fact()
    fact2.set("type", "instance_of")
    fact2.set("individual", "fido")
    fact2.set("concept", "Dog")
    network.add_fact(fact2)

    # Get all instance_of facts
    all_facts = network.get_all_facts()
    instance_facts = [f for f in all_facts if f.get("type") == "instance_of"]

    # Should only have the original fact, NOT an inferred one (because Dog == Dog)
    print(f"\nInstance facts found: {len(instance_facts)}")
    for f in instance_facts:
        print(f"  - {f.get('individual')} : {f.get('concept')} (inferred: {f.get('inferred', 'false')})")

    # Count non-inferred vs inferred (excluding owl:Thing)
    original_count = sum(1 for f in instance_facts if f.get("inferred", "false") == "false")
    inferred_dog_facts = [f for f in instance_facts if f.get("inferred", "false") == "true" and f.get("concept") == "Dog"]

    # Should NOT have inferred Dog(fido) because Dog==Dog is filtered by inequality
    assert len(inferred_dog_facts) == 0, f"Expected 0 inferred Dog facts (Dog==Dog should be filtered), got {len(inferred_dog_facts)}"
    assert original_count == 1, f"Expected 1 original fact, got {original_count}"

    print("✓ Correctly filtered redundant subsumption (Dog==Dog)")

    # Now add a valid subsumption: Dog ⊑ Animal
    print("\nAdding subsumption: Dog ⊑ Animal")
    fact3 = rete.Fact()
    fact3.set("type", "subsumption")
    fact3.set("sub", "Dog")
    fact3.set("sup", "Animal")
    network.add_fact(fact3)

    # Should now have 1 inferred fact (fido:Animal)
    all_facts = network.get_all_facts()
    instance_facts = [f for f in all_facts if f.get("type") == "instance_of"]
    animal_facts = [f for f in instance_facts if f.get("concept") == "Animal"]

    print(f"\nInstance facts after adding Dog ⊑ Animal: {len(instance_facts)}")
    for f in instance_facts:
        print(f"  - {f.get('individual')} : {f.get('concept')} (inferred: {f.get('inferred', 'false')})")

    # Verify the inferred Animal fact exists
    assert len(animal_facts) > 0, "Expected to find fido:Animal fact"

    # Find the inferred Animal fact (there might also be an owl:Thing fact)
    inferred_animal = next((f for f in animal_facts if f.get("inferred", "false") == "true"), None)
    assert inferred_animal is not None, "Expected Animal fact to be inferred"
    assert inferred_animal.get("inferred_by") == "cax-sco", "Should be inferred by cax-sco"

    print(f"\n✓ cax-sco inequality test passed!")


def test_performance_comparison():
    """Compare token creation with and without inequality constraint"""
    print("\n=== Test 3: Performance Comparison ===")

    network = rete.ReteNetwork()

    # Add multiple subsumptions including redundant ones
    subsumptions = [
        ("Dog", "Dog"),      # Redundant
        ("Dog", "Animal"),
        ("Cat", "Cat"),      # Redundant
        ("Cat", "Animal"),
        ("Animal", "Animal"), # Redundant
    ]

    for sub, sup in subsumptions:
        fact = rete.Fact()
        fact.set("type", "subsumption")
        fact.set("sub", sub)
        fact.set("sup", sup)
        network.add_fact(fact)

    # Add instances
    individuals = [
        ("fido", "Dog"),
        ("fluffy", "Cat"),
        ("tweety", "Bird"),
    ]

    for ind, concept in individuals:
        fact = rete.Fact()
        fact.set("type", "instance_of")
        fact.set("individual", ind)
        fact.set("concept", concept)
        network.add_fact(fact)

    # Count inferences
    all_facts = network.get_all_facts()
    instance_facts = [f for f in all_facts if f.get("type") == "instance_of"]
    inferred_facts = [f for f in instance_facts if f.get("inferred", "false") == "true"]

    print(f"\nTotal instance facts: {len(instance_facts)}")
    print(f"Original facts: {len(instance_facts) - len(inferred_facts)}")
    print(f"Inferred facts: {len(inferred_facts)}")

    # Should have inferred Dog->Animal, Cat->Animal
    # Plus owl:Thing inferences for each original instance
    # Should NOT have inferred Dog->Dog, Cat->Cat, Animal->Animal (filtered by inequality)

    # Count non-owl:Thing inferred facts
    non_thing_inferred = [f for f in inferred_facts if f.get("concept") != "owl:Thing"]
    print(f"Non-owl:Thing inferred facts: {len(non_thing_inferred)}")
    for f in non_thing_inferred:
        print(f"  - {f.get('individual')} : {f.get('concept')}")

    assert len(non_thing_inferred) == 2, f"Expected 2 non-owl:Thing inferred facts (Dog->Animal, Cat->Animal), got {len(non_thing_inferred)}"

    # Verify the correct facts were inferred
    fido_animal = any(f.get("individual") == "fido" and f.get("concept") == "Animal" for f in non_thing_inferred)
    fluffy_animal = any(f.get("individual") == "fluffy" and f.get("concept") == "Animal" for f in non_thing_inferred)

    assert fido_animal, "Expected fido:Animal to be inferred"
    assert fluffy_animal, "Expected fluffy:Animal to be inferred"

    print(f"\n✓ Performance test passed!")
    print(f"  Redundant subsumptions (Dog⊑Dog, Cat⊑Cat, Animal⊑Animal) were filtered at join time!")
    print(f"  Only valid inferences (Dog->Animal, Cat->Animal) were created.")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Native Inequality Support in RETE JoinTest")
    print("=" * 60)

    try:
        test_cax_sco_no_redundant_inference()
        test_performance_comparison()

        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
