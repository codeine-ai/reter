"""Debug test for sameAs facts"""
import pytest
import sys
sys.path.insert(0, 'D:/ROOT/reter/rete_cpp')
from reter import owl_rete_cpp

def test_sameas_debug():
    """Debug: Alice ﹦ Bob fact type"""
    net = owl_rete_cpp.ReteNetwork()

    print("\n=== Loading Alice ﹦ Bob ===")
    net.load_ontology_from_string("Alice ﹦ Bob")

    # Get all facts
    fact_list = net.get_all_facts()
    print(f"\n=== All facts: {len(fact_list)} ===")

    for i, f in enumerate(fact_list):
        print(f"{i}: {f}")

    # Check for same_as facts
    same_facts = [f for f in fact_list if f.get('type') == 'same_as']
    print(f"\n=== same_as facts: {len(same_facts)} ===")
    for f in same_facts:
        print(f"  {f}")

    # Try correct query
    print("\n=== Query with same_as ===")
    results = net.query({"type": "same_as", "ind1": "Alice", "ind2": "Bob"})
    print(f"Result: {len(results)} rows")

if __name__ == "__main__":
    test_sameas_debug()
