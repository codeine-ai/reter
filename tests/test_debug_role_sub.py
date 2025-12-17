"""Debug test to see what fact type role subsumption creates"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'rete_cpp'))

from reter_core import owl_rete_cpp

def test_role_subsumption_fact_type():
    """Check what fact type is created for role subsumption"""
    net = owl_rete_cpp.ReteNetwork()

    ontology = "hasParent ⊑ᴿ hasAncestor"
    net.load_ontology_from_string(ontology)

    facts = net.get_all_facts()
    print(f"\nTotal facts: {len(facts)}")

    # Print all unique fact types
    types = set(f.get('type') for f in facts if f.get('type'))
    print(f"All fact types: {sorted(types)}")

    # Print facts that might be role subsumption
    print("\nFacts that might be role subsumption:")
    for f in facts:
        fact_type = f.get('type', '')
        if 'sub' in fact_type.lower() or 'property' in fact_type.lower():
            print(f"  Type: {fact_type}")
            print(f"  Full fact: {dict(f)}")

if __name__ == '__main__':
    test_role_subsumption_fact_type()
