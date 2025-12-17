"""Debug test for instance_of assertions"""
import pytest
import sys
sys.path.insert(0, 'D:/ROOT/reter/rete_cpp')
from reter import owl_rete_cpp

def test_instance_of_debug():
    """Debug: Person（Alice） should create instance_of fact"""
    net = owl_rete_cpp.ReteNetwork()

    print("\n=== Loading Person（Alice） ===")
    net.load_ontology_from_string("Person（Alice）")

    # Get all facts
    fact_list = net.get_all_facts()
    print(f"\n=== All facts: {len(fact_list)} ===")

    for i, f in enumerate(fact_list):
        print(f"{i}: {f}")

    # Check for instance_of facts
    instance_facts = [f for f in fact_list if f.get('type') == 'instance_of']
    print(f"\n=== instance_of facts: {len(instance_facts)} ===")
    for f in instance_facts:
        print(f"  {f}")

    # Try the query
    print("\n=== Testing query ===")
    results = net.query({"type": "instance_of", "individual": "Alice", "concept": "Person"})
    print(f"Result: {len(results)} rows")

if __name__ == "__main__":
    test_instance_of_debug()
