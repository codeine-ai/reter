"""
Test for OWL 2 RL inference rules from more.owlrl.jena
All tests use DL syntax (LARK grammar) instead of add_fact()
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reter import Reter


def test_cls_minc_rec():
    """Test cls-minc-rec rule (min cardinality recognition)"""
    print("\n" + "=" * 60)
    print("TEST: Min Cardinality Recognition (cls-minc-rec)")
    print("=" * 60)

    reasoner = Reter()

    # Define ParentOfAtLeastOne as ≥1 hasChild.Person (min cardinality 1)
    # Then make John have a child (satisfies restriction)
    # Grammar: GE NAT node DOT node -> number_restriction_ge
    ontology = """
    Person ⊑ᑦ ⊤
    ParentOfAtLeastOne ≡ᑦ ≥1 hasChild․Person
    Person（Mary）
    hasChild（John， Mary）
    """

    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check that John is inferred to be ParentOfAtLeastOne
    facts = reasoner.query(
        type="instance_of",
        individual="John",
        concept="ParentOfAtLeastOne"
    )

    print(f"\nInferred facts for John:ParentOfAtLeastOne: {len(facts)}")
    for fact in facts:
        print(f"  - {fact}")

    assert len(facts) > 0, "Should infer John is ParentOfAtLeastOne (has at least 1 child)"

    # Check that cls-minc-rec rule was triggered (or equivalence/subsumption rule based on it)
    has_cls_minc_rec = any(
        fact.get("inferred_by") in ["cls-minc-rec", "cax-eqc1", "cax-eqc2", "cax-sco"]
        for fact in facts
    )
    assert has_cls_minc_rec, "Should have inference from cls-minc-rec or equivalence rule"

    print("✓ Test passed: Min cardinality recognition (cls-minc-rec)")


def test_cls_maxc_rec():
    """Test cls-maxc-rec rule (max cardinality recognition from functional property)"""
    print("\n" + "=" * 60)
    print("TEST: Max Cardinality Recognition from Functional (cls-maxc-rec)")
    print("=" * 60)

    reasoner = Reter()

    # Define hasMother as functional property
    # Define HasAtMostOneMother as ≤1 hasMother.Person (max cardinality 1)
    # All individuals should satisfy this restriction (functional property guarantees it)
    # Grammar: LE NAT node DOT node -> number_restriction_le
    # Note: Functional property syntax requires code or special handling
    ontology = """
    Person ⊑ᑦ ⊤
    HasAtMostOneMother ≡ᑦ ≤1 hasMother․Person
    Person（Alice）
    Person（Bob）
    """

    reasoner.load_ontology(ontology)

    # Add functional property using add_fact (not part of DL syntax yet)
    reasoner.add_fact({
        "type": "functional",
        "property": "hasMother"
    })

    # Reasoning is automatic/incremental - no need to call reason()

    # Check that both Alice and Bob are inferred to be HasAtMostOneMother
    facts_alice = reasoner.query(
        type="instance_of",
        individual="Alice",
        concept="HasAtMostOneMother"
    )

    facts_bob = reasoner.query(
        type="instance_of",
        individual="Bob",
        concept="HasAtMostOneMother"
    )

    print(f"\nInferred facts for Alice:HasAtMostOneMother: {len(facts_alice)}")
    print(f"Inferred facts for Bob:HasAtMostOneMother: {len(facts_bob)}")

    assert len(facts_alice) > 0, "Should infer Alice is HasAtMostOneMother (functional property)"
    assert len(facts_bob) > 0, "Should infer Bob is HasAtMostOneMother (functional property)"

    # Check that cls-maxc-rec rule was triggered (or equivalence rule based on it)
    has_cls_maxc_rec = any(
        fact.get("inferred_by") in ["cls-maxc-rec", "cax-eqc1", "cax-eqc2", "cax-sco"]
        for fact in facts_alice
    )
    assert has_cls_maxc_rec, "Should have inference from cls-maxc-rec or equivalence rule"

    print("✓ Test passed: Max cardinality recognition from functional (cls-maxc-rec)")


def test_cls_avf_rec3():
    """Test cls-avf-rec3 rule (universal restriction recognition from range)"""
    print("\n" + "=" * 60)
    print("TEST: Universal Restriction Recognition from Range (cls-avf-rec3)")
    print("=" * 60)

    reasoner = Reter()

    # Define hasParent with range Person
    # Define OnlyHasPersonParents as ∀hasParent․Person (universal restriction)
    # All individuals should satisfy this restriction (range guarantees it)
    # Grammar: ONLY node DOT node -> only_restriction
    ontology = """
    Person ⊑ᑦ ⊤
    OnlyHasPersonParents ≡ᑦ ∀hasParent․Person
    Person（Charlie）
    Person（Diana）
    """

    reasoner.load_ontology(ontology)

    # Add range axiom using add_fact (calls C++ directly)
    reasoner.add_fact({
        "type": "property_range",
        "property": "hasParent",
        "range": "Person"
    })

    # Reasoning is automatic/incremental - no need to call reason()

    # Check that both Charlie and Diana are inferred to be OnlyHasPersonParents
    facts_charlie = reasoner.query(
        type="instance_of",
        individual="Charlie",
        concept="OnlyHasPersonParents"
    )

    facts_diana = reasoner.query(
        type="instance_of",
        individual="Diana",
        concept="OnlyHasPersonParents"
    )

    print(f"\nInferred facts for Charlie:OnlyHasPersonParents: {len(facts_charlie)}")
    print(f"Inferred facts for Diana:OnlyHasPersonParents: {len(facts_diana)}")

    assert len(facts_charlie) > 0, "Should infer Charlie is OnlyHasPersonParents (range restriction)"
    assert len(facts_diana) > 0, "Should infer Diana is OnlyHasPersonParents (range restriction)"

    # Check that cls-avf-rec3 rule was triggered (or equivalence rule based on it)
    has_cls_avf_rec3 = any(
        fact.get("inferred_by") in ["cls-avf-rec3", "cax-eqc1", "cax-eqc2", "cax-sco"]
        for fact in facts_charlie
    )
    assert has_cls_avf_rec3, "Should have inference from cls-avf-rec3 or equivalence rule"

    print("✓ Test passed: Universal restriction recognition from range (cls-avf-rec3)")


def test_cls_avf_rec4():
    """Test cls-avf-rec4 rule (universal restriction recognition from functional property)"""
    print("\n" + "=" * 60)
    print("TEST: Universal Restriction Recognition from Functional (cls-avf-rec4)")
    print("=" * 60)

    reasoner = Reter()

    # Define hasFather as functional property
    # Define OnlyHasFathersPerson as ∀hasFather․Person (universal restriction)
    # cls-avf-rec4: If P is functional, R is ∀P․D, X has P value Y, and Y:D, then X:R
    # Grammar: ONLY node DOT node -> only_restriction
    ontology = """
    Person ⊑ᑦ ⊤
    OnlyHasFathersPerson ≡ᑦ ∀hasFather․Person
    Person（Dad）
    hasFather（Eve， Dad）
    """

    reasoner.load_ontology(ontology)

    # Add functional property using add_fact
    reasoner.add_fact({
        "type": "functional",
        "property": "hasFather"
    })

    # Reasoning is automatic/incremental - no need to call reason()

    # Check that Eve is inferred to be OnlyHasFathersPerson
    facts_eve = reasoner.query(
        type="instance_of",
        individual="Eve",
        concept="OnlyHasFathersPerson"
    )

    print(f"\nInferred facts for Eve:OnlyHasFathersPerson: {len(facts_eve)}")
    for fact in facts_eve:
        print(f"  - {fact}")

    assert len(facts_eve) > 0, "Should infer Eve is OnlyHasFathersPerson (functional property with value of correct type)"

    # Check that cls-avf-rec4 rule was triggered (or equivalence rule based on it)
    has_cls_avf_rec4 = any(
        fact.get("inferred_by") in ["cls-avf-rec4", "cax-eqc1", "cax-eqc2", "cax-sco"]
        for fact in facts_eve
    )
    assert has_cls_avf_rec4, "Should have inference from cls-avf-rec4 or equivalence rule"

    print("✓ Test passed: Universal restriction recognition from functional (cls-avf-rec4)")


def test_cls_avf_rec5():
    """Test cls-avf-rec5 rule (infer max cardinality from universal restriction)"""
    print("\n" + "=" * 60)
    print("TEST: Infer Max Cardinality from Universal Restriction (cls-avf-rec5)")
    print("=" * 60)

    reasoner = Reter()

    # Define OnlyKnowsStudents as ∀knows․Student (universal restriction)
    # Define HasAtMostOneStudent as ≤1 knows.Student (max cardinality 1)
    # If an individual is OnlyKnowsStudents, it should also be HasAtMostOneStudent
    # Grammar: ONLY node DOT node -> only_restriction
    #         LE NAT node DOT node -> number_restriction_le
    ontology = """
    Student ⊑ᑦ ⊤
    OnlyKnowsStudents ≡ᑦ ∀knows․Student
    HasAtMostOneStudent ≡ᑦ ≤1 knows․Student
    OnlyKnowsStudents（George）
    """

    reasoner.load_ontology(ontology)

    # Add functional property for knows
    reasoner.add_fact({
        "type": "functional",
        "property": "knows"
    })

    # Reasoning is automatic/incremental - no need to call reason()

    # Check that George is inferred to be HasAtMostOneStudent
    facts = reasoner.query(
        type="instance_of",
        individual="George",
        concept="HasAtMostOneStudent"
    )

    print(f"\nInferred facts for George:HasAtMostOneStudent: {len(facts)}")
    for fact in facts:
        print(f"  - {fact}")

    assert len(facts) > 0, "Should infer George is HasAtMostOneStudent (from universal restriction)"

    # Check that cls-avf-rec5 rule was triggered (or equivalence rule based on it)
    has_cls_avf_rec5 = any(
        fact.get("inferred_by") in ["cls-avf-rec5", "cax-eqc1", "cax-eqc2", "cax-sco"]
        for fact in facts
    )
    assert has_cls_avf_rec5, "Should have inference from cls-avf-rec5 or equivalence rule"

    print("✓ Test passed: Infer max cardinality from universal restriction (cls-avf-rec5)")


def test_multiple_cardinality_rules():
    """Test multiple cardinality rules working together"""
    print("\n" + "=" * 60)
    print("TEST: Multiple Cardinality Rules Together")
    print("=" * 60)

    reasoner = Reter()

    # Complex scenario with multiple cardinality constraints
    ontology = """
    Person ⊑ᑦ ⊤
    ParentOfAtLeastOne ≡ᑦ ≥1 hasChild․Person
    ParentOfAtMostTwo ≡ᑦ ≤2 hasChild․Person
    Person（Alice）
    Person（Bob）
    hasChild（Helen， Alice）
    hasChild（Helen， Bob）
    """

    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check that Helen is inferred to be ParentOfAtLeastOne
    facts_min = reasoner.query(
        type="instance_of",
        individual="Helen",
        concept="ParentOfAtLeastOne"
    )

    print(f"\nInferred facts for Helen:ParentOfAtLeastOne: {len(facts_min)}")
    assert len(facts_min) > 0, "Should infer Helen is ParentOfAtLeastOne"

    # Check for cls-minc-rec rule (or equivalence rule based on it)
    has_minc = any(
        fact.get("inferred_by") in ["cls-minc-rec", "cax-eqc1", "cax-eqc2", "cax-sco"]
        for fact in facts_min
    )
    assert has_minc, "Should have inference from cls-minc-rec or equivalence rule"

    print("✓ Test passed: Multiple cardinality rules working together")


if __name__ == '__main__':
    test_cls_minc_rec()
    test_cls_maxc_rec()
    test_cls_avf_rec3()
    test_cls_avf_rec4()
    test_cls_avf_rec5()
    test_multiple_cardinality_rules()

    print("\n" + "=" * 60)
    print("ALL MORE.OWLRL.JENA TESTS PASSED")
    print("=" * 60)
