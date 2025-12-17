"""
Test symmetric property via role equivalence: knows ≣ knows⁻
This is different from: knows ≣ knows⁻ (property equivalence)
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reter import Reter

def test_role_equivalence_symmetric():
    """Test: R ≣ R⁻ → R is symmetric (via role equivalence)"""
    print("\n" + "=" * 60)
    print("TEST: Symmetric via Role Equivalence R ≣ R⁻")
    print("=" * 60)
    
    reasoner = Reter()
    
    # Using role equivalence (EQVR operator ≣)
    ontology = """
    Person（Alice）
    Person（Bob）
    knows（Alice， Bob）
    knows ≡ᴿ knows⁻
    """
    
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()
    
    # Check all facts
    all_facts = reasoner.query()
    print(f"\nTotal facts: {len(all_facts)}")
    for fact in all_facts:
        if 'symmetric' in str(fact.get('type', '')):
            print(f"  SYMMETRIC: {fact}")
        if fact.get('type') == 'equivalent_property':
            print(f"  EQUIV_PROP: {fact}")
    
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
    
    if len(facts) > 0:
        print("✓ Test passed: R ≣ R⁻ works for symmetric")
    else:
        print("✗ Test failed: R ≣ R⁻ doesn't create symmetric inference")
    
    return len(facts) > 0

if __name__ == '__main__':
    result = test_role_equivalence_symmetric()
    if result:
        print("\n✓ Symmetric via role equivalence already works!")
    else:
        print("\n✗ Need to enhance symmetric detection")
