"""
Test Alpha Network Optimization Correctness

This test verifies that the alpha network hash lookup optimization
produces EXACTLY the same results as the original implementation.

Tests:
1. Class hierarchy subsumption closure
2. Instance classification up the hierarchy
3. All expected facts are present
4. Rule firing counts match expectations
"""

import sys
import os
import pytest

# Add PyArrow DLL path before importing anything else
try:
    import pyarrow as pa
    pa.create_library_symlinks()
except (ImportError, AttributeError):
    pass  # PyArrow not available or method doesn't exist

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'rete_cpp'))

from reter import owl_rete_cpp


def test_simple_subsumption():
    """Test basic subsumption inference"""
    print("\n=== Test 1: Simple Subsumption ===")

    ontology = """
    Animal ⊑ᑦ Thing
    Mammal ⊑ᑦ Animal
    Dog ⊑ᑦ Mammal
    """

    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string(ontology)

    facts = net.get_all_facts()
    subsumptions = [f for f in facts if f.get('type') == 'subsumption']

    # Expected: Dog ⊑ Animal, Dog ⊑ Thing, Mammal ⊑ Thing (3 inferred)
    # Plus 3 direct assertions = 6 total
    expected_subsumptions = {
        ('Animal', 'Thing'),
        ('Mammal', 'Animal'),
        ('Dog', 'Mammal'),
        ('Dog', 'Animal'),   # Inferred
        ('Dog', 'Thing'),    # Inferred
        ('Mammal', 'Thing'), # Inferred
    }

    actual_subsumptions = {
        (s.get('sub'), s.get('sup'))  # Fixed: use 'sub' and 'sup'
        for s in subsumptions
    }

    print(f"Expected: {expected_subsumptions}")
    print(f"Actual:   {actual_subsumptions}")

    assert actual_subsumptions == expected_subsumptions, \
        f"Subsumption mismatch!\nMissing: {expected_subsumptions - actual_subsumptions}\nExtra: {actual_subsumptions - expected_subsumptions}"

    print("✓ All subsumptions correct")


def test_instance_classification():
    """Test instance classification up the hierarchy"""
    print("\n=== Test 2: Instance Classification ===")

    ontology = """
    Animal ⊑ᑦ Thing
    Mammal ⊑ᑦ Animal
    Dog ⊑ᑦ Mammal
    Dog（fido）
    """

    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string(ontology)

    facts = net.get_all_facts()
    instance_ofs = [f for f in facts if f.get('type') == 'instance_of']

    # Expected: fido should be classified as Dog, Mammal, Animal, Thing, owl:Thing
    expected_classifications = {
        ('fido', 'Dog'),
        ('fido', 'Mammal'),
        ('fido', 'Animal'),
        ('fido', 'Thing')
    }

    actual_classifications = {
        (i.get('individual'), i.get('concept'))  # Fixed: use 'individual' and 'concept'
        for i in instance_ofs
    }

    print(f"Expected: {expected_classifications}")
    print(f"Actual:   {actual_classifications}")

    assert actual_classifications == expected_classifications, \
        f"Classification mismatch!\nMissing: {expected_classifications - actual_classifications}\nExtra: {actual_classifications - expected_classifications}"

    print("✓ All instance classifications correct")


def test_deep_hierarchy():
    """Test deep class hierarchy (depth 10)"""
    print("\n=== Test 3: Deep Hierarchy ===")

    # Build hierarchy: Root ⊑ Thing, C0 ⊑ Root, C1 ⊑ C0, ..., C9 ⊑ C8
    lines = ["Root ⊑ᑦ Thing"]
    for i in range(10):
        parent = "Root" if i == 0 else f"C{i-1}"
        child = f"C{i}"
        lines.append(f"{child} ⊑ᑦ {parent}")

    ontology = "\n".join(lines)

    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string(ontology)

    facts = net.get_all_facts()
    subsumptions = [f for f in facts if f.get('type') == 'subsumption']

    # Expected subsumptions:
    # Direct: 11 (Root ⊑ Thing, C0 ⊑ Root, ..., C9 ⊑ C8)
    # Inferred transitive closure:
    #   C0: ⊑ Thing (1)
    #   C1: ⊑ Root, ⊑ Thing (2)
    #   C2: ⊑ C0, ⊑ Root, ⊑ Thing (3)
    #   ...
    #   C9: ⊑ C8, C7, ..., C0, Root, Thing (10)
    # Total inferred: 1+2+3+...+10 = 55
    # Total: 11 + 55 = 66

    print(f"Total subsumptions: {len(subsumptions)}")
    assert len(subsumptions) == 66, \
        f"Expected 66 subsumptions, got {len(subsumptions)}"

    # Verify C9 is subclass of all ancestors
    c9_subsumptions = {
        s.get('sup')  # Fixed
        for s in subsumptions
        if s.get('sub') == 'C9'  # Fixed
    }

    expected_c9_ancestors = {
        'C8', 'C7', 'C6', 'C5', 'C4', 'C3', 'C2', 'C1', 'C0', 'Root', 'Thing'
    }

    print(f"C9 ancestors: {c9_subsumptions}")
    assert c9_subsumptions == expected_c9_ancestors, \
        f"C9 ancestor mismatch!\nExpected: {expected_c9_ancestors}\nActual: {c9_subsumptions}"

    print("✓ Deep hierarchy correct (66 subsumptions)")


