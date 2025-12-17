"""
Test functional and inverse functional property detection
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reter import Reter

def test_functional():
    """Test: ⊤ ⊑ ≤1R.⊤ means R is functional"""
    print("=" * 60)
    print("TEST: Functional Property Detection - ⊤ ⊑ ≤1hasSSN.⊤")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    ⊤ ⊑ᑦ ≤1 hasSSN․⊤
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check that functional fact was created
    func_facts = reasoner.query(type="functional", property="hasSSN")
    print(f"Functional facts detected: {len(func_facts)}")
    if func_facts:
        print(f"  hasSSN is functional")
        print(f"  Inferred by: {func_facts[0].get('inferred_by')}")

    success = len(func_facts) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_inverse_functional():
    """Test: ⊤ ⊑ ≤1R⁻.⊤ means R is inverse functional"""
    print("\n" + "=" * 60)
    print("TEST: Inverse Functional - ⊤ ⊑ ≤1hasSSN⁻.⊤")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    ⊤ ⊑ᑦ ≤1 hasSSN⁻․⊤
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check that inverse functional fact was created
    inv_func_facts = reasoner.query(type="inverse_functional", property="hasSSN")
    print(f"Inverse functional facts detected: {len(inv_func_facts)}")
    if inv_func_facts:
        print(f"  hasSSN is inverse functional")
        print(f"  Inferred by: {inv_func_facts[0].get('inferred_by')}")

    success = len(inv_func_facts) > 0
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_both():
    """Test both functional and inverse functional together"""
    print("\n" + "=" * 60)
    print("TEST: Both Functional Properties")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    ⊤ ⊑ᑦ ≤1 hasSSN․⊤
    ⊤ ⊑ᑦ ≤1 hasEmail⁻․⊤
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check functional
    func_facts = reasoner.query(type="functional")
    print(f"Functional properties: {len(func_facts)}")
    for f in func_facts:
        print(f"  {f.get('property')} is functional")

    # Check inverse functional
    inv_func_facts = reasoner.query(type="inverse_functional")
    print(f"Inverse functional properties: {len(inv_func_facts)}")
    for f in inv_func_facts:
        print(f"  {f.get('property')} is inverse functional")

    success = len(func_facts) == 1 and len(inv_func_facts) == 1
    print(f"{'✓ PASS' if success else '✗ FAIL'}")
    return success

if __name__ == "__main__":
    results = {
        "Functional Detection": test_functional(),
        "Inverse Functional Detection": test_inverse_functional(),
        "Both Together": test_both()
    }

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
