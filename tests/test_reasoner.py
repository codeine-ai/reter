"""
Tests for DL Reasoner with C++ OWL RETE
"""

import sys
import os
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reter import Reter


def test_basic_subsumption():
    """Test basic subsumption reasoning"""
    print("\n" + "=" * 60)
    print("TEST: Basic Subsumption")
    print("=" * 60)

    reasoner = Reter()

    ontology = """
    Cat ⊑ᑦ Animal
    Person ⊑ᑦ Animal
    Person（John）
    Cat（Felix）
    """

    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check if John is an Animal (inferred via subsumption)
    animals = reasoner.get_instances('Animal')
    print(f"\nAnimals: {animals}")

    assert 'John' in animals, "John should be an Animal"
    assert 'Felix' in animals, "Felix should be an Animal"

    print("✓ Test passed: Basic subsumption works")


def test_transitivity():
    """Test transitive subsumption"""
    print("\n" + "=" * 60)
    print("TEST: Transitive Subsumption")
    print("=" * 60)

    reasoner = Reter()

    ontology = """
    Student ⊑ᑦ Person
    Person ⊑ᑦ Animal
    Animal ⊑ᑦ LivingThing
    Student（Alice）
    """

    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Alice should be all of these via transitivity
    living_things = reasoner.get_instances('LivingThing')
    animals = reasoner.get_instances('Animal')
    persons = reasoner.get_instances('Person')

    print(f"\nLivingThings: {living_things}")
    print(f"Animals: {animals}")
    print(f"Persons: {persons}")

    assert 'Alice' in living_things, "Alice should be a LivingThing"
    assert 'Alice' in animals, "Alice should be an Animal"
    assert 'Alice' in persons, "Alice should be a Person"

    print("✓ Test passed: Transitive subsumption works")


def test_equivalence():
    """Test equivalence reasoning"""
    print("\n" + "=" * 60)
    print("TEST: Equivalence")
    print("=" * 60)

    reasoner = Reter()

    ontology = """
    Human ≡ᑦ Person
    Human（John）
    """

    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    persons = reasoner.get_instances('Person')
    humans = reasoner.get_instances('Human')

    print(f"\nPersons: {persons}")
    print(f"Humans: {humans}")

    assert 'John' in persons, "John should be a Person (via equivalence)"
    assert 'John' in humans, "John should be a Human"

    print("✓ Test passed: Equivalence works")


def test_role_subsumption():
    """Test role subsumption"""
    print("\n" + "=" * 60)
    print("TEST: Role Subsumption")
    print("=" * 60)

    reasoner = Reter()

    ontology = """
    hasParent ⊑ᴿ hasAncestor
    hasParent（John， Mary）
    """

    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    ancestors = reasoner.get_role_assertions(role='hasAncestor')
    parents = reasoner.get_role_assertions(role='hasParent')

    print(f"\nParent relationships: {parents}")
    print(f"Ancestor relationships: {ancestors}")

    assert ('John', 'hasAncestor', 'Mary') in ancestors, "John should have Mary as ancestor"

    print("✓ Test passed: Role subsumption works")


def test_symmetric_property():
    """Test symmetric property reasoning"""
    print("\n" + "=" * 60)
    print("TEST: Symmetric Property")
    print("=" * 60)

    reasoner = Reter()

    # Define symmetric property using role equivalence with inverse
    # knows ≣ knows⁻ means knows is symmetric
    ontology = """
    knows ≡ᴿ knows⁻
    knows（John， Mary）
    """

    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    knows_facts = reasoner.get_role_assertions(role='knows')
    print(f"\n'knows' relationships: {knows_facts}")

    assert ('Mary', 'knows', 'John') in knows_facts, "If John knows Mary, Mary should know John (symmetric)"

    print("✓ Test passed: Symmetric property works")


def test_transitive_property():
    """Test transitive property reasoning"""
    print("\n" + "=" * 60)
    print("TEST: Transitive Property")
    print("=" * 60)

    reasoner = Reter()

    # Define transitive property using role chain
    # ancestorOf ∘ ancestorOf ⊏ ancestorOf means ancestorOf is transitive
    ontology = """
    ancestorOf ∘ ancestorOf ⊑ᴿ ancestorOf
    ancestorOf（Alice， Bob）
    ancestorOf（Bob， Charlie）
    """

    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    ancestor_facts = reasoner.get_role_assertions(role='ancestorOf')
    print(f"\n'ancestorOf' relationships: {ancestor_facts}")

    assert ('Alice', 'ancestorOf', 'Charlie') in ancestor_facts, "Alice should be ancestor of Charlie (transitive)"

    print("✓ Test passed: Transitive property works")


def test_equality():
    """Test equality reasoning"""
    print("\n" + "=" * 60)
    print("TEST: Equality (owl:sameAs)")
    print("=" * 60)

    reasoner = Reter()

    ontology = """
    Person（John）
    Person（Jonathan）
    John ﹦ Jonathan
    """

    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check for symmetric same_as using pattern query
    same_facts = list(reasoner.pattern(("?x", "same_as", "?y")))
    print(f"\nSame-as relationships: {[(f['?x'], f['?y']) for f in same_facts]}")

    # Check if both directions exist
    has_forward = any(f['?x'] == 'John' and f['?y'] == 'Jonathan' for f in same_facts)
    has_backward = any(f['?x'] == 'Jonathan' and f['?y'] == 'John' for f in same_facts)

    assert has_forward or has_backward, "Should have equality in at least one direction"

    print("✓ Test passed: Equality works")


def test_complex_ontology():
    """Test more complex ontology"""
    print("\n" + "=" * 60)
    print("TEST: Complex Ontology")
    print("=" * 60)

    reasoner = Reter()

    ontology = """
    Student ⊑ᑦ Person
    Professor ⊑ᑦ Person
    Person ⊑ᑦ Animal
    Animal ⊑ᑦ LivingThing

    Student（Alice）
    Professor（Bob）

    teaches ⊑ᴿ interactsWith
    teaches（Bob， Alice）

    Person（Charlie）
    Charlie ﹦ Alice
    """

    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Various checks
    living_things = reasoner.get_instances('LivingThing')
    print(f"\nAll living things: {living_things}")

    interactions = reasoner.get_role_assertions(role='interactsWith')
    print(f"Interactions: {interactions}")

    assert 'Alice' in living_things
    assert 'Bob' in living_things
    assert ('Bob', 'interactsWith', 'Alice') in interactions

    print("✓ Test passed: Complex ontology works")


def run_all_tests():
    """Run all tests"""
    tests = [
        test_basic_subsumption,
        test_transitivity,
        test_equivalence,
        test_role_subsumption,
        test_symmetric_property,
        test_transitive_property,
        test_equality,
        test_complex_ontology
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"\n✗ Test FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗ Test ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
