"""
Compare performance with and without RETE_LOGGING
This test specifically measures the impact of console output on SWRL processing
"""

import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reter import Reter


def test_swrl_performance():
    """Test SWRL performance - will show debug output if RETE_LOGGING is enabled"""
    print("\n" + "=" * 80)
    print("SWRL PERFORMANCE TEST")
    print("=" * 80)

    r = Reter()

    # Create multiple SWRL rules to amplify the logging effect
    ontology = """
        ⊢ Employee（⌂x） → Person（⌂x）
        ⊢ Person（⌂x） → LivingBeing（⌂x）
        ⊢ Student（⌂x） → Person（⌂x）
        ⊢ hasParent（⌂x，⌂y） ∧ hasParent（⌂y，⌂z） → hasGrandparent（⌂x，⌂z）
        ⊢ hasParent（⌂x，⌂z） ∧ hasParent（⌂y，⌂z） → potentialSibling（⌂x，⌂y）

        Employee（alice）
        Employee（bob）
        Employee（charlie）
        Student（dave）
        Student（eve）

        hasParent（alice，mary）
        hasParent（bob，mary）
        hasParent（mary，susan）
        hasParent（dave，frank）
        hasParent（eve，frank）
    """

    print("\nLoading ontology with 5 SWRL rules and 10 data facts...")
    start = time.perf_counter()
    r.load_ontology(ontology)
    load_time = time.perf_counter() - start

    print(f"\n✓ Load time: {load_time * 1000:.2f} ms")

    print("\nStarting reasoning...")
    start = time.perf_counter()
    reason_time = time.perf_counter() - start

    print(f"\n✓ Reasoning time: {reason_time * 1000:.2f} ms")

    # Get stats
    all_facts = r.get_all_facts()
    print(f"✓ Total facts after reasoning: {len(all_facts)}")

    print("\n" + "=" * 80)
    print(f"TOTAL TIME: {(load_time + reason_time) * 1000:.2f} ms")
    print("=" * 80)

    # Verify inferences
    facts_person = r.query(type='instance_of', individual='alice', concept='Person')
    facts_living = r.query(type='instance_of', individual='alice', concept='LivingBeing')
    facts_sibling = r.query(type='role_assertion', subject='alice', role='potentialSibling', object='bob')

    assert len(facts_person) > 0, "Should infer alice is Person"
    assert len(facts_living) > 0, "Should infer alice is LivingBeing"
    assert len(facts_sibling) > 0, "Should infer alice potentialSibling bob"

    print("✓ All inferences verified correctly")


if __name__ == "__main__":
    test_swrl_performance()
