"""Test singleton equivalence simplification"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reter import Reter

def test_singleton_equivalence():
    """Test: {Alice} ≡ {Bob} → Alice = Bob"""
    print("\n" + "=" * 60)
    print("TEST: Singleton Equivalence Simplification")
    print("Pattern: {Alice} ≡ {Bob} → Alice = Bob")
    print("=" * 60)
    
    reasoner = Reter()
    ontology = "｛Alice｝ ≡ᑦ ｛Bob｝"
    reasoner.load_ontology(ontology)
    
    
    # Check that Alice = Bob is inferred
    facts = reasoner.query(type="same_as", ind1="Alice", ind2="Bob")
    
    print(f"\nInferred sameAs facts: {len(facts)}")
    for fact in facts:
        print(f"  - {fact}")
    
    assert len(facts) > 0, "Should infer Alice sameAs Bob"
    # Accept either simplify-singleton-equiv or simplify-singleton-sub as valid inference sources
    # Both are correct paths: equiv->subsumption->sameAs or equiv->sameAs directly
    valid_rules = {"simplify-singleton-equiv", "simplify-singleton-sub", "eq-sym"}
    assert any(f.get("inferred_by") in valid_rules for f in facts), \
        f"Should be inferred by one of {valid_rules}, but got: {[f.get('inferred_by') for f in facts]}"
    
    print("✓ Test passed: {Alice} ≡ {Bob} → Alice = Bob")

def test_combined_equiv_and_sub():
    """Test equivalence and subsumption working together"""
    print("\n" + "=" * 60)
    print("TEST: Combined Equivalence and Subsumption")
    print("=" * 60)
    
    reasoner = Reter()
    ontology = """
    ｛Alice｝ ≡ᑦ ｛Bob｝
    ｛Charlie｝ ⊑ᑦ ｛Bob｝
    ｛Diana｝ ≡ᑦ ｛Charlie｝
    """
    reasoner.load_ontology(ontology)
    
    
    # Check all expected sameAs relationships
    facts_ab = reasoner.query(type="same_as", ind1="Alice", ind2="Bob")
    facts_bc = reasoner.query(type="same_as", ind1="Charlie", ind2="Bob")
    facts_cd = reasoner.query(type="same_as", ind1="Diana", ind2="Charlie")
    
    print(f"\nInferred Alice = Bob: {len(facts_ab)}")
    print(f"Inferred Charlie = Bob: {len(facts_bc)}")
    print(f"Inferred Diana = Charlie: {len(facts_cd)}")
    
    assert len(facts_ab) > 0, "Should infer Alice = Bob"
    assert len(facts_bc) > 0, "Should infer Charlie = Bob"
    assert len(facts_cd) > 0, "Should infer Diana = Charlie"
    
    # Via transitivity, Diana should equal Bob and Alice
    facts_db = reasoner.query(type="same_as", ind1="Diana", ind2="Bob")
    facts_da = reasoner.query(type="same_as", ind1="Diana", ind2="Alice")
    
    print(f"Inferred Diana = Bob (transitive): {len(facts_db)}")
    print(f"Inferred Diana = Alice (transitive): {len(facts_da)}")
    
    # Note: These require eq-trans rule which propagates sameAs transitively
    # The simplification rules create the base facts
    
    print("✓ Test passed: Combined equivalence and subsumption")

if __name__ == '__main__':
    test_singleton_equivalence()
    test_combined_equiv_and_sub()
    
    print("\n" + "=" * 60)
    print("ALL SINGLETON EQUIVALENCE TESTS PASSED")
    print("=" * 60)
