"""
Test property chain template serialization and deserialization.

This test verifies that:
1. Property chain templates work correctly before serialization
2. The network can be serialized (saved)
3. The network can be deserialized (loaded)
4. Property chain reasoning continues to work after deserialization with NEW instances

The key requirement is that template-instantiated rules (like prp-spo2) must be
properly restored during deserialization and remain active for new facts.
"""

import tempfile
import os
import pytest
from reter import Reter


def test_property_chain_serialization_and_deserialization():
    """
    Test that property chain template rules work after deserialization.

    Steps:
    1. Create Reter("ai") instance
    2. Add property chain: hasParent ∘ hasParent ⊑ hasGrandparent
    3. Add initial instances (Alice -> Bob -> Charlie)
    4. Verify property chain inference works (Alice hasGrandparent Charlie)
    5. Serialize network to file
    6. Deserialize network into new Reter instance
    7. Add NEW instances (David -> Eve -> Frank)
    8. Verify property chain inference works for NEW instances (David hasGrandparent Frank)
    """
    print("\n" + "=" * 70)
    print("TEST: Property Chain Serialization & Deserialization")
    print("=" * 70)

    # ========================================================================
    # PHASE 1: Create network with property chain and verify it works
    # ========================================================================
    print("\n--- PHASE 1: Initial Network Setup ---")

    reasoner1 = Reter(variant="ai")

    # Define property chain and initial instances
    ontology = """
    Person(Alice)
    Person(Bob)
    Person(Charlie)
    hasParent(Alice, Bob)
    hasParent(Bob, Charlie)
    hasParent composed_with hasParent is_subproperty_of hasGrandparent
    """

    reasoner1.load_ontology(ontology)
    print("✓ Loaded initial ontology with property chain")

    # Verify property chain reasoning works BEFORE serialization
    facts_before = reasoner1.query(
        type="role_assertion",
        subject="Alice",
        role="hasGrandparent",
        object="Charlie"
    )

    print(f"\nInferred facts BEFORE serialization:")
    for fact in facts_before:
        print(f"  - {fact.get('subject')} {fact.get('role')} {fact.get('object')} "
              f"(inferred_by: {fact.get('inferred_by')})")

    assert len(facts_before) > 0, "Should infer Alice hasGrandparent Charlie BEFORE serialization"
    has_prp_spo2 = any(fact.get("inferred_by") == "prp-spo2" for fact in facts_before)
    assert has_prp_spo2, "Should have inference from prp-spo2 rule BEFORE serialization"
    print("✓ Property chain reasoning works BEFORE serialization")

    # ========================================================================
    # PHASE 2: Serialize the network
    # ========================================================================
    print("\n--- PHASE 2: Serialization ---")

    with tempfile.NamedTemporaryFile(suffix='.pb', delete=False) as f:
        temp_file = f.name

    try:
        success = reasoner1.network.save(temp_file)
        assert success, "Serialization should succeed"
        print(f"✓ Network serialized to: {temp_file}")
        print(f"  File size: {os.path.getsize(temp_file)} bytes")

        # ====================================================================
        # PHASE 3: Deserialize into new network
        # ====================================================================
        print("\n--- PHASE 3: Deserialization ---")

        reasoner2 = Reter(variant="ai")
        success = reasoner2.network.load(temp_file)
        assert success, "Deserialization should succeed"
        print("✓ Network deserialized successfully")

        # Verify old facts are still there
        facts_after_load = reasoner2.query(
            type="role_assertion",
            subject="Alice",
            role="hasGrandparent",
            object="Charlie"
        )

        print(f"\nInferred facts AFTER deserialization (old instances):")
        for fact in facts_after_load:
            print(f"  - {fact.get('subject')} {fact.get('role')} {fact.get('object')} "
                  f"(inferred_by: {fact.get('inferred_by')})")

        assert len(facts_after_load) > 0, "Old inferences should be preserved after deserialization"
        print("✓ Old inferences preserved after deserialization")

        # ====================================================================
        # PHASE 4: Add NEW instances to deserialized network
        # ====================================================================
        print("\n--- PHASE 4: Adding NEW Instances to Deserialized Network ---")

        # Add completely new instances to test if template rule is still active
        new_ontology = """
        Person(David)
        Person(Eve)
        Person(Frank)
        hasParent(David, Eve)
        hasParent(Eve, Frank)
        """

        reasoner2.load_ontology(new_ontology)
        print("✓ Added new instances: David -> Eve -> Frank")

        # ====================================================================
        # PHASE 5: Verify property chain works for NEW instances
        # ====================================================================
        print("\n--- PHASE 5: Verify Property Chain Works for NEW Instances ---")

        # This is the CRITICAL test: Does the template-instantiated prp-spo2 rule
        # fire for NEW instances added AFTER deserialization?
        facts_new = reasoner2.query(
            type="role_assertion",
            subject="David",
            role="hasGrandparent",
            object="Frank"
        )

        print(f"\nInferred facts AFTER deserialization (NEW instances):")
        for fact in facts_new:
            print(f"  - {fact.get('subject')} {fact.get('role')} {fact.get('object')} "
                  f"(inferred_by: {fact.get('inferred_by')})")

        # CRITICAL ASSERTION: Property chain should work for new instances
        assert len(facts_new) > 0, \
            "Should infer David hasGrandparent Frank (property chain on NEW instances after deserialization)"

        has_prp_spo2_new = any(fact.get("inferred_by") == "prp-spo2" for fact in facts_new)
        assert has_prp_spo2_new, \
            "Should have inference from prp-spo2 rule for NEW instances after deserialization"

        print("✓ Property chain reasoning works for NEW instances after deserialization")

        # ====================================================================
        # PHASE 6: Verify both old and new inferences coexist
        # ====================================================================
        print("\n--- PHASE 6: Verify Complete Network State ---")

        # Query all hasGrandparent relationships
        all_grandparent_facts = reasoner2.query(
            type="role_assertion",
            role="hasGrandparent"
        )

        print(f"\nAll hasGrandparent relationships in deserialized network:")
        for fact in all_grandparent_facts:
            print(f"  - {fact.get('subject')} hasGrandparent {fact.get('object')} "
                  f"(inferred_by: {fact.get('inferred_by')})")

        # Should have at least 2 grandparent relationships (Alice->Charlie, David->Frank)
        assert len(all_grandparent_facts) >= 2, \
            "Should have both old and new grandparent inferences"

        subjects = [fact.get('subject') for fact in all_grandparent_facts]
        assert "Alice" in subjects, "Alice should have grandparent relationship"
        assert "David" in subjects, "David should have grandparent relationship"

        print(f"✓ Total hasGrandparent relationships: {len(all_grandparent_facts)}")
        print("✓ Both old and new inferences coexist correctly")

        print("\n" + "=" * 70)
        print("TEST PASSED: Property chain template rules work after deserialization!")
        print("=" * 70)

    finally:
        # Cleanup temp file
        if os.path.exists(temp_file):
            os.unlink(temp_file)
            print(f"\n✓ Cleaned up temp file: {temp_file}")


