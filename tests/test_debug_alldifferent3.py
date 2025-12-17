"""Debug test for AllDifferent with single item"""
import pytest
import sys
sys.path.insert(0, 'D:/ROOT/reter/rete_cpp')
from reter_core import owl_rete_cpp

def test_alldifferent_single():
    """Debug: Single instance"""
    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string("≠｛Alice｝")
    facts = net.get_all_facts()
    print(f"\nFacts with single instance: {len(facts)}")
    for f in facts:
        print(f"  {f}")

def test_alldifferent_two():
    """Debug: Two instances"""
    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string("≠｛Alice，Bob｝")
    facts = net.get_all_facts()
    print(f"\nFacts with two instances: {len(facts)}")
    for f in facts:
        print(f"  {f}")

if __name__ == "__main__":
    test_alldifferent_single()
    test_alldifferent_two()
