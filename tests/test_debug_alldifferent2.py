"""Debug test for AllDifferent fact creation"""
import pytest
import sys
sys.path.insert(0, 'D:/ROOT/reter/rete_cpp')
from reter import owl_rete_cpp

def test_alldifferent_parsing():
    """Debug: What facts does AllDifferent create?"""
    net = owl_rete_cpp.ReteNetwork()

    print("\n=== Loading ≠｛Alice，Bob，Charlie｝ ===")
    net.load_ontology_from_string("≠｛Alice，Bob，Charlie｝")

    # Get all facts
    fact_list = net.get_all_facts()
    print(f"\n=== All facts: {len(fact_list)} ===")

    for i, f in enumerate(fact_list):
        print(f"{i}: {f}")

    # Check what types exist
    types = set(f.get('type') for f in fact_list if f.get('type'))
    print(f"\n=== Fact types: {types} ===")

def test_simple_different():
    """Debug: Simple different from"""
    net = owl_rete_cpp.ReteNetwork()

    print("\n=== Loading Alice ≠ Bob ===")
    net.load_ontology_from_string("Alice ≠ Bob")

    # Get all facts
    fact_list = net.get_all_facts()
    print(f"\n=== All facts: {len(fact_list)} ===")

    for i, f in enumerate(fact_list):
        print(f"{i}: {f}")

if __name__ == "__main__":
    test_alldifferent_parsing()
    print("\n" + "="*60)
    test_simple_different()