def test_property_chain_three_property_serialization():
    """
    Test 3-property chain serialization (more complex case).

    Chain: hasParent ∘ hasParent ∘ hasParent ⊑ hasGreatGrandparent
    """
    print("\n" + "=" * 70)
    print("TEST: 3-Property Chain Serialization & Deserialization")
    print("=" * 70)

    reasoner1 = Reter(variant="ai")

    # 3-property chain
    ontology = """
    Person(Alice)
    Person(Bob)
    Person(Charlie)
    Person(Diana)
    hasParent(Alice, Bob)
    hasParent(Bob, Charlie)
    hasParent(Charlie, Diana)
    hasParent composed_with hasParent composed_with hasParent is_subproperty_of hasGreatGrandparent
    """

    reasoner1.load_ontology(ontology)
    print("✓ Loaded ontology with 3-property chain")

    # Verify before serialization
    facts_before = reasoner1.query(
        type="role_assertion",
        subject="Alice",
        role="hasGreatGrandparent",
        object="Diana"
    )

    assert len(facts_before) > 0, "Should infer Alice hasGreatGrandparent Diana"
    print("✓ 3-property chain works BEFORE serialization")

    # Serialize
    with tempfile.NamedTemporaryFile(suffix='.pb', delete=False) as f:
        temp_file = f.name

    try:
        reasoner1.network.save(temp_file)
        print(f"✓ Serialized to: {temp_file}")

        # Deserialize and add new instances
        reasoner2 = Reter(variant="ai")
        reasoner2.network.load(temp_file)
        print("✓ Deserialized network")

        # Add new 3-generation chain
        new_ontology = """
        Person(Eve)
        Person(Frank)
        Person(Grace)
        Person(Henry)
        hasParent(Eve, Frank)
        hasParent(Frank, Grace)
        hasParent(Grace, Henry)
        """

        reasoner2.load_ontology(new_ontology)
        print("✓ Added new 3-generation chain: Eve -> Frank -> Grace -> Henry")

        # Verify 3-property chain works for new instances
        facts_new = reasoner2.query(
            type="role_assertion",
            subject="Eve",
            role="hasGreatGrandparent",
            object="Henry"
        )

        print(f"\nInferred facts for NEW instances:")
        for fact in facts_new:
            print(f"  - {fact.get('subject')} {fact.get('role')} {fact.get('object')}")

        assert len(facts_new) > 0, \
            "Should infer Eve hasGreatGrandparent Henry after deserialization"

        print("✓ 3-property chain works for NEW instances after deserialization")
        print("\n" + "=" * 70)
        print("TEST PASSED: 3-property chain template survives deserialization!")
        print("=" * 70)

    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def test_multiple_property_chains_serialization():
    """
    Test multiple different property chains in same network.

    Tests that multiple template-instantiated rules can coexist and
    all survive deserialization.
    """
    print("\n" + "=" * 70)
    print("TEST: Multiple Property Chains Serialization")
    print("=" * 70)

    reasoner1 = Reter(variant="ai")

    # Define multiple property chains
    ontology = """
    Person(Alice)
    Person(Bob)
    Person(Charlie)
    Person(Dana)

    hasParent(Alice, Bob)
    hasParent(Bob, Charlie)
    hasSibling(Bob, Dana)

    hasParent composed_with hasParent is_subproperty_of hasGrandparent
    hasParent composed_with hasSibling is_subproperty_of hasUncle
    """

    reasoner1.load_ontology(ontology)
    print("✓ Loaded ontology with 2 different property chains")

    # Verify both chains work
    grandparent = reasoner1.query(
        type="role_assertion",
        subject="Alice",
        role="hasGrandparent"
    )

    uncle = reasoner1.query(
        type="role_assertion",
        subject="Alice",
        role="hasUncle"
    )

    assert len(grandparent) > 0, "hasGrandparent chain should work"
    assert len(uncle) > 0, "hasUncle chain should work"
    print("✓ Both property chains work BEFORE serialization")

    # Serialize
    with tempfile.NamedTemporaryFile(suffix='.pb', delete=False) as f:
        temp_file = f.name

    try:
        reasoner1.network.save(temp_file)

        # Deserialize and add new instances
        reasoner2 = Reter(variant="ai")
        reasoner2.network.load(temp_file)
        print("✓ Deserialized network")

        # Add new instances for both chains
        new_ontology = """
        Person(Eve)
        Person(Frank)
        Person(Grace)
        Person(Henry)

        hasParent(Eve, Frank)
        hasParent(Frank, Grace)
        hasSibling(Frank, Henry)
        """

        reasoner2.load_ontology(new_ontology)
        print("✓ Added new instances for both chains")

        # Verify both chains work for new instances
        new_grandparent = reasoner2.query(
            type="role_assertion",
            subject="Eve",
            role="hasGrandparent",
            object="Grace"
        )

        new_uncle = reasoner2.query(
            type="role_assertion",
            subject="Eve",
            role="hasUncle",
            object="Henry"
        )

        print(f"\nNew grandparent inferences: {len(new_grandparent)}")
        print(f"New uncle inferences: {len(new_uncle)}")

        assert len(new_grandparent) > 0, "hasGrandparent chain should work after deserialization"
        assert len(new_uncle) > 0, "hasUncle chain should work after deserialization"

        print("✓ Both property chains work for NEW instances after deserialization")
        print("\n" + "=" * 70)
        print("TEST PASSED: Multiple property chains survive deserialization!")
        print("=" * 70)

    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


if __name__ == "__main__":
    test_property_chain_serialization_and_deserialization()
    test_property_chain_three_property_serialization()
    test_multiple_property_chains_serialization()
    print("\n" + "=" * 70)
    print("ALL TESTS PASSED!")
    print("=" * 70)
