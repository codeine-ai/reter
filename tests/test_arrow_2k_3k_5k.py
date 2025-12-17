"""
Test Arrow conversion for 2K, 3K, 5K results
Focus only on conversion time (skip slow ontology loading)
"""
import sys
import os
import time
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reter import Reter


@pytest.mark.slow
@pytest.mark.parametrize("size", [2000, 3000, 5000])
def test_arrow_conversion_performance(size):
    """Test Arrow conversion performance for different result sizes

    FIXED: Grammar now uses right-recursion to avoid stack overflow with large ontologies.
    """
    print(f"\n{'='*70}")
    print(f"📊 Testing {size} results")
    print(f"{'-'*70}")

    r = Reter()

    # Generate ontology
    print(f"  Generating ontology with {size} individuals...")
    ontology = "\n".join([
        f"Person（p{i}）\nhasAge（p{i}，{20 + (i % 50)}）"
        for i in range(size)
    ])

    print(f"  Loading into RETE network...", end=" ", flush=True)
    start = time.perf_counter()
    r.load_ontology(ontology)
    load_time = (time.perf_counter() - start) * 1000
    print(f"{load_time:.0f} ms")

    print(f"  Building query...", end=" ", flush=True)
    start = time.perf_counter()
    results = r.pattern(
        ("?x", "type", "Person"),
        ("?x", "hasAge", "?age")
    )
    query_time = (time.perf_counter() - start) * 1000
    print(f"{query_time:.0f} ms")

    # Test Arrow conversion 3 times and take best
    times = []
    for i in range(3):
        start = time.perf_counter()
        df = results.to_pandas()
        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)

    best_time = min(times)
    per_row_us = (best_time * 1000) / size
    throughput = size / (best_time / 1000)

    print(f"\n  Arrow Conversion Results:")
    print(f"    Best time:      {best_time:.2f} ms")
    print(f"    Per row:        {per_row_us:.2f} μs")
    print(f"    Throughput:     {throughput:,.0f} rows/sec")
    print(f"    Verified:       {len(df)} rows × {len(df.columns)} columns")

    assert len(df) == size
    assert set(df.columns) == {"?age", "?x"}
    print(f"    ✓ Validation passed!")
