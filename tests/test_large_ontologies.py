"""
Performance tests for large ontologies (10,000 and 100,000 axioms)
Tests RETE network scalability with production-scale ontologies
"""

import time
import sys
import os
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reter import owl_rete_cpp

# Mark all tests in this module as slow
pytestmark = pytest.mark.slow


def format_time(seconds):
    """Format time in appropriate units"""
    if seconds < 0.001:
        return f"{seconds * 1000000:.2f} µs"
    elif seconds < 1:
        return f"{seconds * 1000:.2f} ms"
    else:
        return f"{seconds:.2f} s"


def format_number(num):
    """Format large numbers with thousand separators"""
    return f"{num:,}"


def test_10k_hierarchy():
    """Test with 10,000 axioms: deep hierarchy with multiple branches"""
    print("\n" + "=" * 80)
    print("LARGE ONTOLOGY TEST: 10,000 Axioms")
    print("=" * 80)

    network = owl_rete_cpp.ReteNetwork()

    # Configuration: Create a hierarchy with:
    # - 10 main branches
    # - Each branch has 100 levels deep
    # - 10 individuals per branch (100 total individuals)
    # Total: 1,000 subsumption axioms + 9,000 class assertions = 10,000 axioms

    num_branches = 10
    depth_per_branch = 100
    individuals_per_branch = 900  # 9,000 total individuals

    total_axioms = 0

    print(f"\nGenerating ontology:")
    print(f"  Branches: {num_branches}")
    print(f"  Depth per branch: {depth_per_branch}")
    print(f"  Individuals per branch: {individuals_per_branch}")

    start = time.perf_counter()

    # Create class hierarchies
    for branch in range(num_branches):
        branch_name = f"Branch{branch}"

        # Root of this branch
        fact = owl_rete_cpp.Fact({
            "type": "subsumption",
            "subclass": f"{branch_name}L0",
            "superclass": "Thing"
        })
        network.add_fact(fact)
        total_axioms += 1

        # Create deep chain
        for level in range(1, depth_per_branch):
            fact = owl_rete_cpp.Fact({
                "type": "subsumption",
                "subclass": f"{branch_name}L{level}",
                "superclass": f"{branch_name}L{level-1}"
            })
            network.add_fact(fact)
            total_axioms += 1

        # Add individuals distributed across levels
        for i in range(individuals_per_branch):
            # Distribute individuals across different levels
            level = i % depth_per_branch
            fact = owl_rete_cpp.Fact({
                "type": "class_assertion",
                "individual": f"{branch_name}Ind{i}",
                "class": f"{branch_name}L{level}"
            })
            network.add_fact(fact)
            total_axioms += 1

    add_time = time.perf_counter() - start

    print(f"\n✓ Generated {format_number(total_axioms)} axioms")
    print(f"  Fact addition time: {format_time(add_time)}")
    print(f"  Average per axiom: {format_time(add_time / total_axioms)}")

    # Reasoning is automatic/incremental - already happened during fact addition
    print(f"\n🔍 Reasoning complete (automatic/incremental during fact addition)...")
    reason_time = add_time  # Reasoning is included in add_time with automatic reasoning

    fact_count = network.fact_count()
    inferred_facts = fact_count - total_axioms

    print(f"\n📊 Results:")
    print(f"  Initial axioms:      {format_number(total_axioms)}")
    print(f"  Inferred facts:      {format_number(inferred_facts)}")
    print(f"  Total facts:         {format_number(fact_count)}")
    print(f"  ")
    print(f"  Fact addition time:  {format_time(add_time)}")
    print(f"  Reasoning time:      {format_time(reason_time)}")
    print(f"  Total time:          {format_time(add_time + reason_time)}")
    print(f"  ")
    print(f"  Throughput:          {format_number(int(fact_count / (add_time + reason_time)))} facts/sec")
    print(f"  Inference rate:      {format_number(int(inferred_facts / reason_time)) if reason_time > 0 else 0} inferences/sec")

    print("\n✓ 10K axiom test completed")
    return {
        'axioms': total_axioms,
        'total_facts': fact_count,
        'add_time': add_time,
        'reason_time': reason_time,
        'total_time': add_time + reason_time
    }