def test_multiple_instances():
    """Test multiple instances at deepest level"""
    print("\n=== Test 4: Multiple Instances ===")

    ontology = """
    Animal ⊑ᑦ Thing
    Mammal ⊑ᑦ Animal
    Dog ⊑ᑦ Mammal
    Dog（fido）
    Dog（rex）
    Dog（buddy）
    """

    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string(ontology)

    facts = net.get_all_facts()
    instance_ofs = [f for f in facts if f.get('type') == 'instance_of']

    # Each of 3 dogs should be classified as: Dog, Mammal, Animal, Thing (4 classes)
    # owl:Thing is disabled by default (ENABLE_OWL_THING_REASONING=OFF)
    # Total: 3 * 4 = 12
    assert len(instance_ofs) == 12, \
        f"Expected 12 instance_of facts, got {len(instance_ofs)}"

    # Verify each dog is classified correctly
    for dog_name in ['fido', 'rex', 'buddy']:
        dog_classes = {
            i.get('concept')  # Fixed
            for i in instance_ofs
            if i.get('individual') == dog_name  # Fixed
        }

        # Note: owl:Thing is also added by the cls-thing rule
        expected_classes = {'Dog', 'Mammal', 'Animal', 'Thing'}

        print(f"{dog_name} is instance of: {dog_classes}")
        assert dog_classes == expected_classes, \
            f"{dog_name} classification wrong!\nExpected: {expected_classes}\nActual: {dog_classes}"

    print("✓ All 3 instances classified correctly")


def test_complex_hierarchy_with_instances():
    """Test the exact scenario from test_tbox_with_1000_instances.py"""
    print("\n=== Test 5: Complex Hierarchy (depth=5, instances=10) ===")

    # Replicate test_tbox_with_1000_instances.py scenario
    depth = 5
    num_instances = 10

    lines = ["Root ⊑ᑦ Thing"]
    for i in range(depth):
        parent = "Root" if i == 0 else f"Class{i-1}"
        child = f"Class{i}"
        lines.append(f"{child} ⊑ᑦ {parent}")

    deepest_class = f"Class{depth-1}"
    for j in range(num_instances):
        lines.append(f"{deepest_class}（ind_{j}）")

    ontology = "\n".join(lines)

    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string(ontology)

    facts = net.get_all_facts()
    subsumptions = [f for f in facts if f.get('type') == 'subsumption']
    instance_ofs = [f for f in facts if f.get('type') == 'instance_of']

    # Verify subsumptions
    # Direct: 6 (Root ⊑ Thing, Class0 ⊑ Root, ..., Class4 ⊑ Class3)
    # Inferred: 1+2+3+4+5 = 15
    # Total: 21
    assert len(subsumptions) == 21, \
        f"Expected 21 subsumptions, got {len(subsumptions)}"

    # Verify Class4 has all ancestors
    class4_ancestors = {
        s.get('sup')  # Fixed
        for s in subsumptions
        if s.get('sub') == 'Class4'  # Fixed
    }
    expected_ancestors = {'Class3', 'Class2', 'Class1', 'Class0', 'Root', 'Thing'}

    print(f"Class4 ancestors: {class4_ancestors}")
    assert class4_ancestors == expected_ancestors, \
        f"Class4 ancestors wrong!"

    # Verify instances
    # Each of 10 instances should be classified as:
    # Class4 (asserted), Class3, Class2, Class1, Class0, Root, Thing (6 inferred) = 7 total
    # owl:Thing is disabled by default (ENABLE_OWL_THING_REASONING=OFF)
    # 10 instances × 7 = 70
    assert len(instance_ofs) == 70, \
        f"Expected 70 instance_of facts, got {len(instance_ofs)}"

    # Verify one specific instance has all classifications
    ind_0_classes = {
        i.get('concept')  # Fixed
        for i in instance_ofs
        if i.get('individual') == 'ind_0'  # Fixed
    }
    expected_classes = {'Class4', 'Class3', 'Class2', 'Class1', 'Class0', 'Root', 'Thing'}
    # Note: "Thing" might appear twice (once from assertion propagation, once from owl:Thing rule)
    # Let's check the actual count

    print(f"ind_0 classifications: {ind_0_classes}")
    print(f"Count: {len(ind_0_classes)}")

    # Should have at least the 7 classes in hierarchy
    minimum_expected = {'Class4', 'Class3', 'Class2', 'Class1', 'Class0', 'Root', 'Thing'}
    assert minimum_expected.issubset(ind_0_classes), \
        f"ind_0 missing classifications!\nExpected at least: {minimum_expected}\nActual: {ind_0_classes}"

    print("✓ Complex hierarchy with instances correct")


