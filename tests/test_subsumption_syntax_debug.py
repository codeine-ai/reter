"""Debug test for subsumption syntax with complex class expressions"""
import pytest
import sys
sys.path.insert(0, 'D:/ROOT/reter/rete_cpp')
from reter_core import owl_rete_cpp

def test_simple_subsumption_works():
    """Verify simple subsumption works (baseline)"""
    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string("Dog ⊑ᑦ Animal")
    facts = net.get_all_facts()
    assert len(facts) > 0, "Simple subsumption should work"

def test_subsumption_plain_symbol():
    """Test if plain ⊑ (without subscript) works with complex expressions"""
    net = owl_rete_cpp.ReteNetwork()
    try:
        net.load_ontology_from_string("Parent ⊑ ∃hasChild․Person")
        facts = net.get_all_facts()
        print(f"SUCCESS with ⊑: {len(facts)} facts")
        return True
    except RuntimeError as e:
        print(f"FAILED with ⊑: {e}")
        return False

def test_subsumption_subscript_c_with_existential():
    """Test if ⊑ᑦ works with existential restriction"""
    net = owl_rete_cpp.ReteNetwork()
    try:
        net.load_ontology_from_string("Parent ⊑ᑦ ∃hasChild․Person")
        facts = net.get_all_facts()
        print(f"SUCCESS with ⊑ᑦ + existential: {len(facts)} facts")
        return True
    except RuntimeError as e:
        print(f"FAILED with ⊑ᑦ + existential: {e}")
        return False

if __name__ == "__main__":
    print("Test 1: Simple subsumption")
    test_simple_subsumption_works()

    print("\nTest 2: Plain ⊑ with existential")
    test_subsumption_plain_symbol()

    print("\nTest 3: ⊑ᑦ with existential")
    test_subsumption_subscript_c_with_existential()
