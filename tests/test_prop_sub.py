#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'rete_cpp'))
from reter_core import owl_rete_cpp

def test_property_subsumption():
    """Test 3.1: Object Property Subsumption - hasParent ⊑ᴿ hasAncestor"""
    print("\n" + "="*80)
    print("TEST 4: Object Property Subsumption")
    print("="*80)

    net = owl_rete_cpp.ReteNetwork()
    print("Loading: hasParent ⊑ᴿ hasAncestor")
    net.load_ontology_from_string("hasParent ⊑ᴿ hasAncestor")
    print("Loading: hasParent（Alice，Bob）")
    net.load_ontology_from_string("hasParent（Alice，Bob）")

    print("Getting all facts...")
    all_facts = net.get_all_facts()
    print(f"Total facts: {len(all_facts)}")

    alice_ancestor = [f for f in all_facts if f.get('type') == 'role_assertion'
                      and f.get('subject') == 'Alice'
                      and f.get('role') == 'hasAncestor'
                      and f.get('object') == 'Bob']

    if len(alice_ancestor) > 0:
        print("✓ PASS: hasAncestor inferred from hasParent")
        return True
    else:
        print("✗ FAIL: hasAncestor not inferred")
        print(f"  Role assertions: {[f for f in all_facts if f.get('type') == 'role_assertion'][:5]}")
        return False

if __name__ == "__main__":
    exit(0 if test_property_subsumption() else 1)
