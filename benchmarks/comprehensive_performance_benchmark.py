"""
Comprehensive Performance Test for OWL 2 RL Reasoning
Tests all grammar constructs from test_comprehensive_grammar_fixed.py with 1000 instances

This test validates performance and correctness across all supported OWL 2 RL features:
- Class axioms (subsumption, equivalence, disjoint, disjoint union)
- Property axioms (subsumption, equivalence, property chains)
- Assertions (class, property, individual equality/inequality)
- Class expressions (union, intersection, complement)
- Restrictions (someValuesFrom, allValuesFrom)
"""

import sys
import os

# Add PyArrow DLL path before importing anything else
try:
    import pyarrow as pa
    pa.create_library_symlinks()
except (ImportError, AttributeError):
    pass  # PyArrow not available or method doesn't exist

# Use installed package instead of development build
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'rete_cpp'))

import time
from reter import owl_rete_cpp


def format_time(seconds):
    """Format time in appropriate units"""
    if seconds < 0.001:
        return f"{seconds * 1000000:.2f} µs"
    elif seconds < 1:
        return f"{seconds * 1000:.2f} ms"
    else:
        return f"{seconds:.2f} s"


def create_ontology_with_instances(num_instances):
    """
    Create comprehensive ontology with all OWL 2 RL constructs + N instances

    Schema covers:
    1. Class hierarchy (subsumption)
    2. Class equivalence
    3. Disjoint classes
    4. Disjoint union
    5. Property subsumption
    6. Property equivalence
    7. Property chains
    8. Class union
    9. Class intersection
    10. Class complement
    11. SomeValuesFrom restrictions
    12. AllValuesFrom restrictions

    Instances test scalability of reasoning across all constructs
    """
    lines = []

    # ========================================================================
    # SCHEMA: Class Axioms
    # ========================================================================
    lines.append("Dog ⊑ᑦ Animal")
    lines.append("Cat ⊑ᑦ Animal")
    lines.append("Animal ⊑ᑦ LivingThing")
    lines.append("")

    lines.append("Human ≡ᑦ Person")
    lines.append("≡ᑦ（Student，Learner，Pupil）")
    lines.append("")

    lines.append("¬≡ᑦ（Male，Female）")
    lines.append("¬≡ᑦ（Child，Adult）")
    lines.append("")

    lines.append("Parent ¬≡ᑦ（Mother，Father）")
    lines.append("Citizen ¬≡ᑦ（LocalCitizen，ForeignCitizen）")
    lines.append("")

    lines.append("WorkingParent ≡ᑦ Parent ⊓ Employee")
    lines.append("Guardian ≡ᑦ Parent ⊔ LegalGuardian")
    lines.append("NonPerson ≡ᑦ ¬Person")

    # ========================================================================
    # SCHEMA: Property Axioms
    # ========================================================================
    lines.append("")
    lines.append("hasParent ⊑ᴿ hasAncestor")
    lines.append("hasMother ⊑ᴿ hasParent")
    lines.append("hasFather ⊑ᴿ hasParent")
    lines.append("")

    lines.append("spouse ≡ᴿ marriedTo")
    lines.append("≡ᴿ（friend，buddy，pal）")
    lines.append("")

    lines.append("hasParent ∘ hasBrother ⊑ᴿ hasUncle")
    lines.append("hasParent ∘ hasSister ⊑ᴿ hasAunt")
    lines.append("hasMother ∘ hasMother ⊑ᴿ hasGrandmother")

    # ========================================================================
    # SCHEMA: Restrictions
    # ========================================================================
    lines.append("")
    lines.append("ParentOfPerson ≡ᑦ ∃hasChild․Person")
    lines.append("DogOwner ≡ᑦ ∃owns․Dog")
    lines.append("")

    lines.append("HappyParent ≡ᑦ ∀hasChild․Happy")
    lines.append("CaringOwner ≡ᑦ ∀owns․WellCared")

    # ========================================================================
    # INSTANCES: Create N individuals with various assertions
    # ========================================================================
    lines.append("")

    for i in range(num_instances):
        ind = f"ind_{i}"

        # Class assertions (rotate through different classes)
        if i % 10 == 0:
            lines.append(f"Person（{ind}）")
        elif i % 10 == 1:
            lines.append(f"Dog（{ind}）")
        elif i % 10 == 2:
            lines.append(f"Cat（{ind}）")
        elif i % 10 == 3:
            lines.append(f"Mother（{ind}）")  # Will infer Parent
        elif i % 10 == 4:
            lines.append(f"Father（{ind}）")  # Will infer Parent
        elif i % 10 == 5:
            lines.append(f"Employee（{ind}）")
        elif i % 10 == 6:
            lines.append(f"Student（{ind}）")  # Will infer Learner, Pupil
        elif i % 10 == 7:
            lines.append(f"Male（{ind}）")
        elif i % 10 == 8:
            lines.append(f"Female（{ind}）")
        else:
            lines.append(f"LivingThing（{ind}）")

        # Property assertions (every 5th individual)
        if i % 5 == 0 and i + 1 < num_instances:
            target = f"ind_{i+1}"

            if i % 20 == 0:
                # Create parent-child relationships (will trigger property chains)
                lines.append(f"hasParent（{target}，{ind}）")
                lines.append(f"hasChild（{ind}，{target}）")
            elif i % 20 == 5:
                # Create sibling relationships (for property chains)
                if i + 2 < num_instances:
                    sibling = f"ind_{i+2}"
                    lines.append(f"hasBrother（{ind}，{sibling}）")
            elif i % 20 == 10:
                # Create ownership relationships (for restrictions)
                lines.append(f"owns（{ind}，{target}）")
            elif i % 20 == 15:
                # Create friendship relationships (property equivalence)
                lines.append(f"friend（{ind}，{target}）")

        # Individual identity (every 10th)
        if i % 10 == 0 and i + 3 < num_instances:
            # Same individuals
            same = f"ind_{i+3}"
            lines.append(f"{ind} ﹦ {same}")

        # Data properties (every 7th)
        if i % 7 == 0:
            age = 20 + (i % 60)
            lines.append(f"hasAge（{ind}，{age}）")

    return "\n".join(lines)


