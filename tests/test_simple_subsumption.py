#!/usr/bin/env python3
"""
Simple Subsumption Test
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'rete_cpp'))
from reter_core import owl_rete_cpp

def test_subsumption():
    """Test 1.1: Subsumption (SubClassOf) - Dog ⊑ᑦ Animal"""
    print("\n" + "="*80)
    print("TEST 1: Subsumption (SubClassOf)")
    print("="*80)

    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string("Dog ⊑ᑦ Animal")
    net.load_ontology_from_string("Dog（Fido）")

    # Check if Fido is inferred to be an Animal
    all_facts = net.get_all_facts()
    fido_animal = [f for f in all_facts if f.get('type') == 'instance_of'
                   and f.get('individual') == 'Fido'
                   and f.get('concept') == 'Animal']

    if len(fido_animal) > 0:
        print("✓ PASS: Fido inferred as Animal")
        return True
    else:
        print("✗ FAIL: Fido not inferred as Animal")
        print(f"  Total facts: {len(all_facts)}")
        print(f"  Fido facts: {[f for f in all_facts if 'Fido' in str(f)][:5]}")
        return False

if __name__ == "__main__":
    exit(0 if test_subsumption() else 1)