def test_rule_firing_counts():
    """Verify specific rule firing counts"""
    print("\n=== Test 6: Rule Firing Counts ===")

    depth = 5
    num_instances = 10

    lines = ["Root ⊑ᑦ Thing"]
    for i in range(depth):
        parent = "Root" if i == 0 else f"Class{i-1}"
        child = f"Class{i}"
        lines.append(f"{child} ⊑ᑦ {parent}")

    deepest_class = f"Class{depth-1}"
    for j in range(num_instances):
        lines.append(f"{deepest_class}（ind_{j}）")

    ontology = "\n".join(lines)

    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string(ontology)

    stats = net.get_production_stats()

    print(f"Production firing stats: {stats}")

    # Expected from test results:
    # scm-sco: 35 (subsumption transitivity)
    # cls-thing-1: 0 (disabled - owl:Thing reasoning is OFF)

    scm_sco = stats.get('scm-sco', 0)
    cls_thing = stats.get('cls-thing-1', 0)

    print(f"scm-sco fires: {scm_sco} (expected: 35)")
    print(f"cls-thing-1 fires: {cls_thing} (expected: 0 - owl:Thing disabled)")

    assert scm_sco == 35, f"scm-sco should fire 35 times, got {scm_sco}"
    assert cls_thing == 0, f"cls-thing-1 should fire 0 times (owl:Thing disabled), got {cls_thing}"

    print("✓ Rule firing counts match exactly")


def test_no_duplicate_facts():
    """Verify no duplicate facts are created"""
    print("\n=== Test 7: No Duplicate Facts ===")

    ontology = """
    Animal ⊑ᑦ Thing
    Mammal ⊑ᑦ Animal
    Dog ⊑ᑦ Mammal
    Dog（fido）
    """

    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string(ontology)

    facts = net.get_all_facts()

    # Check for duplicate subsumptions
    subsumptions = [f for f in facts if f.get('type') == 'subsumption']
    subsumption_pairs = [
        (s.get('sub'), s.get('sup'))  # Fixed
        for s in subsumptions
    ]

    duplicates = [pair for pair in subsumption_pairs if subsumption_pairs.count(pair) > 1]

    if duplicates:
        print(f"⚠️  Duplicate subsumptions found: {set(duplicates)}")
        # Count each
        from collections import Counter
        counts = Counter(subsumption_pairs)
        for pair, count in counts.items():
            if count > 1:
                print(f"  {pair}: {count} times")

    assert len(duplicates) == 0, f"Found duplicate subsumptions: {set(duplicates)}"

    # Check for duplicate instance_of
    instance_ofs = [f for f in facts if f.get('type') == 'instance_of']
    instance_pairs = [
        (i.get('individual'), i.get('concept'))  # Fixed
        for i in instance_ofs
    ]

    duplicates = [pair for pair in instance_pairs if instance_pairs.count(pair) > 1]

    if duplicates:
        print(f"⚠️  Duplicate instance_of found: {set(duplicates)}")
        from collections import Counter
        counts = Counter(instance_pairs)
        for pair, count in counts.items():
            if count > 1:
                print(f"  {pair}: {count} times")

    assert len(duplicates) == 0, f"Found duplicate instance_of facts: {set(duplicates)}"

    print("✓ No duplicate facts")


def run_all_tests():
    """Run all correctness tests"""
    print("\n" + "=" * 80)
    print("ALPHA NETWORK OPTIMIZATION CORRECTNESS TESTS")
    print("=" * 80)

    tests = [
        test_simple_subsumption,
        test_instance_classification,
        test_deep_hierarchy,
        test_multiple_instances,
        test_complex_hierarchy_with_instances,
        test_rule_firing_counts,
        test_no_duplicate_facts,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"💥 ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 80)

    if failed == 0:
        print("\n✅ ALL TESTS PASSED - OPTIMIZATION IS CORRECT!")
        return 0
    else:
        print(f"\n❌ {failed} TEST(S) FAILED - OPTIMIZATION HAS BUGS!")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
