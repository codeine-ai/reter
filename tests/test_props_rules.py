"""
Test for OWL 2 RL property rules from props.owlrl.jena
All tests use DL syntax (LARK grammar) instead of add_fact()
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reter import Reter


def test_prp_dom():
    """Test prp-dom rule (property domain inference)"""
    print("\n" + "=" * 60)
    print("TEST: Property Domain Inference (prp-dom)")
    print("=" * 60)

    reasoner = Reter()

    # Define hasParent with domain Person
    # If John hasParent Mary, then John must be a Person
    ontology = """
    Person ⊑ᑦ ⊤
    hasParent（John， Mary）
    """

    reasoner.load_ontology(ontology)

    # Add domain axiom using add_fact (not part of DL syntax yet)
    reasoner.add_fact({
        "type": "property_domain",
        "property": "hasParent",
        "domain": "Person"
    })

    # Reasoning is automatic/incremental - no need to call reason()

    # Check that John is inferred to be a Person
    facts = reasoner.query(
        type="instance_of",
        individual="John",
        concept="Person"
    )

    print(f"\nInferred facts for John:Person: {len(facts)}")
    for fact in facts:
        print(f"  - {fact}")

    assert len(facts) > 0, "Should infer John is a Person (property domain)"

    # Check that prp-dom rule was triggered
    has_prp_dom = any(
        fact.get("inferred_by") == "prp-dom"
        for fact in facts
    )
    assert has_prp_dom, "Should have inference from prp-dom rule"

    print("✓ Test passed: Property domain inference (prp-dom)")


def test_prp_rng():
    """Test prp-rng rule (property range inference)"""
    print("\n" + "=" * 60)
    print("TEST: Property Range Inference (prp-rng)")
    print("=" * 60)

    reasoner = Reter()

    # Define hasParent with range Person
    # If John hasParent Mary, then Mary must be a Person
    ontology = """
    Person ⊑ᑦ ⊤
    hasParent（John， Mary）
    """

    reasoner.load_ontology(ontology)

    # Add range axiom using add_fact
    reasoner.add_fact({
        "type": "property_range",
        "property": "hasParent",
        "range": "Person"
    })

    # Reasoning is automatic/incremental - no need to call reason()

    # Check that Mary is inferred to be a Person
    facts = reasoner.query(
        type="instance_of",
        individual="Mary",
        concept="Person"
    )

    print(f"\nInferred facts for Mary:Person: {len(facts)}")
    for fact in facts:
        print(f"  - {fact}")

    assert len(facts) > 0, "Should infer Mary is a Person (property range)"

    # Check that prp-rng rule was triggered
    has_prp_rng = any(
        fact.get("inferred_by") == "prp-rng"
        for fact in facts
    )
    assert has_prp_rng, "Should have inference from prp-rng rule"

    print("✓ Test passed: Property range inference (prp-rng)")


def test_prp_fp():
    """Test prp-fp rule (functional property infers sameAs)"""
    print("\n" + "=" * 60)
    print("TEST: Functional Property Infers SameAs (prp-fp)")
    print("=" * 60)

    reasoner = Reter()

    # Define hasMother as functional property
    # If Alice hasMother MotherA and Alice hasMother MotherB, then MotherA = MotherB
    ontology = """
    Person（Alice）
    Person（MotherA）
    Person（MotherB）
    hasMother（Alice， MotherA）
    hasMother（Alice， MotherB）
    """

    reasoner.load_ontology(ontology)

    # Add functional property declaration
    reasoner.add_fact({
        "type": "functional",
        "property": "hasMother"
    })

    # Reasoning is automatic/incremental - no need to call reason()

    # Check that MotherA and MotherB are inferred to be the same
    facts = reasoner.query(
        type="same_as",
        ind1="MotherA",
        ind2="MotherB"
    )

    print(f"\nInferred sameAs facts for MotherA=MotherB: {len(facts)}")
    for fact in facts:
        print(f"  - {fact}")

    assert len(facts) > 0, "Should infer MotherA sameAs MotherB (functional property)"

    # Check that prp-fp rule was triggered
    has_prp_fp = any(
        fact.get("inferred_by") == "prp-fp"
        for fact in facts
    )
    assert has_prp_fp, "Should have inference from prp-fp rule"

    print("✓ Test passed: Functional property infers sameAs (prp-fp)")


def test_prp_ifp():
    """Test prp-ifp rule (inverse functional property infers sameAs)"""
    print("\n" + "=" * 60)
    print("TEST: Inverse Functional Property Infers SameAs (prp-ifp)")
    print("=" * 60)

    reasoner = Reter()

    # Define hasSocialSecurityNumber as inverse functional property
    # If PersonA hasSSN "123" and PersonB hasSSN "123", then PersonA = PersonB
    ontology = """
    Person（PersonA）
    Person（PersonB）
    hasSSN（PersonA， SSN123）
    hasSSN（PersonB， SSN123）
    """

    reasoner.load_ontology(ontology)

    # Add inverse functional property declaration
    reasoner.add_fact({
        "type": "inverse_functional",
        "property": "hasSSN"
    })

    # Reasoning is automatic/incremental - no need to call reason()

    # Check that PersonA and PersonB are inferred to be the same
    facts = reasoner.query(
        type="same_as",
        ind1="PersonA",
        ind2="PersonB"
    )

    print(f"\nInferred sameAs facts for PersonA=PersonB: {len(facts)}")
    for fact in facts:
        print(f"  - {fact}")

    assert len(facts) > 0, "Should infer PersonA sameAs PersonB (inverse functional property)"

    # Check that prp-ifp rule was triggered
    has_prp_ifp = any(
        fact.get("inferred_by") == "prp-ifp"
        for fact in facts
    )
    assert has_prp_ifp, "Should have inference from prp-ifp rule"

    print("✓ Test passed: Inverse functional property infers sameAs (prp-ifp)")


def test_prp_symp():
    """Test prp-symp rule (symmetric property)"""
    print("\n" + "=" * 60)
    print("TEST: Symmetric Property (prp-symp)")
    print("=" * 60)

    reasoner = Reter()

    # Define knows as symmetric property using R ≣ R⁻
    # If Alice knows Bob, then Bob knows Alice
    ontology = """
    Person（Alice）
    Person（Bob）
    knows（Alice， Bob）
    knows ≡ᴿ knows⁻
    """

    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check that Bob knows Alice is inferred
    facts = reasoner.query(
        type="role_assertion",
        subject="Bob",
        role="knows",
        object="Alice"
    )

    print(f"\nInferred facts for Bob knows Alice: {len(facts)}")
    for fact in facts:
        print(f"  - {fact}")

    assert len(facts) > 0, "Should infer Bob knows Alice (symmetric property)"

    # Check that prp-symp or prp-inv2 rule was triggered
    # (When R ≡ R⁻, symmetry can be inferred via prp-inv2, which is logically equivalent)
    # Template rules have names like "prp-symp-knows", so check if inferred_by contains the rule name
    has_inference = any(
        "prp-symp" in fact.get("inferred_by", "") or "prp-inv2" in fact.get("inferred_by", "")
        for fact in facts
    )
    assert has_inference, "Should have inference from prp-symp or prp-inv2 rule"

    print("✓ Test passed: Symmetric property (prp-symp)")


def test_prp_trp():
    """Test prp-trp rule (transitive property)"""
    print("\n" + "=" * 60)
    print("TEST: Transitive Property (prp-trp)")
    print("=" * 60)

    reasoner = Reter()

    # Define hasAncestor as transitive property
    # If Alice hasAncestor Bob and Bob hasAncestor Charlie, then Alice hasAncestor Charlie
    ontology = """
    Person（Alice）
    Person（Bob）
    Person（Charlie）
    hasAncestor（Alice， Bob）
    hasAncestor（Bob， Charlie）
    """

    reasoner.load_ontology(ontology)

    # Add transitive property declaration
    reasoner.add_fact({
        "type": "transitive_property",
        "property": "hasAncestor"
    })

    # Reasoning is automatic/incremental - no need to call reason()

    # Check that Alice hasAncestor Charlie is inferred
    facts = reasoner.query(
        type="role_assertion",
        subject="Alice",
        role="hasAncestor",
        object="Charlie"
    )

    print(f"\nInferred facts for Alice hasAncestor Charlie: {len(facts)}")
    for fact in facts:
        print(f"  - {fact}")

    assert len(facts) > 0, "Should infer Alice hasAncestor Charlie (transitive property)"

    # Check that prp-trp rule was triggered
    has_prp_trp = any(
        fact.get("inferred_by") == "prp-trp"
        for fact in facts
    )
    assert has_prp_trp, "Should have inference from prp-trp rule"

    print("✓ Test passed: Transitive property (prp-trp)")


def test_prp_spo1():
    """Test prp-spo1 rule (property subsumption)"""
    print("\n" + "=" * 60)
    print("TEST: Property Subsumption (prp-spo1)")
    print("=" * 60)

    reasoner = Reter()

    # Define hasParent as subproperty of hasAncestor
    # If Alice hasParent Bob, then Alice hasAncestor Bob
    # Grammar: node SUBPROP node -> subproperty_axiom
    ontology = """
    Person（Alice）
    Person（Bob）
    hasParent ⊑ᴿ hasAncestor
    hasParent（Alice， Bob）
    """

    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check that Alice hasAncestor Bob is inferred
    facts = reasoner.query(
        type="role_assertion",
        subject="Alice",
        role="hasAncestor",
        object="Bob"
    )

    print(f"\nInferred facts for Alice hasAncestor Bob: {len(facts)}")
    for fact in facts:
        print(f"  - {fact}")

    assert len(facts) > 0, "Should infer Alice hasAncestor Bob (property subsumption)"

    # Check that prp-spo1 rule was triggered
    has_prp_spo1 = any(
        fact.get("inferred_by") == "prp-spo1"
        for fact in facts
    )
    assert has_prp_spo1, "Should have inference from prp-spo1 rule"

    print("✓ Test passed: Property subsumption (prp-spo1)")


def test_prp_eqp():
    """Test prp-eqp1 and prp-eqp2 rules (equivalent property)"""
    print("\n" + "=" * 60)
    print("TEST: Equivalent Property (prp-eqp1, prp-eqp2)")
    print("=" * 60)

    reasoner = Reter()

    # Define hasMother as equivalent to hasMom
    # If Alice hasMother Bob, then Alice hasMom Bob (and vice versa)
    # Grammar: node EQUIVPROP node -> equivalent_property_axiom
    ontology = """
    Person（Alice）
    Person（MotherMary）
    Person（Bob）
    Person（MotherJane）
    hasMother ≡ᴿ hasMom
    hasMother（Alice， MotherMary）
    hasMom（Bob， MotherJane）
    """

    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check that Alice hasMom MotherMary is inferred (prp-eqp1)
    facts1 = reasoner.query(
        type="role_assertion",
        subject="Alice",
        role="hasMom",
        object="MotherMary"
    )

    print(f"\nInferred facts for Alice hasMom MotherMary: {len(facts1)}")
    for fact in facts1:
        print(f"  - {fact}")

    assert len(facts1) > 0, "Should infer Alice hasMom MotherMary (prp-eqp1)"

    # Check that Bob hasMother MotherJane is inferred (prp-eqp2)
    facts2 = reasoner.query(
        type="role_assertion",
        subject="Bob",
        role="hasMother",
        object="MotherJane"
    )

    print(f"\nInferred facts for Bob hasMother MotherJane: {len(facts2)}")
    for fact in facts2:
        print(f"  - {fact}")

    assert len(facts2) > 0, "Should infer Bob hasMother MotherJane (prp-eqp2)"

    # Check that rules were triggered (prp-eqp creates sub_property, then prp-spo1 uses it)
    # So the final inferred_by might be prp-spo1, which is correct
    # Template rules have names like "prp-eqp1-hasMom-hasMother", so check if inferred_by contains the rule name
    # Note: prp-eqp1 and prp-eqp2 both may appear as "prp-eqp" in template names
    has_inference1 = any("prp-eqp" in fact.get("inferred_by", "") or "prp-spo1" in fact.get("inferred_by", "") for fact in facts1)
    has_inference2 = any("prp-eqp" in fact.get("inferred_by", "") or "prp-spo1" in fact.get("inferred_by", "") for fact in facts2)

    assert has_inference1, "Should have inference from prp-eqp1 or prp-spo1 rule"
    assert has_inference2, "Should have inference from prp-eqp2 or prp-spo1 rule"

    print("✓ Test passed: Equivalent property (prp-eqp1, prp-eqp2)")


def test_prp_inv():
    """Test prp-inv1 and prp-inv2 rules (inverse property)"""
    print("\n" + "=" * 60)
    print("TEST: Inverse Property (prp-inv1, prp-inv2)")
    print("=" * 60)

    reasoner = Reter()

    # Define hasChild as inverse of hasParent
    # If Alice hasChild Bob, then Bob hasParent Alice
    # If Charlie hasParent Diana, then Diana hasChild Charlie
    ontology = """
    Person（Alice）
    Person（Bob）
    Person（Charlie）
    Person（Diana）
    hasChild（Alice， Bob）
    hasParent（Charlie， Diana）
    """

    reasoner.load_ontology(ontology)

    # Add inverse property axiom using add_fact
    reasoner.add_fact({
        "type": "inverse",
        "property1": "hasChild",
        "property2": "hasParent"
    })

    # Reasoning is automatic/incremental - no need to call reason()

    # Check that Bob hasParent Alice is inferred (prp-inv1)
    facts1 = reasoner.query(
        type="role_assertion",
        subject="Bob",
        role="hasParent",
        object="Alice"
    )

    print(f"\nInferred facts for Bob hasParent Alice: {len(facts1)}")
    for fact in facts1:
        print(f"  - {fact}")

    assert len(facts1) > 0, "Should infer Bob hasParent Alice (prp-inv1)"

    # Check that Diana hasChild Charlie is inferred (prp-inv2)
    facts2 = reasoner.query(
        type="role_assertion",
        subject="Diana",
        role="hasChild",
        object="Charlie"
    )

    print(f"\nInferred facts for Diana hasChild Charlie: {len(facts2)}")
    for fact in facts2:
        print(f"  - {fact}")

    assert len(facts2) > 0, "Should infer Diana hasChild Charlie (prp-inv2)"

    # Check that both rules were triggered
    has_prp_inv1 = any(fact.get("inferred_by") == "prp-inv1" for fact in facts1)
    has_prp_inv2 = any(fact.get("inferred_by") == "prp-inv2" for fact in facts2)

    assert has_prp_inv1, "Should have inference from prp-inv1 rule"
    assert has_prp_inv2, "Should have inference from prp-inv2 rule"

    print("✓ Test passed: Inverse property (prp-inv1, prp-inv2)")


def test_complex_property_interactions():
    """Test multiple property rules working together

    Tests that symmetric + transitive properties work correctly without
    causing infinite loops. This combination requires proper refraction
    (preventing duplicate production firings) and token deduplication
    in the RETE network.
    """
    print("\n" + "=" * 60)
    print("TEST: Complex Property Rule Interactions")
    print("=" * 60)

    reasoner = Reter()

    # Complex scenario: transitive + symmetric + domain/range
    ontology = """
    Person ⊑ᑦ ⊤
    Person（Alice）
    Person（Bob）
    knows（Alice， Bob）
    knows（Bob， Charlie）
    knows ≡ᴿ knows⁻
    knows ∘ knows ⊑ᴿ knows
    """

    reasoner.load_ontology(ontology)

    # Add domain and range (not yet in LARK syntax)
    reasoner.add_fact({
        "type": "property_domain",
        "property": "knows",
        "domain": "Person"
    })
    reasoner.add_fact({
        "type": "property_range",
        "property": "knows",
        "range": "Person"
    })

    # Reasoning is automatic/incremental - no need to call reason()

    # Check that Charlie is inferred to be a Person (range)
    facts_charlie = reasoner.query(
        type="instance_of",
        individual="Charlie",
        concept="Person"
    )
    print(f"\nInferred facts for Charlie:Person: {len(facts_charlie)}")
    assert len(facts_charlie) > 0, "Should infer Charlie is a Person (range)"

    # Check that Alice knows Charlie (transitivity)
    facts_knows = reasoner.query(
        type="role_assertion",
        subject="Alice",
        role="knows",
        object="Charlie"
    )
    print(f"Inferred facts for Alice knows Charlie: {len(facts_knows)}")
    assert len(facts_knows) > 0, "Should infer Alice knows Charlie (transitive)"

    # Check that Bob knows Alice (symmetric)
    facts_symmetric = reasoner.query(
        type="role_assertion",
        subject="Bob",
        role="knows",
        object="Alice"
    )
    print(f"Inferred facts for Bob knows Alice: {len(facts_symmetric)}")
    assert len(facts_symmetric) > 0, "Should infer Bob knows Alice (symmetric)"

    print("✓ Test passed: Complex property rule interactions")


if __name__ == '__main__':
    test_prp_dom()
    test_prp_rng()
    test_prp_fp()
    test_prp_ifp()
    test_prp_symp()
    test_prp_trp()
    test_prp_spo1()
    test_prp_eqp()
    test_prp_inv()
    test_complex_property_interactions()

    print("\n" + "=" * 60)
    print("ALL PROPS.OWLRL.JENA TESTS PASSED")
    print("=" * 60)
