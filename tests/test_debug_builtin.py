#!/usr/bin/env python3
"""
Debug test for SWRL builtin binding propagation
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from reter import Reter

def test_builtin_binding():
    """Test that builtin-bound variables trigger consequent actions"""

    engine = Reter()

    # Load ontology with SWRL rule that uses builtin
    engine.load_ontology("""
        ⊢ hasAge（⌂x，⋈age） ∧ ⍚add（⋈new，⋈age，5） → hasFutureAge（⌂x，⋈new）
        hasAge（john，25）
    """)

    # Reasoning is automatic/incremental - no need to call reason()
    print("\n=== Checking results ===")

    # Get all facts from the network
    network = engine.network
    all_facts = network.get_all_facts()

    print(f"Total facts: {len(all_facts)}")

    # Check for the inferred hasFutureAge fact
    found_future_age = False
    for fact in all_facts:
        fact_type = fact.get("type", "")
        if fact_type in ["data_assertion", "data_property_assertion"]:
            prop = fact.get("property", "")
            subj = fact.get("subject", "")
            val = fact.get("value", "")
            print(f"  Data assertion: {subj} {prop} {val}")
            if prop == "hasFutureAge" and subj == "john" and val == "30":
                found_future_age = True

    if found_future_age:
        print("\n✓ SUCCESS: Builtin bound variable and consequent fired!")
        return True
    else:
        print("\n✗ FAILED: Consequent did not fire with builtin-bound variable")
        print("\nExpected to find: hasFutureAge(john, 30)")
        print("\nAll facts:")
        for fact in all_facts:
            print(f"  {fact}")
        return False

if __name__ == "__main__":
    success = test_builtin_binding()
    sys.exit(0 if success else 1)
