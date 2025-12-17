#!/usr/bin/env python3
"""
Simple Class Equivalence Test
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'rete_cpp'))
from reter import owl_rete_cpp

def test_class_equivalence():
    """Test 1.3: Class Equivalence - Human ≡ᑦ Person"""
    print("\n" + "="*80)
    print("TEST 2: Class Equivalence")
    print("="*80)

    net = owl_rete_cpp.ReteNetwork()
    print("Loading: Human ≡ᑦ Person")
    net.load_ontology_from_string("Human ≡ᑦ Person")
    print("Loading: Human（Alice）")
    net.load_ontology_from_string("Human（Alice）")

    print("Getting all facts...")
    all_facts = net.get_all_facts()
    print(f"Total facts: {len(all_facts)}")

    alice_person = [f for f in all_facts if f.get('type') == 'instance_of'
                    and f.get('individual') == 'Alice'
                    and f.get('concept') == 'Person']

    if len(alice_person) > 0:
        print("✓ PASS: Alice inferred as Person")
        return True
    else:
        print("✗ FAIL: Alice not inferred as Person")
        alice_facts = [f for f in all_facts if 'Alice' in str(f)]
        print(f"  Alice facts: {alice_facts[:10]}")
        return False

if __name__ == "__main__":
    exit(0 if test_class_equivalence() else 1)
