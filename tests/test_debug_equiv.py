#!/usr/bin/env python3
"""Debug test for equivalence list"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rete_cpp'))
from reter import owl_rete_cpp

def test_debug_equivalence_list():
    # Test equivalence list
    net = owl_rete_cpp.ReteNetwork()
    print("\n=== LOADING EQUIVALENCE LIST ===")
    net.load_ontology_from_string("≡ᑦ（Human，Person，Individual）")

    print("\n=== LOADING INSTANCE ===")
    net.load_ontology_from_string("Human（Bob）")

    # Get all facts
    all_facts = net.get_all_facts()
    print(f"\nTotal facts: {len(all_facts)}")

    # Print equivalence facts
    print("\n=== EQUIVALENCE FACTS ===")
    equiv_facts = [f for f in all_facts if f.get('type') == 'equivalence']
    for f in equiv_facts:
        print(f"  {f.get('concept1', '')} = {f.get('concept2', '')}")

    # Print instance_of facts
    print("\n=== INSTANCE_OF FACTS ===")
    instance_facts = [f for f in all_facts if f.get('type') == 'instance_of']
    for f in instance_facts:
        ind = f.get('individual', '')
        concept = f.get('concept', '')
        inferred = f.get('inferred', 'false')
        inferred_by = f.get('inferred_by', '')
        if inferred == 'true':
            print(f"  {ind} : {concept} (inferred by {inferred_by})")
        else:
            print(f"  {ind} : {concept} (asserted)")

    # Check if Bob is Individual
    print("\n=== INFERENCE CHECK ===")
    results = net.query({"type": "instance_of", "individual": "Bob", "concept": "Individual"})
    print(f"Bob as Individual: {len(results)} results")

    if len(results) == 0:
        print("\n✗ FAILED: Bob should be inferred as Individual")
        print("\nExpected inference chain:")
        print("  1. Bob : Human (asserted)")
        print("  2. Human ≡ Individual (from equivalence list)")
        print("  3. Bob : Individual (should be inferred by cax-eqc1 or cax-eqc2)")
    else:
        print("\n✓ PASSED: Bob is inferred as Individual")
