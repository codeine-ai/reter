import pytest
from reter.owl_rete_cpp import ReteNetwork

def test_debug_max_cardinality():
    net = ReteNetwork()
    print("\nLoading: Person ⊑ᑦ ≤ 1 hasBirthMother․Person")
    net.load_ontology_from_string("Person ⊑ᑦ ≤ 1 hasBirthMother․Person")

    print("\nAll facts:")
    all_facts = net.query({})
    for i in range(min(30, len(all_facts))):
        row = {col: all_facts[col][i].as_py() for col in all_facts.column_names}
        if row.get('type'):  # Only print rows with type
            print(f"  {row}")

    print("\nLooking for max_qualified_cardinality facts:")
    max_qcard_facts = net.query({"type": "max_qualified_cardinality"})
    print(f"Found {len(max_qcard_facts)} max_qualified_cardinality facts")
    for i in range(len(max_qcard_facts)):
        row = {col: max_qcard_facts[col][i].as_py() for col in max_qcard_facts.column_names}
        print(f"  {row}")

    print("\nNow adding instance facts:")
    net.load_ontology_from_string("Person（Alice）")
    net.load_ontology_from_string("Person（Mary）")
    net.load_ontology_from_string("Person（Sue）")
    net.load_ontology_from_string("hasBirthMother（Alice，Mary）")
    net.load_ontology_from_string("hasBirthMother（Alice，Sue）")

    print("\nLooking for instance_of facts:")
    instance_facts = net.query({"type": "instance_of"})
    print(f"Found {len(instance_facts)} instance_of facts")
    for i in range(len(instance_facts)):
        row = {col: instance_facts[col][i].as_py() for col in instance_facts.column_names}
        print(f"  {row}")

    print("\nLooking for role_assertion facts:")
    role_facts = net.query({"type": "role_assertion"})
    print(f"Found {len(role_facts)} role_assertion facts")
    for i in range(len(role_facts)):
        row = {col: role_facts[col][i].as_py() for col in role_facts.column_names}
        print(f"  {row}")

    print("\nLooking for same_as facts after adding instances:")
    sameas_facts = net.query({"type": "same_as"})
    print(f"Found {len(sameas_facts)} same_as facts")
    for i in range(len(sameas_facts)):
        row = {col: sameas_facts[col][i].as_py() for col in sameas_facts.column_names}
        print(f"  {row}")

    # Check that cardinality inference generated Sue sameAs Mary
    # Look for the cardinality-inferred same_as (not just reflexive ones)
    cardinality_sameas = [
        i for i in range(len(sameas_facts))
        if sameas_facts['inferred_by'][i].as_py() and 'cls-maxqc' in str(sameas_facts['inferred_by'][i].as_py())
    ]
    assert len(cardinality_sameas) > 0, "Should have at least one same_as fact from cardinality inference"
    print(f"✓ Test passed: Found {len(cardinality_sameas)} cardinality-inferred same_as facts")
