"""Debug test for AllDifferent validation"""
import pytest
import sys
sys.path.insert(0, 'D:/ROOT/reter/rete_cpp')
from reter import owl_rete_cpp

def test_alldifferent_debug():
    """Debug: AllDifferent should detect violation"""
    net = owl_rete_cpp.ReteNetwork()

    print("\n=== Loading ≠｛Alice，Bob，Charlie｝ ===")
    net.load_ontology_from_string("≠｛Alice，Bob，Charlie｝")

    print("\n=== Loading Alice ﹦ Bob (violation) ===")
    net.load_ontology_from_string("Alice ﹦ Bob")

    # Get all facts
    fact_list = net.get_all_facts()
    print(f"\n=== All facts: {len(fact_list)} ===")

    for i, f in enumerate(fact_list):
        print(f"{i}: {f}")

    # Check for inconsistency facts
    errors = [f for f in fact_list if f.get('type') == 'inconsistency']
    print(f"\n=== Inconsistency facts: {len(errors)} ===")
    for e in errors:
        print(f"  {e}")

    # Check for different_from facts
    diff_facts = [f for f in fact_list if f.get('type') == 'different_from']
    print(f"\n=== different_from facts: {len(diff_facts)} ===")
    for d in diff_facts:
        print(f"  {d}")

    # Check for same_as facts
    same_facts = [f for f in fact_list if f.get('type') == 'same_as']
    print(f"\n=== same_as facts: {len(same_facts)} ===")
    for s in same_facts:
        print(f"  {s}")

    if len(errors) > 0:
        print("\n✓ Validation working!")
    else:
        print("\n✗ No inconsistency detected - template not firing")

if __name__ == "__main__":
    test_alldifferent_debug()