def run_performance_test(num_instances):
    """Run comprehensive test with N instances"""
    print(f"\n{'='*80}")
    print(f"TEST: {num_instances} INSTANCES")
    print(f"{'='*80}")

    # Create ontology
    ontology = create_ontology_with_instances(num_instances)

    # Load and measure (BUILD FROM SCRATCH)
    net = owl_rete_cpp.ReteNetwork()

    start = time.perf_counter()
    net.load_ontology_from_string(ontology)
    build_time = time.perf_counter() - start
    load_time = build_time  # Keep for backwards compatibility

    # Gather statistics
    total_facts = net.fact_count()
    all_facts = net.get_all_facts()

    # Count by type
    facts_by_type = {}
    for f in all_facts:
        t = f.get('type') or 'unknown'
        facts_by_type[t] = facts_by_type.get(t, 0) + 1

    # Count inferred vs asserted
    inferred_facts = [f for f in all_facts if f.get('inferred') == 'true']
    asserted_facts = total_facts - len(inferred_facts)

    # Get production statistics
    stats = net.get_production_stats()

    # Get profiling statistics
    prof_stats = net.get_profiling_stats()

    # Get loading statistics (optimization metrics)
    loading_stats = net.get_loading_stats()

    # ========================================================================
    # SERIALIZATION BENCHMARK
    # ========================================================================

    # Save network to binary file
    filename = f"benchmark_comprehensive_{num_instances}.pb"

    start = time.perf_counter()
    success = net.save(filename)
    save_time = time.perf_counter() - start

    file_size = 0
    if success and os.path.exists(filename):
        file_size = os.path.getsize(filename)

    # Load network from binary file
    net2 = owl_rete_cpp.ReteNetwork()
    stats_before_load = net2.get_production_stats()

    start = time.perf_counter()
    success = net2.load(filename)
    deserialize_time = time.perf_counter() - start

    stats_after_load = net2.get_production_stats()
    rules_fired_during_load = sum(stats_after_load.values()) - sum(stats_before_load.values())

    loaded_facts = net2.fact_count()

    # Cleanup
    if os.path.exists(filename):
        os.remove(filename)

    # Calculate speedup
    speedup = build_time / deserialize_time if deserialize_time > 0 else 0

    # Print results
    print(f"\n📊 RESULTS:")
    print(f"  Build time:          {format_time(build_time)} (parse + reasoning)")
    print(f"  Total facts:         {total_facts:,}")
    print(f"  Asserted facts:      {asserted_facts:,}")
    print(f"  Inferred facts:      {len(inferred_facts):,}")
    print(f"  Inference ratio:     {len(inferred_facts)/asserted_facts:.2f}x" if asserted_facts > 0 else "")

    print(f"\n💾 SERIALIZATION:")
    print(f"  Save time:           {format_time(save_time)}")
    print(f"  File size:           {file_size:,} bytes ({file_size/1024:.1f} KB)")
    print(f"  Bytes per fact:      {file_size/total_facts:.1f}" if total_facts > 0 else "")

    print(f"\n⚡ DESERIALIZATION:")
    print(f"  Load time:           {format_time(deserialize_time)}")
    print(f"  Facts loaded:        {loaded_facts:,}")
    print(f"  Rules fired:         {rules_fired_during_load} ({'✅ CORRECT' if rules_fired_during_load == 0 else '❌ ERROR'})")
    print(f"  Speedup vs build:    {speedup:.2f}x faster")

    print(f"\n📈 FACTS BY TYPE:")
    for fact_type in sorted(facts_by_type.keys()):
        count = facts_by_type[fact_type]
        pct = count / total_facts * 100
        print(f"  {fact_type:<30} {count:>8,} ({pct:>5.1f}%)")

    print(f"\n🔥 TOP RULE FIRINGS:")
    top_rules = sorted(stats.items(), key=lambda x: x[1], reverse=True)[:15]
    for rule, count in top_rules:
        print(f"  {rule:<35} {count:>8,}")

    print(f"\n⚡ OPTIMIZATION METRICS:")
    beta_idx = loading_stats.get('indexed_beta_activations', 0)
    beta_fallback = loading_stats.get('fallback_beta_activations', 0)
    total_beta = beta_idx + beta_fallback
    if total_beta > 0:
        idx_pct = beta_idx / total_beta * 100
        print(f"  Beta indexed:        {beta_idx:,} ({idx_pct:.1f}%)")
        print(f"  Beta fallback:       {beta_fallback:,} ({100-idx_pct:.1f}%)")

    alpha_checks = prof_stats.get('alpha_memory_checks', 0)
    alpha_acts = prof_stats.get('alpha_activations', 0)
    if alpha_checks > 0:
        alpha_hit = alpha_acts / alpha_checks * 100
        print(f"  Alpha hit rate:      {alpha_hit:.1f}%")

    join_tests = prof_stats.get('join_tests_performed', 0)
    join_passed = prof_stats.get('join_tests_passed', 0)
    if join_tests > 0:
        join_success = join_passed / join_tests * 100
        print(f"  Join success rate:   {join_success:.1f}%")

    # Verify correctness (sample checks)
    print(f"\n✅ CORRECTNESS CHECKS:")

    # Check class hierarchy inference
    subsumptions = [f for f in all_facts if f.get('type') == 'subsumption']
    print(f"  Subsumptions:        {len(subsumptions):,} (schema + inferred)")

    # Check equivalence reasoning
    equivalences = [f for f in all_facts if f.get('type') == 'equivalence']
    print(f"  Equivalences:        {len(equivalences):,} (includes symmetry)")

    # Check disjoint union
    unions = [f for f in all_facts if f.get('type') == 'union']
    print(f"  Unions:              {len(unions):,}")

    # Check intersections
    intersections = [f for f in all_facts if f.get('type') == 'intersection']
    print(f"  Intersections:       {len(intersections):,}")

    # Check property chains
    prop_chains = [f for f in all_facts if f.get('type') == 'property_chain']
    print(f"  Property chains:     {len(prop_chains):,}")

    # Check restrictions
    restrictions = [f for f in all_facts if 'values_from' in f.get('type', '')]
    print(f"  Restrictions:        {len(restrictions):,}")

    # Check validation errors (disjoint violations)
    errors = [f for f in all_facts if f.get('type') == 'validation_error']
    print(f"  Validation errors:   {len(errors):,} (expected for disjoint tests)")

    # Check inferred instances
    instance_ofs = [f for f in all_facts if f.get('type') == 'instance_of']
    inferred_instances = [f for f in instance_ofs if f.get('inferred') == 'true']
    print(f"  Instance inferences: {len(inferred_instances):,}")

    return {
        'instances': num_instances,
        'load_time': load_time,
        'build_time': build_time,
        'save_time': save_time,
        'deserialize_time': deserialize_time,
        'file_size': file_size,
        'speedup': speedup,
        'rules_fired_during_load': rules_fired_during_load,
        'total_facts': total_facts,
        'inferred_facts': len(inferred_facts),
        'facts_by_type': facts_by_type,
        'beta_idx': beta_idx,
        'beta_fallback': beta_fallback,
        'alpha_checks': alpha_checks,
        'join_tests': join_tests,
        'profiling': prof_stats,
        'network': net
    }


# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

print("\n" + "="*80)
print("COMPREHENSIVE OWL 2 RL PERFORMANCE TEST")
print("Testing all grammar constructs with scalable instances")
print("="*80)

# Test configurations
test_configs = [1,2,3,4,5,10, 50, 100, 200, 500, 1000]

results = []

for num_inst in test_configs:
    result = run_performance_test(num_inst)
    results.append(result)


# ============================================================================
# SCALABILITY ANALYSIS
# ============================================================================

print("\n" + "="*80)
print("SCALABILITY ANALYSIS")
print("="*80)

print(f"\n{'Instances':<12} {'Build Time':<15} {'Load Time':<15} {'Speedup':<12} {'Facts':<12} {'Inferred':<12}")
print("-"*95)

for r in results:
    print(f"{r['instances']:<12} {format_time(r['build_time']):<15} {format_time(r['deserialize_time']):<15} "
          f"{r['speedup']:<11.2f}x {r['total_facts']:<12,} {r['inferred_facts']:<12,}")

# Check for O(n²) behavior
print(f"\n{'From':<8} {'To':<8} {'Time Ratio':<15} {'Expected O(n)':<15} {'Status':<20}")
print("-"*80)

for i in range(1, len(results)):
    r1 = results[i-1]
    r2 = results[i]

    inst_ratio = r2['instances'] / r1['instances']
    time_ratio = r2['load_time'] / r1['load_time']

    # For O(n), time ratio should equal instance ratio
    # For O(n²), time ratio would equal instance ratio squared
    if time_ratio > inst_ratio * 1.8:
        status = "⚠️  Superlinear growth"
    elif time_ratio > inst_ratio * 1.2:
        status = "⚠️  Slightly superlinear"
    else:
        status = "✓  Linear scaling"

    print(f"{r1['instances']:<8} {r2['instances']:<8} {time_ratio:<15.2f} {inst_ratio:<15.2f} {status:<20}")


