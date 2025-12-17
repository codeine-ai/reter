#!/usr/bin/env python3
"""
Minimal test to reproduce SWRL builtin segmentation fault

This is the simplest possible test case that triggers the crash.
The crash occurs when adding facts AFTER a SWRL rule with builtins is loaded.
"""

import sys
sys.path.insert(0, '.')
from reter import Reter

def test_builtin_crash():
    """Minimal test: hasAge(x, age) ∧ :add(new, age, 5) → hasFutureAge(x, new)"""
    print("\n" + "="*70)
    print("MINIMAL SWRL BUILTIN CRASH TEST")
    print("="*70)
    print("STEP A: Creating reasoner...")
    import sys
    sys.stdout.flush()

    r = Reter()
    print("STEP B: Reasoner created")
    sys.stdout.flush()

    # This loads successfully - parser works, typed structures work
    print("\n1. Loading SWRL rule with builtin...")
    sys.stdout.flush()
    r.load_ontology("""
        ⊢ hasAge（⌂x，⋈age） ∧ ⍚add（⋈new，⋈age，5） → hasFutureAge（⌂x，⋈new）
    """)
    print("   ✓ Rule loaded (filter-based production built)")
    sys.stdout.flush()

    # This triggers the segfault
    print("\n2. Adding fact to trigger rule...")
    print("   Adding: hasAge(john, 25)")
    r.load_ontology("""
        hasAge（john，25）
    """)
    print("   ✓ Fact added (should not reach here if crash)")

    print("\n3. Running reasoner...")

    print("\n✓ NO CRASH - builtin filter bug is fixed!")

if __name__ == "__main__":
    try:
        test_builtin_crash()
    except Exception as e:
        print(f"\n✗ Exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
