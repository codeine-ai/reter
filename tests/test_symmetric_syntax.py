"""
Test if symmetric properties can be expressed as R ≣ R⁻
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reter import Reter

def test_symmetric_via_inverse_equivalence():
    print("\n" + "=" * 60)
    print("TEST: Symmetric via R ≣ R⁻")
    print("=" * 60)
    
    reasoner = Reter()
    
    # Define knows as symmetric using R ≣ R⁻
    ontology = """
    Person（Alice）
    Person（Bob）
    knows（Alice， Bob）
    knows ≡ᴿ knows⁻
    """
    
    reasoner.load_ontology(ontology)
    
    
    # Check if Bob knows Alice is inferred
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
        print("✓ Test passed: Symmetric property via R ≣ R⁻")
    else:
        print("✗ Test failed: Symmetric property not inferred")

if __name__ == '__main__':
    test_symmetric_via_inverse_equivalence()
