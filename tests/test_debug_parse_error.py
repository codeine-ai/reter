"""Debug test to check for parse errors"""
import pytest
import sys
sys.path.insert(0, 'D:/ROOT/reter/rete_cpp')
from reter import owl_rete_cpp

def test_parse_alldifferent():
    """Debug: Check if parse error occurs"""
    net = owl_rete_cpp.ReteNetwork()
    try:
        net.load_ontology_from_string("≠｛Alice，Bob｝")
        print("\n✓ No parse error")
    except RuntimeError as e:
        print(f"\n✗ Parse error: {e}")
        raise

    facts = net.get_all_facts()
    print(f"Facts created: {len(facts)}")

if __name__ == "__main__":
    test_parse_alldifferent()
