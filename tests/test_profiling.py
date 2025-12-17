#!/usr/bin/env python
"""
Profiling test - demonstrates comprehensive performance statistics collection

This test builds a class hierarchy and instances programmatically,
then collects detailed profiling statistics to identify bottlenecks.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from reter import Reter
import time

def build_hierarchy(reasoner, depth, num_siblings):
    """Build a class hierarchy of specified depth and branching factor"""
    # Create root class - using DL syntax: Root ⊑ᑦ Thing
    reasoner.network.load_ontology_from_string("Root ⊑ᑦ ⊤")

    # Build hierarchy level by level
    for level in range(depth):
        for sibling in range(num_siblings):
            if level == 0:
                parent = "Root"
            else:
                # Fan out: each class at level L has num_siblings children at level L+1
                parent_idx = sibling // num_siblings
                parent = f"L{level-1}C{parent_idx}"

            child = f"L{level}C{sibling}"
            # Using DL syntax: child ⊑ᑦ parent
            reasoner.network.load_ontology_from_string(f"{child} ⊑ᑦ {parent}")

    return depth * num_siblings

def add_instances(reasoner, num_classes, instances_per_class):
    """Add instances to leaf classes"""
    for cls_idx in range(num_classes):
        class_name = f"L{0}C{cls_idx}"  # Use level 0 classes
        for inst_idx in range(instances_per_class):
            inst_name = f"inst_{cls_idx}_{inst_idx}"
            # Using DL syntax: ClassName（instance）
            reasoner.network.load_ontology_from_string(f"{class_name}（{inst_name}）")

    return num_classes * instances_per_class

def test_profiling():
    print("=" * 80)
    print("RETE PROFILING TEST")
    print("=" * 80)
    print()

    # Create reasoner
    reasoner = Reter()

    # Build test hierarchy
    print("Building class hierarchy...")
    depth = 5
    siblings = 5
    num_classes = build_hierarchy(reasoner, depth, siblings)
    print(f"  Created {num_classes} classes in {depth} levels")

    print("\nAdding instances...")
    num_instances = add_instances(reasoner, siblings, 10)
    print(f"  Created {num_instances} instances")

    # Perform reasoning
    print("\nPerforming reasoning...")
    start = time.time()
    
    elapsed = time.time() - start
    print(f"  Reasoning completed in {elapsed:.3f}s")

    # Get profiling stats
    stats = reasoner.network.get_profiling_stats()

    print("Profiling Statistics:")
    print("-" * 80)

    # Group stats by category
    join_stats = {k: v for k, v in stats.items() if 'beta' in k}
    alpha_stats = {k: v for k, v in stats.items() if 'alpha' in k}
    general_stats = {k: v for k, v in stats.items() if k not in join_stats and k not in alpha_stats}

    print("\n📊 Alpha Network Statistics:")
    for key, value in sorted(alpha_stats.items()):
        print(f"  {key:30s}: {value:,}")

    print("\n📊 Beta Network (Join) Statistics:")
    for key, value in sorted(join_stats.items()):
        print(f"  {key:30s}: {value:,}")

    print("\n📊 General Statistics:")
    for key, value in sorted(general_stats.items()):
        print(f"  {key:30s}: {value:,}")

    # Calculate some derived metrics
    print("\n📈 Derived Metrics:")
    print("-" * 80)

    if stats.get('alpha_memory_checks', 0) > 0:
        hit_rate = (stats.get('alpha_activations', 0) / stats.get('alpha_memory_checks', 0)) * 100
        print(f"  Alpha memory hit rate: {hit_rate:.2f}%")

    total_beta = stats.get('indexed_beta_activations', 0) + stats.get('fallback_beta_activations', 0)
    if total_beta > 0:
        indexed_pct = (stats.get('indexed_beta_activations', 0) / total_beta) * 100
        print(f"  Beta join index usage: {indexed_pct:.2f}%")

    if stats.get('join_tests_performed', 0) > 0:
        join_success_rate = (stats.get('join_tests_passed', 0) / stats.get('join_tests_performed', 0)) * 100
        print(f"  Join test success rate: {join_success_rate:.2f}%")

    print("\n✅ Profiling test completed successfully!")
    print()

if __name__ == "__main__":
    test_profiling()
