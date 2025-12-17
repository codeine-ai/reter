"""Debug test to check if subsumption with complex expressions creates correct facts"""
import pytest
import sys
sys.path.insert(0, 'D:/ROOT/reter/rete_cpp')
from reter import owl_rete_cpp

def test_subsumption_with_existential():
    """Test if Parent ⊑ᑦ ∃hasChild․Person creates the right facts"""
    net = owl_rete_cpp.ReteNetwork()

    try:
        # Note: Using U+2024 (ONE DOT LEADER '․') not ASCII period '.'
        net.load_ontology_from_string("Parent ⊑ᑦ ∃hasChild․Person")

        # Get all facts
        facts = net.get_all_facts()
        print(f"\n=== Total facts created: {len(facts)} ===\n")

        # Facts are already a list of dicts
        fact_list = facts
        for i, fact_dict in enumerate(fact_list):
            print(f"Fact {i}: {fact_dict}")

        # Check if subsumption fact exists
        subsumptions = [f for f in fact_list if f.get('type') == 'subsumption']
        print(f"\n=== Subsumption facts: {len(subsumptions)} ===")
        for s in subsumptions:
            print(f"  {s}")

        # Check if some_values_from fact exists
        restrictions = [f for f in fact_list if f.get('type') == 'some_values_from']
        print(f"\n=== Restriction facts: {len(restrictions)} ===")
        for r in restrictions:
            print(f"  {r}")

        assert len(subsumptions) > 0, "Should create subsumption fact"
        assert len(restrictions) > 0, "Should create some_values_from fact"

        print("\n✓ Test PASSED - Complex subsumption parsed correctly!")

    except RuntimeError as e:
        print(f"\n✗ Parse error: {e}")
        raise

if __name__ == "__main__":
    test_subsumption_with_existential()
