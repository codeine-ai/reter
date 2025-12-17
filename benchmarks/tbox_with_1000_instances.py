"""
Test RETE performance with TBox + 1000 instances
Based on test_closure_tbox_only.py but adds instances to test scalability
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
    if seconds < 0.001:
        return f"{seconds * 1000000:.2f} µs"
    elif seconds < 1:
        return f"{seconds * 1000:.2f} ms"
    else:
        return f"{seconds:.2f} s"


def create_hierarchy_with_instances(depth, num_instances):
    """Create a deep class hierarchy with instances at the deepest level"""
    lines = ["Root ⊑ᑦ Thing"]

    # Build hierarchy
    for i in range(depth):
        parent = "Root" if i == 0 else f"Class{i-1}"
        child = f"Class{i}"
        lines.append(f"{child} ⊑ᑦ {parent}")

    # Add instances at the deepest level
    deepest_class = f"Class{depth-1}" if depth > 0 else "Root"
    for j in range(num_instances):
        lines.append(f"{deepest_class}（ind_{j}）")

    return "\n".join(lines)


print("\n" + "=" * 80)
print("RETE PERFORMANCE: TBox + INSTANCES")
print("=" * 80)

# Test configurations: (depth, instances)
# Reduced for unoptimized veryold code
test_configs = [
    (5, 10),
    (5, 50),
    (5, 100),
    (5, 200),
    (10, 10),
    (10, 50),
    (10, 100),
    (10, 200),
    (20, 10),
    (20, 50),
    (20, 100),
    (20, 200),
]

print(f"\n{'Config':<25} {'Load Time':<12} {'Facts':<10} {'Subs':<10} {'Instances':<12} {'scm-sco':<10} {'cls-thing':<12}")
print("-" * 100)

results = []

for depth, num_instances in test_configs:
    ontology = create_hierarchy_with_instances(depth, num_instances)

    net = owl_rete_cpp.ReteNetwork()

    # Measure build time (parse + reasoning)
    start = time.perf_counter()
    net.load_ontology_from_string(ontology)
    build_time = time.perf_counter() - start

    total_facts = net.fact_count()

    # Count facts by type
    all_facts = net.get_all_facts()
    subsumptions = [f for f in all_facts if f.get('type') == 'subsumption']
    instance_ofs = [f for f in all_facts if f.get('type') == 'instance_of']

    # Get production stats
    stats = net.get_production_stats()
    scm_sco_fires = stats.get('scm-sco', 0)
    cls_thing_fires = stats.get('cls-thing-1', 0)

    # Get loading stats for performance metrics (Phase 2 optimization)
    loading_stats = net.get_loading_stats()
    beta_idx = loading_stats.get('indexed_beta_activations', 0)
    beta_fallback = loading_stats.get('fallback_beta_activations', 0)

    # Get comprehensive profiling stats (added for bottleneck analysis)
    profiling_stats = net.get_profiling_stats()

    # ====================  ================================================
    # SERIALIZATION BENCHMARK
    # ========================================================================

    # Save network
    filename = f"benchmark_tbox_d{depth}_i{num_instances}.pb"

    start = time.perf_counter()
    success = net.save(filename)
    save_time = time.perf_counter() - start

    file_size = 0
    if success and os.path.exists(filename):
        file_size = os.path.getsize(filename)

    # Load network
    net2 = owl_rete_cpp.ReteNetwork()
    stats_before = net2.get_production_stats()

    start = time.perf_counter()
    success = net2.load(filename)
    deserialize_time = time.perf_counter() - start

    stats_after = net2.get_production_stats()
    rules_fired = sum(stats_after.values()) - sum(stats_before.values())

    loaded_facts = net2.fact_count()

    # Cleanup
    if os.path.exists(filename):
        os.remove(filename)

    # Calculate speedup
    speedup = build_time / deserialize_time if deserialize_time > 0 else 0

    results.append({
        'depth': depth,
        'instances': num_instances,
        'load_time': build_time,  # For backwards compatibility
        'build_time': build_time,
        'save_time': save_time,
        'deserialize_time': deserialize_time,
        'file_size': file_size,
        'speedup': speedup,
        'rules_fired_during_load': rules_fired,
        'total_facts': total_facts,
        'subsumptions': len(subsumptions),
        'instance_ofs': len(instance_ofs),
        'scm_sco_fires': scm_sco_fires,
        'cls_thing_fires': cls_thing_fires,
        'beta_idx': beta_idx,
        'beta_fallback': beta_fallback,
        'profiling': profiling_stats,  # Store all profiling metrics
        'network': net  # Store network for filtering stats
    })

    config_str = f"d={depth}, i={num_instances}"
    print(f"{config_str:<25} {format_time(build_time):<12} {total_facts:<10} "
          f"{len(subsumptions):<10} {len(instance_ofs):<12} {scm_sco_fires:<10} {cls_thing_fires:<12}")


# Performance analysis
print("\n" + "=" * 80)
print("PERFORMANCE SCALING ANALYSIS")
print("=" * 80)

print(f"\n{'Instances':<12} {'Load Time':<15} {'β_idx':<12} {'β_fallback':<12} {'β_idx/inst':<12} {'Facts/inst':<12}")
print("-" * 95)

for r in sorted(results, key=lambda x: x['instances']):
    beta_per_inst = r['beta_idx'] / r['instances'] if r['instances'] > 0 else 0
    facts_per_inst = r['total_facts'] / r['instances'] if r['instances'] > 0 else 0
    print(f"{r['instances']:<12} {format_time(r['load_time']):<15} {r['beta_idx']:<12} "
          f"{r['beta_fallback']:<12} {beta_per_inst:<12.1f} {facts_per_inst:<12.1f}")


# O(n²) detection
print("\n" + "=" * 80)
print("O(n²) DETECTION")
print("=" * 80)

print(f"\n{'From':<8} {'To':<8} {'Time Ratio':<12} {'β_idx Ratio':<12} {'Expected O(n)':<15}")
print("-" * 60)

# Group by depth and compare instance scaling
by_depth = {}
for r in results:
    depth = r['depth']
    if depth not in by_depth:
        by_depth[depth] = []
    by_depth[depth].append(r)

for depth in sorted(by_depth.keys()):
    depth_results = sorted(by_depth[depth], key=lambda x: x['instances'])
    for i in range(1, len(depth_results)):
        r1 = depth_results[i-1]
        r2 = depth_results[i]

        inst_ratio = r2['instances'] / r1['instances']
        time_ratio = r2['load_time'] / r1['load_time']
        beta_ratio = r2['beta_idx'] / r1['beta_idx'] if r1['beta_idx'] > 0 else 0

        print(f"{r1['instances']:<8} {r2['instances']:<8} {time_ratio:<12.2f} "
              f"{beta_ratio:<12.2f} {inst_ratio:<15.2f}")

# Check for O(n²) behavior
print("\n" + "=" * 80)

# Check if beta activations grow quadratically
max_beta_ratio = 0
for depth in by_depth.keys():
    depth_results = sorted(by_depth[depth], key=lambda x: x['instances'])
    for i in range(1, len(depth_results)):
        r1 = depth_results[i-1]
        r2 = depth_results[i]
        inst_ratio = r2['instances'] / r1['instances']
        beta_ratio = r2['beta_idx'] / r1['beta_idx'] if r1['beta_idx'] > 0 else 0
        # For O(n), beta_ratio should equal inst_ratio
        # For O(n²), beta_ratio should equal inst_ratio²
        if beta_ratio > inst_ratio * 1.5:  # Threshold for detecting quadratic growth
            max_beta_ratio = max(max_beta_ratio, beta_ratio / inst_ratio)

if max_beta_ratio > 1.5:
    print(f"⚠️  STRONG O(n²) BEHAVIOR DETECTED!")
    print(f"   Beta activations growing at {max_beta_ratio:.1f}x the instance growth rate")
else:
    print(f"✓  LINEAR GROWTH")
    print(f"   Beta activations growing at {max_beta_ratio:.1f}x, close to expected 1.0x")


# Join indexing optimization effectiveness
print("\n" + "=" * 80)
print("JOIN INDEXING OPTIMIZATION EFFECTIVENESS")
print("=" * 80)

print(f"\n{'Config':<25} {'β_idx':<12} {'β_fallback':<12} {'Index %':<12} {'Optimization':<15}")
print("-" * 85)

for r in results:
    config_str = f"d={r['depth']}, i={r['instances']}"
    total_beta = r['beta_idx'] + r['beta_fallback']
    index_pct = (r['beta_idx'] / total_beta * 100) if total_beta > 0 else 0

    # Estimate speedup: indexed operations are O(k), fallback are O(N)
    # Assume k=10 (average bucket size), N=1000 (avg beta memory size for large workloads)
    # Without index: all operations are O(N) = 1000 time units each
    # With index: indexed ops are O(k) = 10 time units, fallback are O(N) = 1000 time units
    if total_beta > 0:
        without_opt = total_beta * 1000  # All operations at O(N)
        with_opt = r['beta_idx'] * 10 + r['beta_fallback'] * 1000  # Mixed
        speedup = without_opt / with_opt if with_opt > 0 else 1.0
        opt_str = f"{speedup:.2f}x faster"
    else:
        opt_str = "N/A"

    print(f"{config_str:<25} {r['beta_idx']:<12} {r['beta_fallback']:<12} {index_pct:<11.1f}% {opt_str:<15}")


# Rule firing verification
print("\n" + "=" * 80)
print("RULE FIRING PATTERNS")
print("=" * 80)

print(f"\n{'Config':<25} {'cls-thing/inst':<15} {'scm-sco/class':<15}")
print("-" * 60)

for r in results:
    config_str = f"d={r['depth']}, i={r['instances']}"
    cls_thing_per_inst = r['cls_thing_fires'] / r['instances'] if r['instances'] > 0 else 0
    scm_sco_per_class = r['scm_sco_fires'] / r['depth'] if r['depth'] > 0 else 0
    print(f"{config_str:<25} {cls_thing_per_inst:<15.2f} {scm_sco_per_class:<15.2f}")


# Detailed profiling analysis
print("\n" + "=" * 80)
print("DETAILED PROFILING ANALYSIS (Bottleneck Detection)")
print("=" * 80)

# Aggregate profiling stats across all runs
total_prof = {}
for r in results:
    for key, value in r['profiling'].items():
        total_prof[key] = total_prof.get(key, 0) + value

print("\n📊 AGGREGATE PROFILING COUNTERS:")
print("-" * 80)
print(f"\n  Alpha Network:")
print(f"    alpha_activations             : {total_prof.get('alpha_activations', 0):,}")
print(f"    alpha_memory_checks           : {total_prof.get('alpha_memory_checks', 0):,}")
if total_prof.get('alpha_memory_checks', 0) > 0:
    hit_rate = (total_prof.get('alpha_activations', 0) / total_prof.get('alpha_memory_checks', 0)) * 100
    print(f"    Alpha hit rate                : {hit_rate:.1f}%")

print(f"\n  Beta Network:")
print(f"    beta_left_activations         : {total_prof.get('beta_left_activations', 0):,}")
print(f"    beta_right_activations        : {total_prof.get('beta_right_activations', 0):,}")
print(f"    indexed_beta_activations      : {total_prof.get('indexed_beta_activations', 0):,}")
print(f"    fallback_beta_activations     : {total_prof.get('fallback_beta_activations', 0):,}")

print(f"\n  Join Operations:")
print(f"    join_tests_performed          : {total_prof.get('join_tests_performed', 0):,}")
print(f"    join_tests_passed             : {total_prof.get('join_tests_passed', 0):,}")
if total_prof.get('join_tests_performed', 0) > 0:
    success_rate = (total_prof.get('join_tests_passed', 0) / total_prof.get('join_tests_performed', 0)) * 100
    print(f"    Join test success rate        : {success_rate:.1f}%")

print(f"\n  Token & Production:")
print(f"    tokens_created                : {total_prof.get('tokens_created', 0):,}")
print(f"    production_activations        : {total_prof.get('production_activations', 0):,}")

print(f"\n  Predicate Filtering (Jena Innovation):")
# Get WME filtering statistics from all network instances
total_wmes_filtered = sum(r['network'].get_wmes_filtered() for r in results)
total_wmes_processed = sum(r['network'].get_wmes_processed() for r in results)
total_wmes = total_wmes_filtered + total_wmes_processed
if total_wmes > 0:
    filter_pct = total_wmes_filtered / total_wmes * 100
    print(f"    Total WMEs:                   {total_wmes:,}")
    print(f"    WMEs filtered:                {total_wmes_filtered:,} ({filter_pct:.1f}%)")
    print(f"    WMEs processed:               {total_wmes_processed:,} ({100-filter_pct:.1f}%)")
else:
    print(f"    No WME filtering data available")

print(f"\n  Network Structure:")
print(f"    total_alpha_memories          : {total_prof.get('total_alpha_memories', 0):,}")
print(f"    total_beta_memories           : {total_prof.get('total_beta_memories', 0):,}")
print(f"    total_join_nodes              : {total_prof.get('total_join_nodes', 0):,}")

# Per-configuration breakdown
print("\n📈 PER-CONFIGURATION BREAKDOWN:")
print("-" * 80)
print(f"\n{'Config':<15} {'α_checks':<12} {'α_hit%':<10} {'β_tests':<12} {'β_success%':<12} {'Tokens':<10}")
print("-" * 80)

for r in results:
    config = f"d={r['depth']},i={r['instances']}"
    prof = r['profiling']

    alpha_checks = prof.get('alpha_memory_checks', 0)
    alpha_acts = prof.get('alpha_activations', 0)
    alpha_hit_pct = (alpha_acts / alpha_checks * 100) if alpha_checks > 0 else 0

    join_tests = prof.get('join_tests_performed', 0)
    join_passed = prof.get('join_tests_passed', 0)
    join_success_pct = (join_passed / join_tests * 100) if join_tests > 0 else 0

    tokens = prof.get('tokens_created', 0)

    print(f"{config:<15} {alpha_checks:<12,} {alpha_hit_pct:<9.1f}% {join_tests:<12,} {join_success_pct:<11.1f}% {tokens:<10,}")

# Bottleneck identification
print("\n🔍 BOTTLENECK ANALYSIS:")
print("-" * 80)

# Calculate time proportions (rough estimates)
total_alpha_checks = total_prof.get('alpha_memory_checks', 0)
total_join_tests = total_prof.get('join_tests_performed', 0)
total_beta_acts = total_prof.get('indexed_beta_activations', 0) + total_prof.get('fallback_beta_activations', 0)

print(f"\n  Operation counts:")
print(f"    Alpha memory checks   : {total_alpha_checks:,}")
print(f"    Join tests performed  : {total_join_tests:,}")
print(f"    Beta activations      : {total_beta_acts:,}")

# Identify potential bottlenecks
if total_join_tests > total_alpha_checks * 10:
    print(f"\n  ⚠️  BOTTLENECK: Join tests significantly exceed alpha checks ({total_join_tests/total_alpha_checks:.1f}x)")
    print(f"      Recommendation: Optimize join test evaluation or improve join indexing")

fallback_pct = total_prof.get('fallback_beta_activations', 0) / total_beta_acts * 100 if total_beta_acts > 0 else 0
if fallback_pct > 40:
    print(f"\n  ⚠️  BOTTLENECK: {fallback_pct:.1f}% of beta activations use fallback (not indexed)")
    print(f"      Recommendation: Improve join index coverage")
else:
    print(f"\n  ✓  Join indexing effective: {100-fallback_pct:.1f}% of beta activations use hash index")

alpha_hit_rate = total_prof.get('alpha_activations', 0) / total_alpha_checks * 100 if total_alpha_checks > 0 else 0
if alpha_hit_rate < 20:
    print(f"\n  ⚠️  BOTTLENECK: Low alpha memory hit rate ({alpha_hit_rate:.1f}%)")
    print(f"      Recommendation: Many hash lookups don't find matching alpha memories")
else:
    print(f"\n  ✓  Alpha network efficient: {alpha_hit_rate:.1f}% hit rate")

# ============================================================================
# NODE SHARING METRICS (OPS5 Innovation - Phase 2)
# ============================================================================

print("\n" + "=" * 80)
print("NODE SHARING METRICS (OPS5 Innovation)")
print("=" * 80)

# Check if metrics are available (requires ENABLE_METRICS compile flag)
try:
    metrics = net.get_metrics()

    print(f"\nNetwork Construction Efficiency:")
    print(f"  Alpha Memories:")
    print(f"    Requested (virtual): {int(metrics['virtual_alpha_nodes'])}")
    print(f"    Created (real):      {int(metrics['real_alpha_nodes'])}")
    print(f"    Sharing ratio:       {metrics['alpha_sharing_ratio']:.2f}:1")
    alpha_reduction = (1.0 - 1.0/metrics['alpha_sharing_ratio']) * 100 if metrics['alpha_sharing_ratio'] > 1 else 0
    print(f"    Reduction:           {alpha_reduction:.1f}%")

    print(f"\n  Join Nodes:")
    print(f"    Requested (virtual): {int(metrics['virtual_join_nodes'])}")
    print(f"    Created (real):      {int(metrics['real_join_nodes'])}")
    print(f"    Sharing ratio:       {metrics['join_sharing_ratio']:.2f}:1")

    print(f"\n  Beta Memories:")
    print(f"    Requested (virtual): {int(metrics['virtual_beta_nodes'])}")
    print(f"    Created (real):      {int(metrics['real_beta_nodes'])}")
    print(f"    Sharing ratio:       {metrics['beta_sharing_ratio']:.2f}:1")

    total_virtual = int(metrics['virtual_alpha_nodes'] + metrics['virtual_join_nodes'] + metrics['virtual_beta_nodes'])
    total_real = int(metrics['real_alpha_nodes'] + metrics['real_join_nodes'] + metrics['real_beta_nodes'])

    print(f"\n  Overall:")
    print(f"    Total nodes requested: {total_virtual}")
    print(f"    Total nodes created:   {total_real}")
    print(f"    Overall ratio:         {metrics['overall_sharing_ratio']:.2f}:1")
    overall_reduction = (1.0 - 1.0/metrics['overall_sharing_ratio']) * 100 if metrics['overall_sharing_ratio'] > 1 else 0
    print(f"    Overall reduction:     {overall_reduction:.1f}%")

    memory_saved = metrics['estimated_memory_saved_bytes']
    if memory_saved >= 1024 * 1024:
        print(f"    Estimated savings:     {memory_saved / (1024 * 1024):.2f} MB")
    elif memory_saved >= 1024:
        print(f"    Estimated savings:     {memory_saved / 1024:.2f} KB")
    else:
        print(f"    Estimated savings:     {int(memory_saved)} bytes")

    # Analysis
    print(f"\n  Analysis:")
    if metrics['alpha_sharing_ratio'] > 5.0:
        print(f"    ✓ Excellent alpha memory sharing ({metrics['alpha_sharing_ratio']:.1f}:1)")
        print(f"      Many productions share identical constant tests")
    elif metrics['alpha_sharing_ratio'] > 2.0:
        print(f"    ✓ Good alpha memory sharing ({metrics['alpha_sharing_ratio']:.1f}:1)")
    else:
        print(f"    ⚠️  Low alpha memory sharing ({metrics['alpha_sharing_ratio']:.1f}:1)")
        print(f"      Productions have unique constant test patterns")

    if metrics['join_sharing_ratio'] > 1.5:
        print(f"    ✓ Join nodes are being shared ({metrics['join_sharing_ratio']:.1f}:1)")
    else:
        print(f"    ℹ️  No join node sharing (each production has unique structure)")

    if overall_reduction > 30:
        print(f"    ✓ Strong overall sharing: {overall_reduction:.0f}% node reduction")
    elif overall_reduction > 15:
        print(f"    ✓ Moderate overall sharing: {overall_reduction:.0f}% node reduction")
    else:
        print(f"    ℹ️  Limited sharing: {overall_reduction:.0f}% node reduction")

except AttributeError:
    print("\n  ℹ️  Node sharing metrics not available")
    print("     Build with ENABLE_METRICS=1 to track node sharing")
    print("     Command: cd rete_cpp && python setup.py build_ext --inplace")


# ============================================================================
# SERIALIZATION PERFORMANCE ANALYSIS
# ============================================================================

print("\n" + "=" * 80)
print("SERIALIZATION PERFORMANCE ANALYSIS")
print("=" * 80)

print(f"\n{'Config':<15} {'Build(s)':<12} {'Save(s)':<12} {'Load(s)':<12} {'Speedup':<10} {'Size(KB)':<12} {'Rules':<8}")
print("-" * 100)

for r in results:
    config_str = f"d={r['depth']},i={r['instances']}"
    file_size_kb = r['file_size'] / 1024
    print(f"{config_str:<15} {r['build_time']:<12.4f} {r['save_time']:<12.4f} "
          f"{r['deserialize_time']:<12.4f} {r['speedup']:<9.2f}x {file_size_kb:<11.1f} {r['rules_fired_during_load']:<8}")

# Analysis
print("\n" + "=" * 80)
print("SERIALIZATION ANALYSIS")
print("=" * 80)

# Speedup analysis
avg_speedup = sum(r['speedup'] for r in results) / len(results) if results else 0
print(f"\nAverage speedup: {avg_speedup:.2f}x")

if avg_speedup >= 10.0:
    print("✅ EXCELLENT: Serialization provides >10x faster loading")
elif avg_speedup >= 5.0:
    print(f"✅ GOOD: Serialization provides {avg_speedup:.1f}x faster loading")
elif avg_speedup >= 2.0:
    print(f"✓  MODERATE: Serialization provides {avg_speedup:.1f}x faster loading")
else:
    print(f"⚠️  LOW: Only {avg_speedup:.1f}x speedup from serialization")

# Check rules fired
total_rules_fired = sum(r['rules_fired_during_load'] for r in results)
if total_rules_fired == 0:
    print("✅ SUCCESS: Zero rules fired during deserialization (all tests)")
else:
    print(f"❌ FAILURE: {total_rules_fired} rules fired during deserialization")

# File size efficiency
if results:
    avg_bytes_per_fact = sum(r['file_size'] / r['total_facts'] for r in results if r['total_facts'] > 0) / len(results)
    print(f"\nAverage file size: {avg_bytes_per_fact:.1f} bytes per fact")

    if avg_bytes_per_fact < 500:
        print("✅ EXCELLENT: Compact file format")
    elif avg_bytes_per_fact < 1000:
        print("✅ GOOD: Reasonable file format")
    else:
        print("⚠️  File format could be more compact")

# Scaling analysis
print("\nScaling analysis:")
by_depth = {}
for r in results:
    depth = r['depth']
    if depth not in by_depth:
        by_depth[depth] = []
    by_depth[depth].append(r)

for depth in sorted(by_depth.keys()):
    depth_results = sorted(by_depth[depth], key=lambda x: x['instances'])
    if len(depth_results) >= 2:
        r_min = depth_results[0]
        r_max = depth_results[-1]
        inst_ratio = r_max['instances'] / r_min['instances']
        build_ratio = r_max['build_time'] / r_min['build_time']
        load_ratio = r_max['deserialize_time'] / r_min['deserialize_time']

        print(f"  Depth {depth}: {r_min['instances']}->{r_max['instances']} instances ({inst_ratio:.1f}x)")
        print(f"    Build time scales: {build_ratio:.2f}x")
        print(f"    Load time scales:  {load_ratio:.2f}x")

        if load_ratio < build_ratio * 0.7:
            print(f"    ✓  Deserialization scales better than building")
        else:
            print(f"    ⚠️  Deserialization scales similarly to building")

print("\n✓ Test completed")
