#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'rete_cpp'))
from reter_core import owl_rete_cpp

def test_disjoint_classes():
    """Test 1.5: Disjoint Classes - ¬≡ᑦ（Male，Female）"""
    print("\n" + "="*80)
    print("TEST 3: Disjoint Classes")
    print("="*80)

    net = owl_rete_cpp.ReteNetwork()
    print("Loading disjoint declaration...")
    net.load_ontology_from_string("¬≡ᑦ（Male，Female）")
    print("Loading Male（Charlie）...")
    net.load_ontology_from_string("Male（Charlie）")
    print("Loading Female（Charlie）...")
    net.load_ontology_from_string("Female（Charlie）")

    print("Getting all facts...")
    all_facts = net.get_all_facts()
    print(f"Total facts: {len(all_facts)}")
    errors = [f for f in all_facts if f.get('type') == 'inconsistency']

    if len(errors) > 0:
        print("✓ PASS: Detected disjoint classes violation")
        for err in errors[:3]:
            print(f"  Error: {err.get('message', '')}")
        return True
    else:
        print("✗ FAIL: Should detect disjoint classes violation")
        return False

if __name__ == "__main__":
    exit(0 if test_disjoint_classes() else 1)
