"""
Test SWRL (Semantic Web Rule Language) support
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reter import Reter


def test_swrl_simple_class_atom():
    """Test simple SWRL rule with class atoms: Person(x) → Adult(x)"""
    r = Reter()

    # Add SWRL rule: If something is a Person, then it's an Adult
    # Add individual who is a Person
    r.load_ontology("""
        ⊢ Person（⌂x） → Adult（⌂x）
        Person（john）
    """)

    # Run reasoning
    # Reasoning is automatic/incremental - no need to call reason()

    # Should infer john is an Adult
    facts = r.pattern(('john', 'type', 'Adult'))
    assert len(facts) > 0, "Should infer john is an Adult"


def test_swrl_object_property():
    """Test SWRL rule with object properties: hasParent(x,y) ∧ hasParent(y,z) → hasGrandparent(x,z)"""
    r = Reter()

    # Add SWRL rule: If x hasParent y and y hasParent z, then x hasGrandparent z
    # Add facts: john hasParent mary, mary hasParent susan
    r.load_ontology("""
        ⊢ hasParent（⌂x，⌂y） ∧ hasParent（⌂y，⌂z） → hasGrandparent（⌂x，⌂z）
        hasParent（john，mary）
        hasParent（mary，susan）
    """)

    # Reasoning is automatic/incremental - no need to call reason()

    # Should infer john hasGrandparent susan
    facts = r.pattern(('john', 'hasGrandparent', 'susan'))
    assert len(facts) > 0, "Should infer john hasGrandparent susan"


def test_swrl_mixed_atoms():
    """Test SWRL rule with mixed class and property atoms"""
    r = Reter()

    # Rule: If x is a Person and x hasParent y, then y is a Parent
    r.load_ontology("""
        ⊢ Person（⌂x） ∧ hasParent（⌂x，⌂y） → Parent（⌂y）
        Person（alice）
        hasParent（alice，bob）
    """)

    # Reasoning is automatic/incremental - no need to call reason()

    # Should infer bob is a Parent
    facts = r.pattern(('bob', 'type', 'Parent'))
    assert len(facts) > 0, "Should infer bob is a Parent"


def test_swrl_transitive():
    """Test SWRL rule expressing transitivity"""
    r = Reter()

    # Rule: hasAncestor is transitive
    r.load_ontology("""
        ⊢ hasAncestor（⌂x，⌂y） ∧ hasAncestor（⌂y，⌂z） → hasAncestor（⌂x，⌂z）
        hasAncestor（alice，bob）
        hasAncestor（bob，charlie）
    """)

    # Reasoning is automatic/incremental - no need to call reason()

    # Should infer alice hasAncestor charlie
    facts = r.pattern(('alice', 'hasAncestor', 'charlie'))
    assert len(facts) > 0, "Should infer alice hasAncestor charlie"


def test_swrl_sibling_rule():
    """Test SWRL rule for sibling relationship (simplified without differentFrom in rule)"""
    r = Reter()

    # Rule: If x and y have same parent, they might be siblings (simplified)
    # In practice, SWRL differentFrom in antecedent is tricky, so we test simpler version
    r.load_ontology("""
        ⊢ hasParent（⌂x，⌂z） ∧ hasParent（⌂y，⌂z） → potentialSibling（⌂x，⌂y）
        hasParent（alice，mary）
        hasParent（bob，mary）
    """)

    # Reasoning is automatic/incremental - no need to call reason()

    # Should infer alice potentialSibling bob
    facts = r.pattern(('alice', 'potentialSibling', 'bob'))
    assert len(facts) > 0, "Should infer alice potentialSibling bob"


def test_swrl_uncle_rule():
    """Test SWRL rule for uncle relationship"""
    r = Reter()

    # Rule: If x hasParent y and y hasBrother z, then x hasUncle z
    r.load_ontology("""
        ⊢ hasParent（⌂x，⌂y） ∧ hasBrother（⌂y，⌂z） → hasUncle（⌂x，⌂z）
        hasParent（charlie，alice）
        hasBrother（alice，bob）
    """)

    # Reasoning is automatic/incremental - no need to call reason()

    # Should infer charlie hasUncle bob
    facts = r.pattern(('charlie', 'hasUncle', 'bob'))
    assert len(facts) > 0, "Should infer charlie hasUncle bob"


def test_swrl_type_propagation():
    """Test SWRL rule that propagates types through relationships"""
    r = Reter()

    # Rule: If x owns y and y is a Car, then x is a CarOwner
    r.load_ontology("""
        ⊢ owns（⌂x，⌂y） ∧ Car（⌂y） → CarOwner（⌂x）
        owns（alice，vehicle1）
        Car（vehicle1）
    """)

    # Reasoning is automatic/incremental - no need to call reason()

    # Should infer alice is CarOwner
    facts = r.pattern(('alice', 'type', 'CarOwner'))
    assert len(facts) > 0, "Should infer alice is a CarOwner"


def test_swrl_with_owl_subsumption():
    """Test SWRL producing facts that OWL rules can use"""
    r = Reter()

    # Add OWL subsumption and SWRL rule
    # Load ontology with SWRL rule and subsumption
    r.load_ontology("""
        ⊢ Person（⌂x） → Adult（⌂x）
        Adult ⊑ᑦ Human
        Person（alice）
    """)

    # Reasoning is automatic/incremental - no need to call reason()

    # Should infer alice is Adult (via SWRL)
    facts_adult = r.pattern(('alice', 'type', 'Adult'))
    assert len(facts_adult) > 0, "Should infer alice is Adult via SWRL"

    # Should infer alice is Human (via OWL cax-sco after SWRL)
    facts_human = r.pattern(('alice', 'type', 'Human'))
    assert len(facts_human) > 0, "Should infer alice is Human via OWL cax-sco"


def test_swrl_multiple_bindings():
    """Test SWRL rule that produces multiple bindings"""
    r = Reter()

    # Rule: If x is a Student, x is a Person
    r.load_ontology("""
        ⊢ Student（⌂x） → Person（⌂x）
        Student（alice）
        Student（bob）
        Student（charlie）
    """)

    # Reasoning is automatic/incremental - no need to call reason()

    # Should infer all three are Persons
    facts_alice = r.pattern(('alice', 'type', 'Person'))
    facts_bob = r.pattern(('bob', 'type', 'Person'))
    facts_charlie = r.pattern(('charlie', 'type', 'Person'))

    assert len(facts_alice) > 0, "Should infer alice is Person"
    assert len(facts_bob) > 0, "Should infer bob is Person"
    assert len(facts_charlie) > 0, "Should infer charlie is Person"


def test_swrl_chain_inference():
    """Test chained SWRL inferences"""
    r = Reter()

    # Rule 1: Employee(x) → Person(x)
    # Rule 2: Person(x) → LivingBeing(x)
    r.load_ontology("""
        ⊢ Employee（⌂x） → Person（⌂x）
        ⊢ Person（⌂x） → LivingBeing（⌂x）
        Employee（alice）
    """)

    # Reasoning is automatic/incremental - no need to call reason()

    # Should infer alice is Person (direct from rule 1)
    facts_person = r.pattern(('alice', 'type', 'Person'))
    assert len(facts_person) > 0, "Should infer alice is Person"

    # Should infer alice is LivingBeing (chained via rule 2)
    facts_living = r.pattern(('alice', 'type', 'LivingBeing'))
    assert len(facts_living) > 0, "Should infer alice is LivingBeing"


if __name__ == "__main__":
    test_swrl_simple_class_atom()
    test_swrl_object_property()
    test_swrl_mixed_atoms()
    test_swrl_transitive()
    test_swrl_sibling_rule()
    test_swrl_uncle_rule()
    test_swrl_type_propagation()
    test_swrl_with_owl_subsumption()
    test_swrl_multiple_bindings()
    test_swrl_chain_inference()
    print("All SWRL tests passed!")