# ============================================================================
# SERIALIZATION PERFORMANCE ANALYSIS
# ============================================================================

print("\n" + "="*80)
print("SERIALIZATION PERFORMANCE")
print("="*80)

print(f"\n{'Instances':<12} {'Save Time':<15} {'Bytes/Fact':<12} {'Speedup':<12} {'Rules Fired':<15}")
print("-"*80)

for r in results:
    bytes_per_fact = r['file_size'] / r['total_facts'] if r['total_facts'] > 0 else 0
    rules_status = "✅ OK" if r['rules_fired_during_load'] == 0 else f"❌ {r['rules_fired_during_load']}"
    print(f"{r['instances']:<12} {format_time(r['save_time']):<15} {bytes_per_fact:<11.1f} "
          f"{r['speedup']:<11.2f}x {rules_status:<15}")

# Serialization speedup analysis
avg_speedup = sum(r['speedup'] for r in results) / len(results) if results else 0
min_speedup = min((r['speedup'] for r in results), default=0)
max_speedup = max((r['speedup'] for r in results), default=0)

print(f"\n📊 SERIALIZATION SUMMARY:")
print(f"  Average speedup:     {avg_speedup:.2f}x")
print(f"  Min speedup:         {min_speedup:.2f}x")
print(f"  Max speedup:         {max_speedup:.2f}x")

# Check if all loads had zero rules fired
all_zero_fires = all(r['rules_fired_during_load'] == 0 for r in results)
if all_zero_fires:
    print(f"  ✅ Zero rules fired during all deserializations (exact state restoration)")
else:
    print(f"  ❌ Some deserializations fired rules (state not exact)")

