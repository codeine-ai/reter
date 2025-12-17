"""Debug test for role subsumption"""
import pytest
import sys
sys.path.insert(0, 'D:/ROOT/reter/rete_cpp')
from reter import owl_rete_cpp

def test_role_subsumption_debug():
    """Debug: hasParent ⊑ᴿ hasAncestor should infer hasAncestor"""
    net = owl_rete_cpp.ReteNetwork()

    print("\n=== Loading role subsumption ===")
    net.load_ontology_from_string("hasParent ⊑ᴿ hasAncestor")

    print("\n=== Loading hasParent relation ===")
    net.load_ontology_from_string("hasParent（Alice，Bob）")

    # Get all facts (returns list of dicts)
    fact_list = net.get_all_facts()
    print(f"\n=== All facts in network: {len(fact_list)} ===")

    print("\nAll facts:")
    for i, f in enumerate(fact_list):
        print(f"{i}: {f}")

    # Check for role_subsumption fact
    role_subs = [f for f in fact_list if f.get('type') == 'role_subsumption']
    print(f"\n=== Role subsumption facts: {len(role_subs)} ===")
    for rs in role_subs:
        print(f"  {rs}")

    # Check for role assertions
    role_assertions = [f for f in fact_list if f.get('type') == 'role_assertion']
    print(f"\n=== Role assertion facts: {len(role_assertions)} ===")
    for ra in role_assertions:
        print(f"  {ra}")

    # Try different query formats
    print("\n=== Testing query formats ===")

    # Format 1: Old WME format
    print("\n1. Old WME format:")
    try:
        results = net.query({"subject": "Alice", "attribute": "hasAncestor", "value": "Bob"})
        print(f"   Result: {len(results)} rows")
        if len(results) > 0:
            print(f"   Columns: {results.column_names}")
    except Exception as e:
        print(f"   Error: {e}")

    # Format 2: Role assertion format
    print("\n2. Role assertion format:")
    try:
        results = net.query({"type": "role_assertion", "role": "hasAncestor", "subject": "Alice", "object": "Bob"})
        print(f"   Result: {len(results)} rows")
        if len(results) > 0:
            print(f"   Columns: {results.column_names}")
    except Exception as e:
        print(f"   Error: {e}")

    # Format 3: Check what hasParent looks like
    print("\n3. Query for hasParent:")
    try:
        results = net.query({"type": "role_assertion", "role": "hasParent"})
        print(f"   Result: {len(results)} rows")
        if len(results) > 0:
            print(f"   Columns: {results.column_names}")
            for i in range(len(results)):
                row = {col: results[col][i].as_py() for col in results.column_names}
                print(f"   Row {i}: {row}")
    except Exception as e:
        print(f"   Error: {e}")

    # Format 4: Check what hasAncestor looks like
    print("\n4. Query for hasAncestor:")
    try:
        results = net.query({"type": "role_assertion", "role": "hasAncestor"})
        print(f"   Result: {len(results)} rows")
        if len(results) > 0:
            print(f"   Columns: {results.column_names}")
            for i in range(len(results)):
                row = {col: results[col][i].as_py() for col in results.column_names}
                print(f"   Row {i}: {row}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_role_subsumption_debug()
