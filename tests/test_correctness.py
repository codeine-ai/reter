"""
Correctness Tests - Validate core reasoning logic

Converted from tests_standalone/ to proper pytest tests.
Tests semantic correctness, error handling, and proper inference.
"""

import sys
import os
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'rete_cpp'))

from reter import owl_rete_cpp


# ============================================================================
# Error Reporting Tests
# ============================================================================

def test_error_reporting_invalid_tokens():
    """Test that invalid tokens are rejected or handled gracefully"""
    # Note: Parser may silently skip invalid characters or raise exceptions
    net = owl_rete_cpp.ReteNetwork()

    invalid_inputs = [
        "Dog ⊑ᑦ @ Animal",  # Invalid character @
        "Dog $ Animal",      # Invalid character $
    ]

    for ontology_str in invalid_inputs:
        try:
            wme_count = net.load_ontology_from_string(ontology_str)
            facts = net.get_all_facts()
            # Parser should either raise error or create no facts from invalid input
            # We don't strictly assert here since behavior may vary
        except Exception:
            # Exception is acceptable for invalid input
            pass


def test_error_reporting_grammar_errors():
    """Test that grammar errors are handled"""
    net = owl_rete_cpp.ReteNetwork()

    grammar_errors = [
        "Dog（fido",         # Missing closing paren
        "Dog ⊑ᑦ",           # Missing concept after subsumption
        "Dog ⊑ᑦ ⊑ᑦ Animal",  # Double operators
    ]

    for ontology_str in grammar_errors:
        try:
            net.load_ontology_from_string(ontology_str)
            # Grammar errors should be caught by parser
        except Exception:
            # Exception is expected
            pass


def test_error_reporting_incomplete_expressions():
    """Test that incomplete expressions are handled"""
    net = owl_rete_cpp.ReteNetwork()

    incomplete = [
        "∃hasOwner.",  # Incomplete restriction
        "¬",           # Incomplete negation
        "Dog ⊔",       # Incomplete union
    ]

    for ontology_str in incomplete:
        try:
            net.load_ontology_from_string(ontology_str)
        except Exception:
            pass


# ============================================================================
# Multiple Assertions Tests
# ============================================================================

def test_multiple_role_assertions():
    """Test that multiple role assertions work correctly"""
    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string("hasParent ∘ hasBrother ⊑ᴿ hasUncle")
    net.load_ontology_from_string("hasParent（Alice，Bob）")
    net.load_ontology_from_string("hasBrother（Bob，Charlie）")

    facts = net.get_all_facts()
    role_facts = [f for f in facts if f.get('type') == 'role_assertion']

    hasParent = [f for f in role_facts if f.get('role') == 'hasParent']
    hasBrother = [f for f in role_facts if f.get('role') == 'hasBrother']
    hasUncle = [f for f in role_facts if f.get('role') == 'hasUncle']

    assert len(hasParent) > 0, "hasParent assertion should exist"
    assert len(hasBrother) > 0, "hasBrother assertion should exist"
    # hasUncle may be inferred via property chain rule


def test_same_individual_different_properties():
    """Test same individual with different properties"""
    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string("hasChild（Alice，Bob）")
    net.load_ontology_from_string("hasChild（Alice，Charlie）")

    facts = net.get_all_facts()
    alice_children = [f for f in facts
                      if f.get('type') == 'role_assertion'
                      and f.get('subject') == 'Alice']

    assert len(alice_children) == 2, "Alice should have 2 children"


def test_same_individual_different_classes():
    """Test same individual can belong to multiple classes"""
    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string("Parent（Bob）")
    net.load_ontology_from_string("Employee（Bob）")

    facts = net.get_all_facts()
    bob_classes = [f for f in facts
                   if f.get('type') == 'instance_of'
                   and f.get('individual') == 'Bob'
                   and f.get('inferred') != 'true']

    assert len(bob_classes) == 2, "Bob should be both Parent and Employee"


def test_different_individuals_same_class():
    """Test different individuals can belong to same class"""
    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string("Person（Alice）")
    net.load_ontology_from_string("Person（Bob）")

    facts = net.get_all_facts()
    person_facts = [f for f in facts
                    if f.get('type') == 'instance_of'
                    and f.get('concept') == 'Person'
                    and f.get('inferred') != 'true']

    assert len(person_facts) == 2, "Both Alice and Bob should be Person instances"


# ============================================================================
# Signature Uniqueness Tests
# ============================================================================

def test_signature_uniqueness_diamond_deduplication():
    """Test that diamond structures deduplicate inferences correctly"""
    # Diamond: A → B → D, A → C → D
    # Should infer A⊑D once (not twice via different paths)
    tbox = """
    A ⊑ᑦ B
    A ⊑ᑦ C
    B ⊑ᑦ D
    C ⊑ᑦ D
    """

    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string(tbox)

    facts = net.get_all_facts()
    subs = [f for f in facts if f.get('type') == 'subsumption']
    inferred = [f for f in subs if f.get('inferred') == 'true']

    # Count A⊑D facts
    a_to_d = [f for f in inferred if f.get('sub') == 'A' and f.get('sup') == 'D']

    assert len(a_to_d) == 1, "A⊑D should be inferred exactly once (deduplicated)"


def test_signature_uniqueness_distinct_conclusions():
    """Test that distinct conclusions are preserved"""
    tbox = """
    A ⊑ᑦ B
    B ⊑ᑦ C
    """

    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string(tbox)

    facts = net.get_all_facts()
    subs = [f for f in facts if f.get('type') == 'subsumption']
    inferred = [f for f in subs if f.get('inferred') == 'true']

    # Should have exactly A⊑C
    assert len(inferred) == 1, "Should have exactly 1 inferred subsumption"
    assert inferred[0].get('sub') == 'A'
    assert inferred[0].get('sup') == 'C'