def test_100k_hierarchy():
    """Test with 100,000 axioms: very large production-scale ontology"""
    print("\n" + "=" * 80)
    print("LARGE ONTOLOGY TEST: 100,000 Axioms")
    print("=" * 80)

    network = owl_rete_cpp.ReteNetwork()

    # Configuration: Create a hierarchy with:
    # - 100 main branches
    # - Each branch has 100 levels deep
    # - 900 individuals per branch (90,000 total individuals)
    # Total: 10,000 subsumption axioms + 90,000 class assertions = 100,000 axioms

    num_branches = 100
    depth_per_branch = 100
    individuals_per_branch = 900  # 90,000 total individuals

    total_axioms = 0

    print(f"\nGenerating ontology:")
    print(f"  Branches: {num_branches}")
    print(f"  Depth per branch: {depth_per_branch}")
    print(f"  Individuals per branch: {individuals_per_branch}")

    start = time.perf_counter()

    # Create class hierarchies
    print(f"\n  Creating class hierarchies...")
    for branch in range(num_branches):
        if branch % 10 == 0:
            print(f"    Branch {branch}/{num_branches}...")

        branch_name = f"B{branch}"

        # Root of this branch
        fact = owl_rete_cpp.Fact({
            "type": "subsumption",
            "subclass": f"{branch_name}L0",
            "superclass": "Thing"
        })
        network.add_fact(fact)
        total_axioms += 1

        # Create deep chain
        for level in range(1, depth_per_branch):
            fact = owl_rete_cpp.Fact({
                "type": "subsumption",
                "subclass": f"{branch_name}L{level}",
                "superclass": f"{branch_name}L{level-1}"
            })
            network.add_fact(fact)
            total_axioms += 1

        # Add individuals distributed across levels
        for i in range(individuals_per_branch):
            # Distribute individuals across different levels
            level = i % depth_per_branch
            fact = owl_rete_cpp.Fact({
                "type": "class_assertion",
                "individual": f"{branch_name}I{i}",
                "class": f"{branch_name}L{level}"
            })
            network.add_fact(fact)
            total_axioms += 1

    add_time = time.perf_counter() - start

    print(f"\n✓ Generated {format_number(total_axioms)} axioms")
    print(f"  Fact addition time: {format_time(add_time)}")
    print(f"  Average per axiom: {format_time(add_time / total_axioms)}")

    # Reasoning is automatic/incremental - already happened during fact addition
    print(f"\n🔍 Reasoning complete (automatic/incremental during fact addition)...")
    reason_time = add_time  # Reasoning is included in add_time with automatic reasoning

    fact_count = network.fact_count()
    inferred_facts = fact_count - total_axioms

    print(f"\n📊 Results:")
    print(f"  Initial axioms:      {format_number(total_axioms)}")
    print(f"  Inferred facts:      {format_number(inferred_facts)}")
    print(f"  Total facts:         {format_number(fact_count)}")
    print(f"  ")
    print(f"  Fact addition time:  {format_time(add_time)}")
    print(f"  Reasoning time:      {format_time(reason_time)}")
    print(f"  Total time:          {format_time(add_time + reason_time)}")
    print(f"  ")
    print(f"  Throughput:          {format_number(int(fact_count / (add_time + reason_time)))} facts/sec")
    print(f"  Inference rate:      {format_number(int(inferred_facts / reason_time)) if reason_time > 0 else 0} inferences/sec")

    print("\n✓ 100K axiom test completed")
    return {
        'axioms': total_axioms,
        'total_facts': fact_count,
        'add_time': add_time,
        'reason_time': reason_time,
        'total_time': add_time + reason_time
    }


def print_summary(results_10k, results_100k):
    """Print comparison summary"""
    print("\n" + "=" * 80)
    print("PERFORMANCE COMPARISON SUMMARY")
    print("=" * 80)

    print(f"\n{'Metric':<30} {'10K Axioms':<20} {'100K Axioms':<20}")
    print("-" * 70)
    print(f"{'Initial Axioms':<30} {format_number(results_10k['axioms']):<20} {format_number(results_100k['axioms']):<20}")
    print(f"{'Total Facts':<30} {format_number(results_10k['total_facts']):<20} {format_number(results_100k['total_facts']):<20}")
    print(f"{'Fact Addition Time':<30} {format_time(results_10k['add_time']):<20} {format_time(results_100k['add_time']):<20}")
    print(f"{'Reasoning Time':<30} {format_time(results_10k['reason_time']):<20} {format_time(results_100k['reason_time']):<20}")
    print(f"{'Total Time':<30} {format_time(results_10k['total_time']):<20} {format_time(results_100k['total_time']):<20}")

    throughput_10k = int(results_10k['total_facts'] / results_10k['total_time'])
    throughput_100k = int(results_100k['total_facts'] / results_100k['total_time'])

    print(f"{'Throughput (facts/sec)':<30} {format_number(throughput_10k):<20} {format_number(throughput_100k):<20}")

    # Scaling factor
    scale_factor = results_100k['axioms'] / results_10k['axioms']
    time_factor = results_100k['total_time'] / results_10k['total_time']

    print(f"\n{'Scaling Analysis:':<30}")
    print(f"{'  Size increase':<30} {scale_factor:.1f}x")
    print(f"{'  Time increase':<30} {time_factor:.1f}x")
    print(f"{'  Scaling efficiency':<30} {scale_factor / time_factor:.2f}x (closer to 1.0 = better)")

    print("\n" + "=" * 80)


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("LARGE ONTOLOGY PERFORMANCE TEST SUITE")
    print("Testing RETE network with production-scale ontologies")
    print("=" * 80)

    # Run tests
    results_10k = test_10k_hierarchy()
    results_100k = test_100k_hierarchy()

    # Print summary
    print_summary(results_10k, results_100k)

    print("\n" + "=" * 80)
    print("ALL LARGE ONTOLOGY TESTS COMPLETED")
    print("=" * 80)
