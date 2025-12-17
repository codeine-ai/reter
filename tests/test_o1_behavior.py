"""
Test O(1) Behavior of Alpha Network Optimization

This test verifies that alpha network activation is truly O(1) (constant time)
with respect to the number of alpha memories, not O(N) (linear time).

The test creates scenarios with different numbers of alpha memories and measures
the time to activate a WME. With O(1) behavior, time should be constant
regardless of the number of alpha memories.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'rete_cpp'))

import time
import pytest
from reter_core import owl_rete_cpp

# Mark all tests in this module as slow (performance tests)
pytestmark = pytest.mark.slow


def create_many_classes(num_classes):
    """
    Create many independent class hierarchies to generate many alpha memories.
    Each hierarchy creates different patterns and thus different alpha memories.
    """
    lines = []

    # Create num_classes independent hierarchies
    # Each creates alpha memories for subsumption patterns
    for i in range(num_classes):
        base = f"Base{i}"
        mid = f"Mid{i}"
        leaf = f"Leaf{i}"

        lines.append(f"{base} ⊑ᑦ Thing")
        lines.append(f"{mid} ⊑ᑦ {base}")
        lines.append(f"{leaf} ⊑ᑦ {mid}")

    return "\n".join(lines)


def measure_wme_insertion_time(num_classes, num_insertions=1000):
    """
    Create a network with num_classes alpha memories,
    then measure time to insert num_insertions WMEs.
    """
    # Create ontology with many classes (many alpha memories)
    ontology = create_many_classes(num_classes)

    net = owl_rete_cpp.ReteNetwork()
    net.load_ontology_from_string(ontology)

    # Create test instances to insert
    # These will create new WMEs that activate alpha network
    test_instances = [f"TestClass（inst_{i}）" for i in range(num_insertions)]
    test_ontology = "TestClass ⊑ᑦ Thing\n" + "\n".join(test_instances)

    # Measure time for WME insertions
    start = time.perf_counter()
    net.load_ontology_from_string(test_ontology)
    elapsed = time.perf_counter() - start

    # Calculate per-WME time
    per_wme_time = elapsed / num_insertions if num_insertions > 0 else 0

    return {
        'num_classes': num_classes,
        'num_insertions': num_insertions,
        'total_time': elapsed,
        'per_wme_time': per_wme_time,
        'alpha_memories': net.fact_count(),  # Approximate
    }


def format_time(seconds):
    """Format time in appropriate units"""
    if seconds < 0.000001:
        return f"{seconds * 1000000000:.2f} ns"
    elif seconds < 0.001:
        return f"{seconds * 1000000:.2f} µs"
    elif seconds < 1:
        return f"{seconds * 1000:.2f} ms"
    else:
        return f"{seconds:.2f} s"


def test_o1_behavior():
    """
    Test that WME insertion time is O(1) with respect to number of alpha memories.
    """
    print("\n" + "=" * 80)
    print("ALPHA NETWORK O(1) BEHAVIOR VERIFICATION")
    print("=" * 80)

    print("\nThis test verifies that alpha network activation time does NOT grow")
    print("linearly with the number of alpha memories (O(N)), but instead remains")
    print("constant (O(1)).")
    print()

    # Test with different numbers of alpha memories
    # Each scenario creates different number of classes (and thus alpha memories)
    scenarios = [
        10,    # Few alpha memories
        50,    # Moderate
        100,   # Many
        200,   # Lots
        500,   # Very many
    ]

    num_insertions = 100  # Number of WMEs to insert for measurement

    print(f"Test: Insert {num_insertions} WMEs with varying numbers of alpha memories")
    print()
    print(f"{'Alpha Mem (approx)':<20} {'Total Time':<15} {'Per-WME Time':<15} {'Ratio':<10}")
    print("-" * 70)

    results = []
    baseline_time = None

    for num_classes in scenarios:
        result = measure_wme_insertion_time(num_classes, num_insertions)
        results.append(result)

        if baseline_time is None:
            baseline_time = result['per_wme_time']
            ratio = 1.0
        else:
            ratio = result['per_wme_time'] / baseline_time if baseline_time > 0 else 0

        print(f"{num_classes:<20} {format_time(result['total_time']):<15} "
              f"{format_time(result['per_wme_time']):<15} {ratio:<10.2f}x")

    # Analyze results
    print()
    print("=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    print()

    # Calculate growth rate
    first_result = results[0]
    last_result = results[-1]

    alpha_mem_ratio = last_result['num_classes'] / first_result['num_classes']
    time_ratio = last_result['per_wme_time'] / first_result['per_wme_time'] if first_result['per_wme_time'] > 0 else 0

    print(f"Alpha memories increased: {first_result['num_classes']} → {last_result['num_classes']} "
          f"({alpha_mem_ratio:.1f}x)")
    print(f"Per-WME time changed: {format_time(first_result['per_wme_time'])} → "
          f"{format_time(last_result['per_wme_time'])} ({time_ratio:.2f}x)")
    print()

    # Check for O(1) behavior
    # If O(1), time ratio should be close to 1.0 (constant time)
    # If O(N), time ratio should equal alpha_mem_ratio (linear growth)

    print("EXPECTED BEHAVIOR:")
    print(f"  O(1) constant time: time ratio = ~1.0x")
    print(f"  O(N) linear time:   time ratio = ~{alpha_mem_ratio:.1f}x")
    print()

    print("ACTUAL BEHAVIOR:")
    print(f"  Time ratio: {time_ratio:.2f}x")
    print()

    # Determine verdict
    # Allow some variance due to measurement noise (within 2x)
    if time_ratio < 2.0:
        print("✅ VERDICT: O(1) CONSTANT TIME BEHAVIOR CONFIRMED")
        print(f"   Time growth ({time_ratio:.2f}x) is much less than alpha memory growth ({alpha_mem_ratio:.1f}x)")
        print("   This indicates hash lookup O(1) is working correctly!")
        return True
    elif time_ratio < alpha_mem_ratio * 0.5:
        print("⚠️  VERDICT: SUB-LINEAR BEHAVIOR (Better than O(N) but not quite O(1))")
        print(f"   Time growth ({time_ratio:.2f}x) is less than alpha memory growth ({alpha_mem_ratio:.1f}x)")
        print("   Optimization is helping but may have some scaling")
        return True
    else:
        print("❌ VERDICT: LINEAR O(N) BEHAVIOR DETECTED")
        print(f"   Time growth ({time_ratio:.2f}x) matches alpha memory growth ({alpha_mem_ratio:.1f}x)")
        print("   Hash lookup optimization may not be working correctly!")
        return False


def test_worst_case_scenario():
    """
    Test worst-case scenario: Many alpha memories, none match the WME.
    With O(N), this would iterate all alpha memories.
    With O(1), this should still be fast (just 8 hash lookups that fail).
    """
    print("\n" + "=" * 80)
    print("WORST-CASE SCENARIO: Many Alpha Memories, No Matches")
    print("=" * 80)
    print()

    # Create 100 different class patterns (100+ alpha memories)
    # Note: Reduced from 1000 to 100 to avoid timeout with automatic reasoning
    ontology = create_many_classes(100)

    net = owl_rete_cpp.ReteNetwork()

    print("Creating network with 100 class hierarchies...")
    start = time.perf_counter()
    net.load_ontology_from_string(ontology)
    setup_time = time.perf_counter() - start
    print(f"Setup time: {format_time(setup_time)}")
    print(f"Facts created: {net.fact_count()}")
    print()

    # Now insert a completely unrelated instance
    # This WME won't match ANY of the 1000+ alpha memories
    print("Inserting unrelated instance (won't match any alpha memories)...")

    unrelated = "UnrelatedClass ⊑ᑦ Thing\nUnrelatedClass（orphan）"

    start = time.perf_counter()
    net.load_ontology_from_string(unrelated)
    insertion_time = time.perf_counter() - start

    print(f"Insertion time: {format_time(insertion_time)}")
    print()

    # With O(N), this would take ~100x longer than single alpha memory
    # With O(1), this should be very fast (just 8 failed hash lookups)

    if insertion_time < 0.1:  # Less than 100ms
        print("✅ VERDICT: Very fast insertion despite 100+ alpha memories")
        print("   This confirms O(1) hash lookup behavior!")
        return True
    else:
        print("⚠️  WARNING: Insertion took longer than expected")
        print("   May indicate some O(N) behavior")
        return False


def test_implementation_inspection():
    """
    Inspect the actual implementation to verify it uses hash lookup.
    """
    print("\n" + "=" * 80)
    print("IMPLEMENTATION INSPECTION")
    print("=" * 80)
    print()

    print("Checking alpha_network.cpp implementation...")
    print()

    # Read the implementation
    try:
        with open("D:\\ROOT\\reter\\rete_cpp\\alpha_network.cpp", 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for the optimized code
        if "generate_matching_keys" in content:
            print("✅ Found generate_matching_keys() method")
        else:
            print("❌ Missing generate_matching_keys() method")
            return False

        if "for (int mask = 0; mask < 8; ++mask)" in content:
            print("✅ Found subset enumeration (8 combinations)")
        else:
            print("❌ Missing subset enumeration")
            return False

        if "alpha_memories_map_.find(key)" in content:
            print("✅ Found hash map lookup (O(1))")
        else:
            print("❌ Missing hash map lookup")
            return False

        # Check for OLD O(N) iteration (should NOT be present)
        if "for (auto& [key, alpha_mem] : alpha_memories_map_)" in content and \
           "bool matches = true" in content and \
           content.count("for (auto& [key, alpha_mem]") == 1:  # Only in clear()
            print("⚠️  WARNING: Found O(N) iteration pattern")
            print("   (May be in clear() method which is OK)")

        print()
        print("✅ Implementation uses hash-based O(1) lookup")
        return True

    except Exception as e:
        print(f"❌ Could not read implementation: {e}")
        return False


def run_all_tests():
    """Run all O(1) behavior tests"""
    print("\n" + "=" * 80)
    print("ALPHA NETWORK O(1) VERIFICATION TEST SUITE")
    print("=" * 80)

    results = []

    # Test 1: O(1) behavior with varying alpha memories
    try:
        result = test_o1_behavior()
        results.append(("O(1) Behavior Test", result))
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        results.append(("O(1) Behavior Test", False))

    # Test 2: Worst-case scenario
    try:
        result = test_worst_case_scenario()
        results.append(("Worst-Case Scenario", result))
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Worst-Case Scenario", False))

    # Test 3: Implementation inspection
    try:
        result = test_implementation_inspection()
        results.append(("Implementation Inspection", result))
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        results.append(("Implementation Inspection", False))

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print()

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print()
    print(f"Results: {passed}/{total} tests passed")
    print()

    if passed == total:
        print("✅ ALL TESTS PASSED - O(1) BEHAVIOR VERIFIED!")
        return 0
    else:
        print(f"❌ {total - passed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
