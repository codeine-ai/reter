#!/usr/bin/env python3
"""
Test what fact types are generated for different equivalence statements
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'rete_cpp'))
from reter import owl_rete_cpp

def test_class_equivalence_facts():
    print("="*80)
    print("CLASS EQUIVALENCE: Human ≡ᑦ Person")
    print("="*80)
    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string("Human ≡ᑦ Person")

    all_facts = net.get_all_facts()
    for f in all_facts:
        fact_type = f.get('type')
        if 'equiv' in fact_type or fact_type in ['equivalence', 'role_equivalence', 'equivalent_property']:
            print(f"  Type: {fact_type}")
            for key in ['concept1', 'concept2', 'property1', 'property2', 'sub', 'sup']:
                val = f.get(key)
                if val:
                    print(f"    {key}: {val}")

def test_property_equivalence_facts():
    print("\n" + "="*80)
    print("PROPERTY EQUIVALENCE: hasSpouse ≡ᴿ marriedTo")
    print("="*80)
    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string("hasSpouse ≡ᴿ marriedTo")

    all_facts = net.get_all_facts()
    for f in all_facts:
        fact_type = f.get('type')
        if 'equiv' in fact_type or fact_type in ['equivalence', 'role_equivalence', 'equivalent_property']:
            print(f"  Type: {fact_type}")
            for key in ['concept1', 'concept2', 'property1', 'property2', 'sub', 'sup']:
                val = f.get(key)
                if val:
                    print(f"    {key}: {val}")

if __name__ == "__main__":
    test_class_equivalence_facts()
    test_property_equivalence_facts()
