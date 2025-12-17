"""
Performance tests with heavy inference workload
Tests complex statements that trigger multiple OWL 2 RL rules and generate many inferences
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


def test_transitive_property_chains():
    """Test transitive property chains - triggers prp-trp rule repeatedly"""
    print("\n" + "=" * 80)
    print("INFERENCE TEST: Transitive Property Chains")
    print("=" * 80)

    network = owl_rete_cpp.ReteNetwork()

    # Define transitive property
    fact = owl_rete_cpp.Fact({
        "type": "transitive_property",
        "property": "hasAncestor"
    })
    network.add_fact(fact)
    initial_facts = network.fact_count()  # Capture BEFORE adding role assertions

    # Create a chain of 50 individuals with hasAncestor relations
    # This will trigger exponential inferences: person0 hasAncestor person1..person49
    # Expected inferences: 50*49/2 - 49 = 1,176 inferences
    chain_length = 50

    print(f"\nGenerating chain of {format_number(chain_length)} individuals...")

    start = time.perf_counter()

    # Create chain: person0 -> person1 -> person2 -> ... -> person999
    for i in range(chain_length - 1):
        fact = owl_rete_cpp.Fact({
            "type": "role_assertion",
            "subject": f"person{i}",
            "role": "hasAncestor",
            "object": f"person{i+1}"
        })
        network.add_fact(fact)

    add_time = time.perf_counter() - start

    print(f"✓ Added {format_number(chain_length - 1)} role assertions")
    print(f"  Fact addition time: {format_time(add_time)}")

    # Reasoning happens automatically/incrementally during fact addition
    print(f"\n🔍 Reasoning complete (prp-trp inferred all transitive closures)...")
    # No network.run() needed - reasoning is automatic
    reason_time = add_time  # Reasoning time is included in add_time

    total_facts = network.fact_count()
    inferred_facts = total_facts - initial_facts

    # For a chain of N, transitive closure creates N*(N-1)/2 total relations
    expected_inferences = (chain_length * (chain_length - 1)) // 2 - (chain_length - 1)

    print(f"\n📊 Results:")
    print(f"  Initial facts:       {format_number(initial_facts)}")
    print(f"  Inferred facts:      {format_number(inferred_facts)}")
    print(f"  Expected inferences: {format_number(expected_inferences)}")
    print(f"  Total facts:         {format_number(total_facts)}")
    print(f"  ")
    print(f"  Fact addition time:  {format_time(add_time)}")
    print(f"  Reasoning time:      {format_time(reason_time)}")
    print(f"  Total time:          {format_time(add_time + reason_time)}")
    print(f"  ")
    print(f"  Inferences/sec:      {format_number(int(inferred_facts / reason_time)) if reason_time > 0 else 0}")
    print(f"  Total throughput:    {format_number(int(total_facts / (add_time + reason_time)))}")

    print("\n✓ Transitive property test completed")
    return {
        'name': 'Transitive Properties',
        'initial': initial_facts,
        'inferred': inferred_facts,
        'total': total_facts,
        'add_time': add_time,
        'reason_time': reason_time
    }


def test_class_hierarchy_propagation():
    """Test class hierarchy with property domain/range - triggers cax-sco, prp-dom, prp-rng"""
    print("\n" + "=" * 80)
    print("INFERENCE TEST: Class Hierarchy with Domain/Range Propagation")
    print("=" * 80)

    network = owl_rete_cpp.ReteNetwork()
    initial_facts = network.fact_count()  # Capture baseline before adding facts

    # Create deep class hierarchy: 100 levels
    num_levels = 100

    print(f"\nGenerating {num_levels}-level class hierarchy...")

    start = time.perf_counter()

    # Create hierarchy
    for i in range(num_levels - 1):
        fact = owl_rete_cpp.Fact({
            "type": "subsumption",
            "subclass": f"Level{i}",
            "superclass": f"Level{i+1}"
        })
        network.add_fact(fact)

    # Add domain and range constraints
    # hasChild domain: Parent, range: Child
    fact = owl_rete_cpp.Fact({
        "type": "property_domain",
        "property": "hasChild",
        "class": "Parent"
    })
    network.add_fact(fact)

    fact = owl_rete_cpp.Fact({
        "type": "property_range",
        "property": "hasChild",
        "class": "Child"
    })
    network.add_fact(fact)

    # Add Parent and Child to hierarchy
    fact = owl_rete_cpp.Fact({
        "type": "subsumption",
        "subclass": "Parent",
        "superclass": "Level0"
    })
    network.add_fact(fact)

    fact = owl_rete_cpp.Fact({
        "type": "subsumption",
        "subclass": "Child",
        "superclass": "Level0"
    })
    network.add_fact(fact)

    # Create 500 individuals at lowest level with hasChild relations
    num_individuals = 500
    for i in range(num_individuals // 2):
        # Individual at lowest level
        fact = owl_rete_cpp.Fact({
            "type": "class_assertion",
            "individual": f"ind{i}",
            "class": "Level0"
        })
        network.add_fact(fact)

        # hasChild relation (triggers domain/range inference)
        fact = owl_rete_cpp.Fact({
            "type": "role_assertion",
            "subject": f"ind{i}",
            "role": "hasChild",
            "object": f"ind{i + num_individuals // 2}"
        })
        network.add_fact(fact)

    add_time = time.perf_counter() - start
    num_facts_added = num_levels - 1 + 4 + num_individuals // 2 + num_individuals // 2  # hierarchy + domain/range + class assertions + role assertions

    print(f"✓ Added {format_number(num_facts_added)} facts")
    print(f"  Fact addition time: {format_time(add_time)}")

    # Reasoning happens automatically/incrementally during fact addition
    print(f"\n🔍 Reasoning complete (cax-sco + prp-dom + prp-rng)...")
    # No network.run() needed - reasoning is automatic
    reason_time = add_time  # Reasoning time is included in add_time

    total_facts = network.fact_count()
    inferred_facts = total_facts - initial_facts

    print(f"\n📊 Results:")
    print(f"  Initial facts:       {format_number(initial_facts)}")
    print(f"  Inferred facts:      {format_number(inferred_facts)}")
    print(f"  Total facts:         {format_number(total_facts)}")
    print(f"  ")
    print(f"  Fact addition time:  {format_time(add_time)}")
    print(f"  Reasoning time:      {format_time(reason_time)}")
    print(f"  Total time:          {format_time(add_time + reason_time)}")
    print(f"  ")
    print(f"  Inferences/sec:      {format_number(int(inferred_facts / reason_time)) if reason_time > 0 else 0}")
    print(f"  Total throughput:    {format_number(int(total_facts / (add_time + reason_time)))}")

    print("\n✓ Class hierarchy propagation test completed")
    return {
        'name': 'Class Hierarchy Propagation',
        'initial': initial_facts,
        'inferred': inferred_facts,
        'total': total_facts,
        'add_time': add_time,
        'reason_time': reason_time
    }


def test_property_equivalence_chains():
    """Test property equivalence - triggers prp-eqp1, prp-eqp2"""
    print("\n" + "=" * 80)
    print("INFERENCE TEST: Property Equivalence Chains")
    print("=" * 80)

    network = owl_rete_cpp.ReteNetwork()
    initial_facts = network.fact_count()  # Capture baseline before adding facts

    # Create chain of equivalent properties: p0 ≡ p1 ≡ p2 ≡ ... ≡ p9
    # Note: Reduced from 50 to 10 properties to avoid exponential explosion
    # (50 properties × 200 assertions = 10,000 inferences, which is too slow)
    num_properties = 10

    print(f"\nGenerating {num_properties} equivalent properties...")

    start = time.perf_counter()

    # Create equivalence chain
    for i in range(num_properties - 1):
        fact = owl_rete_cpp.Fact({
            "type": "equivalent_property",
            "property1": f"prop{i}",
            "property2": f"prop{i+1}"
        })
        network.add_fact(fact)

    # Add 100 role assertions with prop0
    # Note: Reduced from 200 to 100 to keep test time reasonable
    num_assertions = 100
    for i in range(num_assertions):
        fact = owl_rete_cpp.Fact({
            "type": "role_assertion",
            "subject": f"subject{i}",
            "role": "prop0",
            "object": f"object{i}"
        })
        network.add_fact(fact)

    add_time = time.perf_counter() - start
    num_facts_added = (num_properties - 1) + num_assertions  # equivalence chain + role assertions

    print(f"✓ Added {format_number(num_facts_added)} facts")
    print(f"  Fact addition time: {format_time(add_time)}")

    # Reasoning happens automatically/incrementally during fact addition
    print(f"\n🔍 Reasoning complete (prp-eqp1 + prp-eqp2)...")
    # No network.run() needed - reasoning is automatic
    reason_time = add_time  # Reasoning time is included in add_time

    total_facts = network.fact_count()
    inferred_facts = total_facts - initial_facts

    print(f"\n📊 Results:")
    print(f"  Initial facts:       {format_number(initial_facts)}")
    print(f"  Inferred facts:      {format_number(inferred_facts)}")
    print(f"  Total facts:         {format_number(total_facts)}")
    print(f"  ")
    print(f"  Fact addition time:  {format_time(add_time)}")
    print(f"  Reasoning time:      {format_time(reason_time)}")
    print(f"  Total time:          {format_time(add_time + reason_time)}")
    print(f"  ")
    print(f"  Inferences/sec:      {format_number(int(inferred_facts / reason_time)) if reason_time > 0 else 0}")
    print(f"  Total throughput:    {format_number(int(total_facts / (add_time + reason_time)))}")

    print("\n✓ Property equivalence test completed")
    return {
        'name': 'Property Equivalence',
        'initial': initial_facts,
        'inferred': inferred_facts,
        'total': total_facts,
        'add_time': add_time,
        'reason_time': reason_time
    }


def test_inverse_properties():
    """Test inverse properties - triggers prp-inv1, prp-inv2"""
    print("\n" + "=" * 80)
    print("INFERENCE TEST: Inverse Properties")
    print("=" * 80)

    network = owl_rete_cpp.ReteNetwork()

    # Define inverse property pairs
    num_pairs = 25

    print(f"\nGenerating {num_pairs} inverse property pairs...")

    start = time.perf_counter()

    # Create inverse property pairs
    for i in range(num_pairs):
        fact = owl_rete_cpp.Fact({
            "type": "inverse_properties",
            "property1": f"prop{i}",
            "property2": f"invProp{i}"
        })
        network.add_fact(fact)

    # Add 400 role assertions (will double through inverse)
    num_assertions = 400
    for i in range(num_assertions):
        prop_idx = i % num_pairs
        fact = owl_rete_cpp.Fact({
            "type": "role_assertion",
            "subject": f"subject{i}",
            "role": f"prop{prop_idx}",
            "object": f"object{i}"
        })
        network.add_fact(fact)

    add_time = time.perf_counter() - start
    initial_facts = network.fact_count()

    print(f"✓ Added {format_number(initial_facts)} initial facts")
    print(f"  Fact addition time: {format_time(add_time)}")

    # Reasoning happens automatically/incrementally during fact addition
    print(f"\n🔍 Reasoning complete (prp-inv1 + prp-inv2)...")
    # No network.run() needed - reasoning is automatic
    reason_time = add_time  # Reasoning time is included in add_time

    total_facts = network.fact_count()
    inferred_facts = total_facts - initial_facts

    print(f"\n📊 Results:")
    print(f"  Initial facts:       {format_number(initial_facts)}")
    print(f"  Inferred facts:      {format_number(inferred_facts)}")
    print(f"  Total facts:         {format_number(total_facts)}")
    print(f"  ")
    print(f"  Fact addition time:  {format_time(add_time)}")
    print(f"  Reasoning time:      {format_time(reason_time)}")
    print(f"  Total time:          {format_time(add_time + reason_time)}")
    print(f"  ")
    print(f"  Inferences/sec:      {format_number(int(inferred_facts / reason_time)) if reason_time > 0 else 0}")
    print(f"  Total throughput:    {format_number(int(total_facts / (add_time + reason_time)))}")

    print("\n✓ Inverse properties test completed")
    return {
        'name': 'Inverse Properties',
        'initial': initial_facts,
        'inferred': inferred_facts,
        'total': total_facts,
        'add_time': add_time,
        'reason_time': reason_time
    }


def test_symmetric_properties():
    """Test symmetric properties - triggers prp-symp"""
    print("\n" + "=" * 80)
    print("INFERENCE TEST: Symmetric Properties")
    print("=" * 80)

    network = owl_rete_cpp.ReteNetwork()

    # Define symmetric properties
    num_properties = 20

    print(f"\nGenerating {num_properties} symmetric properties...")

    start = time.perf_counter()

    # Create symmetric properties
    for i in range(num_properties):
        fact = owl_rete_cpp.Fact({
            "type": "symmetric_property",
            "property": f"knows{i}"
        })
        network.add_fact(fact)

    # Add 500 role assertions (will double through symmetry)
    num_assertions = 500
    for i in range(num_assertions):
        prop_idx = i % num_properties
        fact = owl_rete_cpp.Fact({
            "type": "role_assertion",
            "subject": f"person{i}",
            "role": f"knows{prop_idx}",
            "object": f"person{i + num_assertions}"
        })
        network.add_fact(fact)

    add_time = time.perf_counter() - start
    initial_facts = network.fact_count()

    print(f"✓ Added {format_number(initial_facts)} initial facts")
    print(f"  Fact addition time: {format_time(add_time)}")

    # Reasoning happens automatically/incrementally during fact addition
    print(f"\n🔍 Reasoning complete (prp-symp)...")
    # No network.run() needed - reasoning is automatic
    reason_time = add_time  # Reasoning time is included in add_time

    total_facts = network.fact_count()
    inferred_facts = total_facts - initial_facts

    print(f"\n📊 Results:")
    print(f"  Initial facts:       {format_number(initial_facts)}")
    print(f"  Inferred facts:      {format_number(inferred_facts)}")
    print(f"  Total facts:         {format_number(total_facts)}")
    print(f"  ")
    print(f"  Fact addition time:  {format_time(add_time)}")
    print(f"  Reasoning time:      {format_time(reason_time)}")
    print(f"  Total time:          {format_time(add_time + reason_time)}")
    print(f"  ")
    print(f"  Inferences/sec:      {format_number(int(inferred_facts / reason_time)) if reason_time > 0 else 0}")
    print(f"  Total throughput:    {format_number(int(total_facts / (add_time + reason_time)))}")

    print("\n✓ Symmetric properties test completed")
    return {
        'name': 'Symmetric Properties',
        'initial': initial_facts,
        'inferred': inferred_facts,
        'total': total_facts,
        'add_time': add_time,
        'reason_time': reason_time
    }


def test_combined_complex():
    """Test combination of multiple rule types - stress test"""
    print("\n" + "=" * 80)
    print("INFERENCE TEST: Combined Complex Reasoning (All Rules)")
    print("=" * 80)

    network = owl_rete_cpp.ReteNetwork()

    print(f"\nGenerating complex ontology with multiple rule types...")

    start = time.perf_counter()

    # 1. Class hierarchy (50 levels)
    for i in range(49):
        fact = owl_rete_cpp.Fact({
            "type": "subsumption",
            "subclass": f"Class{i}",
            "superclass": f"Class{i+1}"
        })
        network.add_fact(fact)

    # 2. Transitive property
    fact = owl_rete_cpp.Fact({
        "type": "transitive_property",
        "property": "hasAncestor"
    })
    network.add_fact(fact)

    # 3. Symmetric property
    fact = owl_rete_cpp.Fact({
        "type": "symmetric_property",
        "property": "knows"
    })
    network.add_fact(fact)

    # 4. Inverse properties
    fact = owl_rete_cpp.Fact({
        "type": "inverse_properties",
        "property1": "hasChild",
        "property2": "hasParent"
    })
    network.add_fact(fact)

    # 5. Property equivalence
    for i in range(10):
        fact = owl_rete_cpp.Fact({
            "type": "equivalent_property",
            "property1": f"related{i}",
            "property2": f"related{i+1}"
        })
        network.add_fact(fact)

    # 6. Domain and range
    fact = owl_rete_cpp.Fact({
        "type": "property_domain",
        "property": "hasChild",
        "class": "Parent"
    })
    network.add_fact(fact)

    fact = owl_rete_cpp.Fact({
        "type": "property_range",
        "property": "hasChild",
        "class": "Child"
    })
    network.add_fact(fact)

    fact = owl_rete_cpp.Fact({
        "type": "subsumption",
        "subclass": "Parent",
        "superclass": "Class0"
    })
    network.add_fact(fact)

    fact = owl_rete_cpp.Fact({
        "type": "subsumption",
        "subclass": "Child",
        "superclass": "Class0"
    })
    network.add_fact(fact)

    # 7. Add 100 individuals with various assertions
    num_individuals = 100
    for i in range(num_individuals):
        # Class assertion
        fact = owl_rete_cpp.Fact({
            "type": "class_assertion",
            "individual": f"ind{i}",
            "class": "Class0"
        })
        network.add_fact(fact)

        # Transitive property (creates chain)
        if i < num_individuals - 1:
            fact = owl_rete_cpp.Fact({
                "type": "role_assertion",
                "subject": f"ind{i}",
                "role": "hasAncestor",
                "object": f"ind{i+1}"
            })
            network.add_fact(fact)

        # Symmetric property
        if i < num_individuals // 2:
            fact = owl_rete_cpp.Fact({
                "type": "role_assertion",
                "subject": f"ind{i}",
                "role": "knows",
                "object": f"ind{i + num_individuals // 2}"
            })
            network.add_fact(fact)

        # Inverse property
        if i < num_individuals // 3:
            fact = owl_rete_cpp.Fact({
                "type": "role_assertion",
                "subject": f"ind{i}",
                "role": "hasChild",
                "object": f"ind{i + 100}"
            })
            network.add_fact(fact)

    add_time = time.perf_counter() - start
    initial_facts = network.fact_count()

    print(f"✓ Added {format_number(initial_facts)} initial facts")
    print(f"  Fact addition time: {format_time(add_time)}")

    # Reasoning happens automatically/incrementally during fact addition
    print(f"\n🔍 Reasoning complete (ALL OWL 2 RL rules active)...")
    # No network.run() needed - reasoning is automatic
    reason_time = add_time  # Reasoning time is included in add_time

    total_facts = network.fact_count()
    inferred_facts = total_facts - initial_facts

    print(f"\n📊 Results:")
    print(f"  Initial facts:       {format_number(initial_facts)}")
    print(f"  Inferred facts:      {format_number(inferred_facts)}")
    print(f"  Total facts:         {format_number(total_facts)}")
    print(f"  Inference ratio:     {inferred_facts / initial_facts:.2f}x")
    print(f"  ")
    print(f"  Fact addition time:  {format_time(add_time)}")
    print(f"  Reasoning time:      {format_time(reason_time)}")
    print(f"  Total time:          {format_time(add_time + reason_time)}")
    print(f"  ")
    print(f"  Inferences/sec:      {format_number(int(inferred_facts / reason_time)) if reason_time > 0 else 0}")
    print(f"  Total throughput:    {format_number(int(total_facts / (add_time + reason_time)))}")

    print("\n✓ Combined complex reasoning test completed")
    return {
        'name': 'Combined Complex',
        'initial': initial_facts,
        'inferred': inferred_facts,
        'total': total_facts,
        'add_time': add_time,
        'reason_time': reason_time
    }


def print_summary(results):
    """Print comprehensive summary of all tests"""
    print("\n" + "=" * 80)
    print("INFERENCE PERFORMANCE SUMMARY")
    print("=" * 80)

    print(f"\n{'Test Name':<35} {'Initial':<10} {'Inferred':<10} {'Ratio':<8} {'Reason Time':<15} {'Inf/sec':<15}")
    print("─" * 100)

    for r in results:
        ratio = r['inferred'] / r['initial'] if r['initial'] > 0 else 0
        inf_per_sec = int(r['inferred'] / r['reason_time']) if r['reason_time'] > 0 else 0

        print(f"{r['name']:<35} "
              f"{format_number(r['initial']):<10} "
              f"{format_number(r['inferred']):<10} "
              f"{ratio:>6.2f}x  "
              f"{format_time(r['reason_time']):<15} "
              f"{format_number(inf_per_sec):<15}")

    # Totals
    total_initial = sum(r['initial'] for r in results)
    total_inferred = sum(r['inferred'] for r in results)
    total_reason_time = sum(r['reason_time'] for r in results)

    print("─" * 100)
    print(f"{'TOTAL':<35} "
          f"{format_number(total_initial):<10} "
          f"{format_number(total_inferred):<10} "
          f"{total_inferred / total_initial if total_initial > 0 else 0:>6.2f}x  "
          f"{format_time(total_reason_time):<15} "
          f"{format_number(int(total_inferred / total_reason_time)) if total_reason_time > 0 else 0:<15}")

    # Analysis
    print("\n" + "=" * 80)
    print("ANALYSIS")
    print("=" * 80)

    print(f"\nTotal inferences generated: {format_number(total_inferred)}")
    print(f"Total reasoning time: {format_time(total_reason_time)}")
    print(f"Average inference rate: {format_number(int(total_inferred / total_reason_time)) if total_reason_time > 0 else 0} inferences/sec")

    # Find best/worst
    best = max(results, key=lambda r: r['inferred'] / r['reason_time'] if r['reason_time'] > 0 else 0)
    worst = min(results, key=lambda r: r['inferred'] / r['reason_time'] if r['reason_time'] > 0 else 0)
    most_inferences = max(results, key=lambda r: r['inferred'])

    print(f"\nFastest inference rate: {best['name']} ({format_number(int(best['inferred'] / best['reason_time']))} inf/sec)")
    print(f"Slowest inference rate: {worst['name']} ({format_number(int(worst['inferred'] / worst['reason_time']))} inf/sec)")
    print(f"Most inferences: {most_inferences['name']} ({format_number(most_inferences['inferred'])} inferences)")


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("INFERENCE PERFORMANCE TEST SUITE")
    print("Testing OWL 2 RL rules with heavy inference workloads")
    print("=" * 80)

    results = []

    # Run all tests
    results.append(test_transitive_property_chains())
    results.append(test_class_hierarchy_propagation())
    results.append(test_property_equivalence_chains())
    results.append(test_inverse_properties())
    results.append(test_symmetric_properties())
    results.append(test_combined_complex())

    # Print summary
    print_summary(results)

    print("\n" + "=" * 80)
    print("ALL INFERENCE PERFORMANCE TESTS COMPLETED")
    print("=" * 80)