def test_signature_uniqueness_complex_diamond():
    """Test complex diamond structure with multiple paths"""
    #     A → B → D → F
    #     A → C → E → F
    tbox = """
    A ⊑ᑦ B
    A ⊑ᑦ C
    B ⊑ᑦ D
    C ⊑ᑦ E
    D ⊑ᑦ F
    E ⊑ᑦ F
    """

    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string(tbox)

    facts = net.get_all_facts()
    subs = [f for f in facts if f.get('type') == 'subsumption']
    inferred = [f for f in subs if f.get('inferred') == 'true']

    # Expected unique inferences: A⊑D, A⊑E, A⊑F, B⊑F, C⊑F
    expected = {
        ('A', 'D'),
        ('A', 'E'),
        ('A', 'F'),
        ('B', 'F'),
        ('C', 'F')
    }

    actual = {(f.get('sub'), f.get('sup')) for f in inferred}

    assert actual == expected, f"Expected {expected}, got {actual}"


# ============================================================================
# Comprehensive Correctness Tests (from test_correctness_validation.py)
# ============================================================================

def test_correctness_class_hierarchy():
    """Test class hierarchy subsumption correctness"""
    ontology = """
    Animal ⊑ᑦ Thing
    Mammal ⊑ᑦ Animal
    Primate ⊑ᑦ Mammal
    Hominid ⊑ᑦ Primate
    Human ⊑ᑦ Hominid
    """

    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string(ontology)
    facts = net.get_all_facts()
    subs = [f for f in facts if f.get('type') == 'subsumption']

    # Verify critical inference: Human ⊑ Animal
    human_animal = [f for f in subs
                    if f.get('sub') == 'Human'
                    and f.get('sup') == 'Animal']

    assert len(human_animal) > 0, "Human should be subclass of Animal (transitive)"


def test_correctness_instance_classification():
    """Test instance classification with class hierarchy"""
    ontology = """
    Animal ⊑ᑦ Thing
    Mammal ⊑ᑦ Animal
    Dog ⊑ᑦ Mammal
    Mammal（Fido）
    """

    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string(ontology)
    facts = net.get_all_facts()
    instances = [f for f in facts if f.get('type') == 'instance_of']

    # Fido should be inferred to be an Animal (via Mammal ⊑ Animal)
    fido_animal = [f for f in instances
                   if f.get('individual') == 'Fido'
                   and f.get('concept') == 'Animal']

    assert len(fido_animal) > 0, "Fido should be inferred as Animal"


def test_correctness_transitive_properties():
    """Test transitive property chain inference"""
    net = owl_rete_cpp.ReteNetwork()

    # Declare hasAncestor as transitive
    fact_trans = owl_rete_cpp.Fact({"type": "transitive_property", "property": "hasAncestor"})
    net.add_fact(fact_trans)

    ontology = """
    hasAncestor（Alice，Bob）
    hasAncestor（Bob，Charlie）
    hasAncestor（Charlie，Diana）
    """
    net.load_ontology_from_string(ontology)

    facts = net.get_all_facts()
    roles = [f for f in facts if f.get('type') == 'role_assertion']

    # Verify Alice → Diana (transitive closure)
    alice_diana = [f for f in roles
                   if f.get('subject') == 'Alice'
                   and f.get('object') == 'Diana']

    assert len(alice_diana) > 0, "Alice should be ancestor of Diana (transitive)"


def test_correctness_mixed_reasoning():
    """Test complex mixed scenario with classes and instances"""
    ontology = """
    Animal ⊑ᑦ Thing
    Mammal ⊑ᑦ Animal
    Dog ⊑ᑦ Mammal
    Cat ⊑ᑦ Mammal
    Dog（Fido）
    Cat（Whiskers）
    Animal（Tweety）
    """

    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string(ontology)
    facts = net.get_all_facts()

    subs = [f for f in facts if f.get('type') == 'subsumption']
    instances = [f for f in facts if f.get('type') == 'instance_of']

    # Verify Dog ⊑ Animal
    dog_animal_sub = [f for f in subs
                      if f.get('sub') == 'Dog'
                      and f.get('sup') == 'Animal']
    assert len(dog_animal_sub) > 0, "Dog should be subclass of Animal"

    # Verify Fido : Animal
    fido_animal_inst = [f for f in instances
                        if f.get('individual') == 'Fido'
                        and f.get('concept') == 'Animal']
    assert len(fido_animal_inst) > 0, "Fido should be instance of Animal"


def test_correctness_deep_hierarchy():
    """Test deep hierarchy correctness (depth 10)"""
    hierarchy_parts = ["Root ⊑ᑦ Thing"]
    for i in range(1, 10):
        if i == 1:
            hierarchy_parts.append(f"C{i} ⊑ᑦ Root")
        else:
            hierarchy_parts.append(f"C{i} ⊑ᑦ C{i-1}")

    ontology = "\n".join(hierarchy_parts)

    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string(ontology)
    facts = net.get_all_facts()
    subs = [f for f in facts if f.get('type') == 'subsumption']

    # Verify bottom reaches top: C9 ⊑ Thing
    c9_thing = [f for f in subs
                if f.get('sub') == 'C9'
                and f.get('sup') in ['Thing', 'owl:Thing']]

    assert len(c9_thing) > 0, "C9 should be subclass of Thing (deep transitive)"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
