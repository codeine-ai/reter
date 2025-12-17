"""
Test DLModSimplifier patterns as RETE rules
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reter import Reter

def test_singleton_subsumption():
    """Test: {Alice} ⊑ {Bob} → Alice = Bob"""
    print("\n" + "=" * 60)
    print("TEST: Singleton Subsumption Simplification")
    print("Pattern: {Alice} ⊑ {Bob} → Alice = Bob")
    print("=" * 60)
    
    reasoner = Reter()
    ontology = "｛Alice｝ ⊑ᑦ ｛Bob｝"
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()
    
    # Check that Alice = Bob is inferred
    facts = reasoner.query(type="same_as", ind1="Alice", ind2="Bob")
    
    print(f"\nInferred sameAs facts: {len(facts)}")
    for fact in facts:
        print(f"  - {fact}")
    
    assert len(facts) > 0, "Should infer Alice sameAs Bob"
    assert any(f.get("inferred_by") == "simplify-singleton-sub" for f in facts), \
        "Should be inferred by simplify-singleton-sub rule"
    
    print("✓ Test passed: {Alice} ⊑ {Bob} → Alice = Bob")

def test_singleton_existential():
    """Test: {Alice} ⊑ ∃hasParent.{Bob} → hasParent(Alice, Bob)"""
    print("\n" + "=" * 60)
    print("TEST: Singleton Existential Simplification")
    print("Pattern: {Alice} ⊑ ∃hasParent.{Bob} → hasParent(Alice, Bob)")
    print("=" * 60)
    
    reasoner = Reter()
    ontology = "｛Alice｝ ⊑ᑦ ∃hasParent․｛Bob｝"
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()
    
    # Check that hasParent(Alice, Bob) is inferred
    facts = reasoner.query(
        type="role_assertion",
        subject="Alice",
        role="hasParent",
        object="Bob"
    )
    
    print(f"\nInferred role assertions: {len(facts)}")
    for fact in facts:
        print(f"  - {fact}")
    
    assert len(facts) > 0, "Should infer hasParent(Alice, Bob)"
    assert any(f.get("inferred_by") == "simplify-singleton-exists" for f in facts), \
        "Should be inferred by simplify-singleton-exists rule"
    
    print("✓ Test passed: {Alice} ⊑ ∃hasParent.{Bob} → hasParent(Alice, Bob)")

def test_inverse_role_normalization():
    """Test: hasChild⁻(Alice, Bob) → hasChild(Bob, Alice)"""
    print("\n" + "=" * 60)
    print("TEST: Inverse Role Normalization (AST level)")
    print("Pattern: hasChild⁻(Alice, Bob) → hasChild(Bob, Alice)")
    print("=" * 60)
    
    reasoner = Reter()
    ontology = "hasChild⁻（Alice，Bob）"
    reasoner.load_ontology(ontology)
    
    # Check that hasChild(Bob, Alice) is created (normalized at AST level)
    facts = reasoner.query(
        type="role_assertion",
        subject="Bob",
        role="hasChild",
        object="Alice"
    )
    
    print(f"\nRole assertions: {len(facts)}")
    for fact in facts:
        print(f"  - {fact}")
    
    assert len(facts) > 0, "Should have hasChild(Bob, Alice)"
    
    print("✓ Test passed: hasChild⁻(Alice, Bob) → hasChild(Bob, Alice)")

def test_combined_simplifications():
    """Test multiple simplifications working together"""
    print("\n" + "=" * 60)
    print("TEST: Combined Simplifications")
    print("=" * 60)
    
    reasoner = Reter()
    ontology = """
    ｛Alice｝ ⊑ᑦ ∃hasParent․｛Bob｝
    ｛Bob｝ ⊑ᑦ ∃hasParent․｛Charlie｝
    ｛John｝ ⊑ᑦ ｛Alice｝
    hasParent ∘ hasParent ⊑ᴿ hasGrandparent
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()
    
    # Check that hasParent(Alice, Bob) is inferred
    facts1 = reasoner.query(
        type="role_assertion",
        subject="Alice",
        role="hasParent",
        object="Bob"
    )
    print(f"\nInferred hasParent(Alice, Bob): {len(facts1)}")
    assert len(facts1) > 0
    
    # Check that hasParent(Bob, Charlie) is inferred
    facts2 = reasoner.query(
        type="role_assertion",
        subject="Bob",
        role="hasParent",
        object="Charlie"
    )
    print(f"Inferred hasParent(Bob, Charlie): {len(facts2)}")
    assert len(facts2) > 0
    
    # Check that John = Alice is inferred
    facts3 = reasoner.query(type="same_as", ind1="John", ind2="Alice")
    print(f"Inferred John = Alice: {len(facts3)}")
    assert len(facts3) > 0
    
    # Check that hasGrandparent(Alice, Charlie) is inferred via property chain
    facts4 = reasoner.query(
        type="role_assertion",
        subject="Alice",
        role="hasGrandparent",
        object="Charlie"
    )
    print(f"Inferred hasGrandparent(Alice, Charlie): {len(facts4)}")
    assert len(facts4) > 0
    
    print("✓ Test passed: Combined simplifications")

if __name__ == '__main__':
    test_singleton_subsumption()
    test_singleton_existential()
    test_inverse_role_normalization()
    test_combined_simplifications()
    
    print("\n" + "=" * 60)
    print("ALL DLMOD SIMPLIFICATION TESTS PASSED")
    print("=" * 60)