# File size analysis
avg_bytes = sum(r['file_size'] / r['total_facts'] for r in results if r['total_facts'] > 0) / len([r for r in results if r['total_facts'] > 0])
print(f"  Average bytes/fact:  {avg_bytes:.1f}")


# ============================================================================
# CORRECTNESS VERIFICATION
# ============================================================================

print("\n" + "="*80)
print("CORRECTNESS VERIFICATION (1000 instances)")
print("="*80)

if len(results) > 0:
    final_result = results[-1]
    net = final_result['network']
    all_facts = net.get_all_facts()

    print("\n✅ Verifying specific inferences:")

    # Check that Mother instances are inferred as Parent (disjoint union)
    mothers = [f for f in all_facts if f.get('type') == 'instance_of'
               and f.get('concept') == 'Mother' and f.get('inferred') != 'true']
    parents_from_mothers = [f for f in all_facts if f.get('type') == 'instance_of'
                            and f.get('concept') == 'Parent' and f.get('inferred') == 'true']

    if len(mothers) > 0:
        print(f"  Mother assertions:   {len(mothers)}")
        print(f"  Parent inferences:   {len(parents_from_mothers)}")
        if len(parents_from_mothers) >= len(mothers):
            print(f"  ✓ Disjoint union reasoning working")
        else:
            print(f"  ⚠️  Missing Parent inferences from Mother")

    # Check equivalence reasoning (Student ≡ Learner ≡ Pupil)
    students = [f for f in all_facts if f.get('type') == 'instance_of'
                and f.get('concept') == 'Student' and f.get('inferred') != 'true']
    learners = [f for f in all_facts if f.get('type') == 'instance_of'
                and f.get('concept') in ['Learner', 'Pupil'] and f.get('inferred') == 'true']

    if len(students) > 0:
        print(f"  Student assertions:  {len(students)}")
        print(f"  Learner/Pupil inferences: {len(learners)}")
        if len(learners) >= len(students):
            print(f"  ✓ Equivalence reasoning working")

    # Check property chain reasoning
    hasParent_assertions = [f for f in all_facts if f.get('type') == 'role_assertion'
                            and f.get('role') == 'hasParent' and f.get('inferred') != 'true']
    hasAncestor_inferences = [f for f in all_facts if f.get('type') == 'role_assertion'
                              and f.get('role') == 'hasAncestor' and f.get('inferred') == 'true']

    if len(hasParent_assertions) > 0:
        print(f"  hasParent assertions: {len(hasParent_assertions)}")
        print(f"  hasAncestor inferences: {len(hasAncestor_inferences)}")
        if len(hasAncestor_inferences) >= len(hasParent_assertions):
            print(f"  ✓ Property subsumption working")


# ============================================================================
# NODE SHARING METRICS
# ============================================================================

print("\n" + "="*80)
print("NODE SHARING METRICS (OPS5 Innovation)")
print("="*80)

try:
    metrics = net.get_metrics()

    print(f"\nNetwork Construction Efficiency:")
    print(f"  Alpha sharing ratio:   {metrics['alpha_sharing_ratio']:.2f}:1")
    print(f"  Join sharing ratio:    {metrics['join_sharing_ratio']:.2f}:1")
    print(f"  Beta sharing ratio:    {metrics['beta_sharing_ratio']:.2f}:1")
    print(f"  Overall sharing ratio: {metrics['overall_sharing_ratio']:.2f}:1")

    reduction = (1.0 - 1.0/metrics['overall_sharing_ratio']) * 100 if metrics['overall_sharing_ratio'] > 1 else 0
    print(f"  Overall reduction:     {reduction:.1f}%")

    memory_saved = metrics['estimated_memory_saved_bytes']
    if memory_saved >= 1024 * 1024:
        print(f"  Estimated savings:     {memory_saved / (1024 * 1024):.2f} MB")
    elif memory_saved >= 1024:
        print(f"  Estimated savings:     {memory_saved / 1024:.2f} KB")

except (AttributeError, KeyError):
    print("\n  ℹ️  Node sharing metrics not available")
    print("     Build with ENABLE_METRICS=1 to track node sharing")


print("\n" + "="*80)
print("✓ COMPREHENSIVE PERFORMANCE TEST COMPLETED")
print("="*80)
print()
