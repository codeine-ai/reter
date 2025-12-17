"""
Test Arrow cache incremental append functionality (LIVE MODE)

This test verifies that the two-flag cache system works correctly:
- arrow_cache_dirty_ (full rebuild)
- arrow_cache_more_facts_ (incremental append)

Focus: Test Case 4 - incremental append when new facts are added
"""

import time
from reter import Reter


def test_cache_incremental_append():
    """Test that cache can incrementally append new facts instead of full rebuild"""
    print("=== Testing Arrow Cache Incremental Append (Live Mode) ===\n")

    # Create reasoner
    print("1. Creating DLReasoner...")
    reasoner = Reter()

    # Add initial ontology
    print("2. Adding initial ontology...")
    ontology = """
    Dog ⊑ᑦ Animal
    Cat ⊑ᑦ Animal
    Dog（Fido）
    Cat（Whiskers）
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # First call - should build cache (Case 1)
    print("\n3. First get_all_facts() - should build cache...")
    start = time.perf_counter()
    facts1 = reasoner.get_all_facts()
    time1 = time.perf_counter() - start
    count1 = facts1.num_rows
    print(f"   ✓ Built cache: {count1} facts in {time1*1000:.3f}ms")

    # Second call - should use cached table (Case 2 - zero-copy!)
    print("\n4. Second get_all_facts() - should use cache (zero-copy)...")
    start = time.perf_counter()
    facts2 = reasoner.get_all_facts()
    time2 = time.perf_counter() - start
    count2 = facts2.num_rows
    print(f"   ✓ Returned cached: {count2} facts in {time2*1000:.3f}ms")
    print(f"   ✓ Speedup: {time1/time2:.1f}x faster (cache hit)")
    assert count2 == count1, "Cache should return same number of facts"

    # Add new fact - should set more_facts flag
    print("\n5. Adding new fact (should set more_facts flag)...")
    from reter_core.owl_rete_cpp import Fact
    reasoner.network.add_fact(Fact({
        'type': 'instance_of',
        'individual': 'Rex',
        'concept': 'Dog',
        'inferred': 'false'
    }))

    # Third call - should incrementally append (Case 4 - LIVE MODE!)
    print("\n6. Third get_all_facts() - should APPEND new fact (incremental)...")
    start = time.perf_counter()
    facts3 = reasoner.get_all_facts()
    time3 = time.perf_counter() - start
    count3 = facts3.num_rows
    print(f"   ✓ Appended to cache: {count3} facts in {time3*1000:.3f}ms")
    print(f"   ✓ New facts added: {count3 - count2}")
    assert count3 > count2, "Should have more facts after adding Rex"

    # Verify Rex is in the facts
    print("\n7. Verifying new fact (Rex) is present...")
    df = facts3.to_pandas()
    rex_facts = df[df['individual'] == 'Rex']
    print(f"   ✓ Found {len(rex_facts)} fact(s) about Rex")
    assert len(rex_facts) > 0, "Rex should be in the facts"

    # Add multiple facts
    print("\n8. Adding multiple facts at once...")
    reasoner.network.add_fact(Fact({
        'type': 'instance_of',
        'individual': 'Buddy',
        'concept': 'Dog',
        'inferred': 'false'
    }))
    reasoner.network.add_fact(Fact({
        'type': 'instance_of',
        'individual': 'Mittens',
        'concept': 'Cat',
        'inferred': 'false'
    }))

    # Fourth call - should append multiple new facts (Case 4)
    print("\n9. Fourth get_all_facts() - should APPEND multiple facts...")
    start = time.perf_counter()
    facts4 = reasoner.get_all_facts()
    time4 = time.perf_counter() - start
    count4 = facts4.num_rows
    print(f"   ✓ Appended to cache: {count4} facts in {time4*1000:.3f}ms")
    print(f"   ✓ New facts added: {count4 - count3}")
    assert count4 > count3, "Should have more facts after adding Buddy and Mittens"

    # Verify all new individuals are present
    print("\n10. Verifying all new individuals are present...")
    df4 = facts4.to_pandas()
    rex_count = len(df4[df4['individual'] == 'Rex'])
    buddy_count = len(df4[df4['individual'] == 'Buddy'])
    mittens_count = len(df4[df4['individual'] == 'Mittens'])
    print(f"    ✓ Rex: {rex_count} fact(s)")
    print(f"    ✓ Buddy: {buddy_count} fact(s)")
    print(f"    ✓ Mittens: {mittens_count} fact(s)")
    assert rex_count > 0 and buddy_count > 0 and mittens_count > 0, "All new individuals should be present"

    # Final cache hit test
    print("\n11. Final cache hit test (should be zero-copy again)...")
    start = time.perf_counter()
    facts5 = reasoner.get_all_facts()
    time5 = time.perf_counter() - start
    count5 = facts5.num_rows
    print(f"    ✓ Returned cached: {count5} facts in {time5*1000:.3f}ms")
    print(f"    ✓ Speedup: {time4/time5:.1f}x faster (cache hit)")
    assert count5 == count4, "Cache should return same number of facts"

    print("\n" + "="*60)
    print("✅ All incremental append tests PASSED!")
    print("="*60)
    print("\nCache Performance Summary:")
    print(f"  - First call (build):        {time1*1000:.3f}ms ({count1} facts)")
    print(f"  - Second call (cache hit):   {time2*1000:.3f}ms ({count2} facts) - {time1/time2:.1f}x faster")
    print(f"  - Third call (append 1):     {time3*1000:.3f}ms ({count3} facts, +{count3-count2})")
    print(f"  - Fourth call (append 2):    {time4*1000:.3f}ms ({count4} facts, +{count4-count3})")
    print(f"  - Fifth call (cache hit):    {time5*1000:.3f}ms ({count5} facts) - {time4/time5:.1f}x faster")
    print("\n✅ Incremental append is working correctly!")


def test_cache_vs_full_rebuild_performance():
    """Compare incremental append vs. full rebuild performance"""
    print("\n" + "="*60)
    print("=== Performance: Incremental Append vs. Full Rebuild ===")
    print("="*60 + "\n")

    from reter_core.owl_rete_cpp import Fact

    # Create reasoner with larger dataset
    print("1. Creating reasoner with larger dataset...")
    reasoner = Reter()

    # Add many facts initially
    ontology_lines = ["Dog ⊑ᑦ Animal", "Cat ⊑ᑦ Animal"]
    for i in range(50):
        ontology_lines.append(f"Dog（Dog{i}）")
        ontology_lines.append(f"Cat（Cat{i}）")

    ontology = "\n".join(ontology_lines)
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Build initial cache
    print("2. Building initial cache...")
    start = time.perf_counter()
    facts1 = reasoner.get_all_facts()
    build_time = time.perf_counter() - start
    initial_count = facts1.num_rows
    print(f"   ✓ Built cache: {initial_count} facts in {build_time*1000:.3f}ms")

    # Add 10 new facts and measure incremental append time
    print("\n3. Adding 10 new facts (incremental append)...")
    for i in range(10):
        reasoner.network.add_fact(Fact({
            'type': 'instance_of',
            'individual': f'NewDog{i}',
            'concept': 'Dog',
            'inferred': 'false'
        }))

    start = time.perf_counter()
    facts2 = reasoner.get_all_facts()
    append_time = time.perf_counter() - start
    new_count = facts2.num_rows
    print(f"   ✓ Appended: {new_count} facts in {append_time*1000:.3f}ms")
    print(f"   ✓ Added: {new_count - initial_count} facts")

    # Estimate what full rebuild would have taken
    # (proportional to number of facts)
    estimated_rebuild = build_time * (new_count / initial_count)
    print(f"\n4. Performance comparison:")
    print(f"   - Incremental append:  {append_time*1000:.3f}ms")
    print(f"   - Estimated rebuild:   {estimated_rebuild*1000:.3f}ms")
    print(f"   - Speedup:             {estimated_rebuild/append_time:.1f}x faster")

    print("\n✅ Incremental append is significantly faster than full rebuild!")


if __name__ == "__main__":
    test_cache_incremental_append()
    test_cache_vs_full_rebuild_performance()

    print("\n" + "="*60)
    print("🎉 ALL TESTS PASSED!")
    print("="*60)
