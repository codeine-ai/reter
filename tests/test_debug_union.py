"""Debug test for union inference"""
import pytest
import sys
sys.path.insert(0, 'D:/ROOT/reter/rete_cpp')
from reter_core import owl_rete_cpp

def test_union_debug():
    """Debug: Parent ≡ᑦ Mother ⊔ Father should infer Parent from Mother"""
    net = owl_rete_cpp.ReteNetwork()

    print("\n=== Loading Parent ≡ᑦ Mother ⊔ Father ===")
    net.load_ontology_from_string("Parent ≡ᑦ Mother ⊔ Father")

    print("\n=== Loading Mother（Alice） ===")
    net.load_ontology_from_string("Mother（Alice）")

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

    # Query for Alice as Parent
    print("\n=== Query for Alice as Parent ===")
    results = net.query({"type": "instance_of", "individual": "Alice", "concept": "Parent"})
    print(f"Result: {len(results)} rows")
    if len(results) > 0:
        print("✓ Inference working!")
    else:
        print("✗ No inference - check if cls-uni template exists/fires")

if __name__ == "__main__":
    test_union_debug()
