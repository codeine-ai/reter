"""
Test for advanced OWL 2 RL rules: prp-spo2 (property chains) and prp-key (hasKey)
All tests use DL syntax (LARK grammar) - NO add_fact() calls
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reter import Reter


def test_prp_spo2_simple_chain():
    """Test prp-spo2 rule with simple 2-property chain"""
    print("\n" + "=" * 60)
    print("TEST: Property Chain - Simple (prp-spo2)")
    print("=" * 60)

    reasoner = Reter()

    # Define hasGrandparent as chain of hasParent ∘ hasParent
    # If Alice hasParent Bob and Bob hasParent Charlie, then Alice hasGrandparent Charlie
    ontology = """
    Person（Alice）
    Person（Bob）
    Person（Charlie）
    hasParent（Alice， Bob）
    hasParent（Bob， Charlie）
    hasParent ∘ hasParent ⊑ᴿ hasGrandparent
    """

    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check that Alice hasGrandparent Charlie is inferred
    facts = reasoner.query(
        type="role_assertion",
        subject="Alice",
        role="hasGrandparent",
        object="Charlie"
    )

    print(f"\nInferred facts for Alice hasGrandparent Charlie: {len(facts)}")
    for fact in facts:
        print(f"  - {fact}")

    assert len(facts) > 0, "Should infer Alice hasGrandparent Charlie (property chain)"

    # Check that prp-spo2 rule was triggered
    has_prp_spo2 = any(fact.get("inferred_by") == "prp-spo2" for fact in facts)
    assert has_prp_spo2, "Should have inference from prp-spo2 rule"

    print("✓ Test passed: Property chain - simple (prp-spo2)")


def test_prp_spo2_three_property_chain():
    """Test prp-spo2 rule with 3-property chain"""
    print("\n" + "=" * 60)
    print("TEST: Property Chain - Three Properties (prp-spo2)")
    print("=" * 60)

    reasoner = Reter()

    # Define hasGreatGrandparent as chain of hasParent ∘ hasParent ∘ hasParent
    ontology = """
    Person（Alice）
    Person（Bob）
    Person（Charlie）
    Person（Diana）
    hasParent（Alice， Bob）
    hasParent（Bob， Charlie）
    hasParent（Charlie， Diana）
    hasParent ∘ hasParent ∘ hasParent ⊑ᴿ hasGreatGrandparent
    """

    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check that Alice hasGreatGrandparent Diana is inferred
    facts = reasoner.query(
        type="role_assertion",
        subject="Alice",
        role="hasGreatGrandparent",
        object="Diana"
    )

    print(f"\nInferred facts for Alice hasGreatGrandparent Diana: {len(facts)}")
    for fact in facts:
        print(f"  - {fact}")

    assert len(facts) > 0, "Should infer Alice hasGreatGrandparent Diana (3-property chain)"

    has_prp_spo2 = any(fact.get("inferred_by") == "prp-spo2" for fact in facts)
    assert has_prp_spo2, "Should have inference from prp-spo2 rule"

    print("✓ Test passed: Property chain - three properties (prp-spo2)")


def test_prp_spo2_uncle_chain():
    """Test prp-spo2 rule with mixed properties (uncle relationship)"""
    print("\n" + "=" * 60)
    print("TEST: Property Chain - Mixed Properties (Uncle) (prp-spo2)")
    print("=" * 60)

    reasoner = Reter()

    # Define hasUncle as chain of hasParent ∘ hasBrother
    # If Alice hasParent Bob and Bob hasBrother Charlie, then Alice hasUncle Charlie
    ontology = """
    Person（Alice）
    Person（Bob）
    Person（Charlie）
    hasParent（Alice， Bob）
    hasBrother（Bob， Charlie）
    hasParent ∘ hasBrother ⊑ᴿ hasUncle
    """

    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check that Alice hasUncle Charlie is inferred
    facts = reasoner.query(
        type="role_assertion",
        subject="Alice",
        role="hasUncle",
        object="Charlie"
    )

    print(f"\nInferred facts for Alice hasUncle Charlie: {len(facts)}")
    for fact in facts:
        print(f"  - {fact}")

    assert len(facts) > 0, "Should infer Alice hasUncle Charlie (mixed property chain)"

    has_prp_spo2 = any(fact.get("inferred_by") == "prp-spo2" for fact in facts)
    assert has_prp_spo2, "Should have inference from prp-spo2 rule"

    print("✓ Test passed: Property chain - mixed properties (prp-spo2)")


def test_prp_spo2_multiple_chains():
    """Test prp-spo2 rule with multiple possible chain paths"""
    print("\n" + "=" * 60)
    print("TEST: Property Chain - Multiple Paths (prp-spo2)")
    print("=" * 60)

    reasoner = Reter()

    # Multiple paths to grandparents
    ontology = """
    Person（Alice）
    Person（Bob）
    Person（Charlie）
    Person（Diana）
    Person（Eve）
    hasParent（Alice， Bob）
    hasParent（Alice， Charlie）
    hasParent（Bob， Diana）
    hasParent（Charlie， Eve）
    hasParent ∘ hasParent ⊑ᴿ hasGrandparent
    """

    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check for both grandparents
    facts_diana = reasoner.query(
        type="role_assertion",
        subject="Alice",
        role="hasGrandparent",
        object="Diana"
    )

    facts_eve = reasoner.query(
        type="role_assertion",
        subject="Alice",
        role="hasGrandparent",
        object="Eve"
    )

    print(f"\nInferred facts for Alice hasGrandparent Diana: {len(facts_diana)}")
    print(f"Inferred facts for Alice hasGrandparent Eve: {len(facts_eve)}")

    assert len(facts_diana) > 0, "Should infer Alice hasGrandparent Diana"
    assert len(facts_eve) > 0, "Should infer Alice hasGrandparent Eve"

    print("✓ Test passed: Property chain - multiple paths (prp-spo2)")


def test_prp_key_single_property():
    """Test prp-key rule with single key property"""
    print("\n" + "=" * 60)
    print("TEST: HasKey - Single Property (prp-key)")
    print("=" * 60)

    reasoner = Reter()

    # Person class has key hasSocialSecurityNumber
    # If two persons have the same SSN, they are the same individual
    ontology = """
    Person（Alice）
    Person（Bob）
    hasSSN（Alice， SSN123）
    hasSSN（Bob， SSN123）
    Person ⊑ᴷ （hasSSN）
    """

    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check that Alice and Bob are inferred to be the same
    facts = reasoner.query(
        type="same_as",
        ind1="Alice",
        ind2="Bob"
    )

    print(f"\nInferred sameAs facts for Alice=Bob: {len(facts)}")
    for fact in facts:
        print(f"  - {fact}")

    assert len(facts) > 0, "Should infer Alice sameAs Bob (same SSN key)"

    # Check that prp-key rule was triggered (template creates class-specific rule names like "prp-key-Person")
    has_prp_key = any(fact.get("inferred_by", "").startswith("prp-key") for fact in facts)
    assert has_prp_key, "Should have inference from prp-key rule"

    print("✓ Test passed: HasKey - single property (prp-key)")


def test_prp_key_multiple_properties():
    """Test prp-key rule with multiple key properties (composite key)"""
    print("\n" + "=" * 60)
    print("TEST: HasKey - Composite Key (prp-key)")
    print("=" * 60)

    reasoner = Reter()

    # Account class has composite key: username + domain
    # Two accounts are the same if they have both the same username AND domain
    ontology = """
    Account（Account1）
    Account（Account2）
    Account（Account3）
    hasUsername（Account1， user123）
    hasDomain（Account1， example_com）
    hasUsername（Account2， user123）
    hasDomain（Account2， example_com）
    hasUsername（Account3， user123）
    hasDomain（Account3， other_com）
    Account ⊑ᴷ （hasUsername， hasDomain）
    """

    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check that Account1 and Account2 are the same (both keys match)
    facts_12 = reasoner.query(
        type="same_as",
        ind1="Account1",
        ind2="Account2"
    )

    # Check that Account1 and Account3 are NOT the same (domain differs)
    facts_13 = reasoner.query(
        type="same_as",
        ind1="Account1",
        ind2="Account3"
    )

    print(f"\nInferred sameAs for Account1=Account2: {len(facts_12)}")
    print(f"Inferred sameAs for Account1=Account3: {len(facts_13)}")

    assert len(facts_12) > 0, "Should infer Account1 sameAs Account2 (both keys match)"
    assert len(facts_13) == 0, "Should NOT infer Account1 sameAs Account3 (domain differs)"

    # Check that prp-key rule was triggered (template creates class-specific rule names like "prp-key-Account")
    has_prp_key = any(fact.get("inferred_by", "").startswith("prp-key") for fact in facts_12)
    assert has_prp_key, "Should have inference from prp-key rule"

    print("✓ Test passed: HasKey - composite key (prp-key)")


def test_prp_key_different_classes():
    """Test prp-key rule only matches within same class"""
    print("\n" + "=" * 60)
    print("TEST: HasKey - Class Restriction (prp-key)")
    print("=" * 60)

    reasoner = Reter()

    # Person has key hasSSN
    # Company also has key hasSSN (different types)
    # Same SSN should not match across classes
    ontology = """
    Person（Alice）
    Company（CorpX）
    hasSSN（Alice， SSN123）
    hasSSN（CorpX， SSN123）
    Person ⊑ᴷ （hasSSN）
    """

    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check that Alice and CorpX are NOT the same (different classes)
    facts = reasoner.query(
        type="same_as",
        ind1="Alice",
        ind2="CorpX"
    )

    print(f"\nInferred sameAs for Alice=CorpX: {len(facts)}")

    assert len(facts) == 0, "Should NOT infer Alice sameAs CorpX (different classes)"

    print("✓ Test passed: HasKey - class restriction (prp-key)")


def test_combined_chains_and_keys():
    """Test property chains and hasKey working together"""
    print("\n" + "=" * 60)
    print("TEST: Combined Property Chains and HasKey")
    print("=" * 60)

    reasoner = Reter()

    # Complex scenario: property chains create relationships, then keys identify same individuals
    ontology = """
    Person（Alice）
    Person（Bob1）
    Person（Bob2）
    Person（Charlie）
    hasParent（Alice， Bob1）
    hasParent（Bob1， Charlie）
    hasParent（Alice， Bob2）
    hasSSN（Bob1， SSN999）
    hasSSN（Bob2， SSN999）
    hasParent ∘ hasParent ⊑ᴿ hasGrandparent
    Person ⊑ᴷ （hasSSN）
    """

    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Bob1 and Bob2 should be identified as the same (via hasKey)
    facts_same = reasoner.query(
        type="same_as",
        ind1="Bob1",
        ind2="Bob2"
    )

    # Alice should have Charlie as grandparent (via chain)
    facts_grandparent = reasoner.query(
        type="role_assertion",
        subject="Alice",
        role="hasGrandparent",
        object="Charlie"
    )

    print(f"\nInferred Bob1=Bob2: {len(facts_same)}")
    print(f"Inferred Alice hasGrandparent Charlie: {len(facts_grandparent)}")

    assert len(facts_same) > 0, "Should infer Bob1 sameAs Bob2"
    assert len(facts_grandparent) > 0, "Should infer Alice hasGrandparent Charlie"

    print("✓ Test passed: Combined property chains and hasKey")


if __name__ == '__main__':
    test_prp_spo2_simple_chain()
    test_prp_spo2_three_property_chain()
    test_prp_spo2_uncle_chain()
    test_prp_spo2_multiple_chains()
    test_prp_key_single_property()
    test_prp_key_multiple_properties()
    test_prp_key_different_classes()
    test_combined_chains_and_keys()

    print("\n" + "=" * 60)
    print("ALL ADVANCED RULES TESTS PASSED")
    print("=" * 60)
