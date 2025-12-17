#!/usr/bin/env python3
"""
Quick SWRL test - smaller set to verify no infinite loops
"""

import sys
sys.path.insert(0, '.')
from reter import Reter

def test_basic_swrl():
    """Test: Person(x) → Adult(x)"""
    print("1. Basic class atom...")
    r = Reter()
    r.load_ontology("""
        ⊢ Person（⌂x） → Adult（⌂x）
        Person（john）
    """)
    print("   ✓ Passed")

def test_property_chain():
    """Test: hasParent(x,y) ∧ hasParent(y,z) → hasGrandparent(x,z)"""
    print("2. Property chain...")
    r = Reter()
    r.load_ontology("""
        ⊢ hasParent（⌂x，⌂y） ∧ hasParent（⌂y，⌂z） → hasGrandparent（⌂x，⌂z）
        hasParent（alice，bob）
        hasParent（bob，charlie）
    """)
    print("   ✓ Passed")

def test_builtin_add():
    """Test: hasAge(x, age) ∧ :add(new, age, 5) → hasFutureAge(x, new)"""
    print("3. Builtin :add...")
    r = Reter()
    r.load_ontology("""
        ⊢ hasAge（⌂x，⋈age） ∧ ⍚add（⋈new，⋈age，5） → hasFutureAge（⌂x，⋈new）
        hasAge（john，25）
    """)
    print("   ✓ Passed")

def test_builtin_multiply():
    """Test: hasPrice(x, price) ∧ :multiply(total, price, 2) → hasDoublePrice(x, total)"""
    print("4. Builtin :multiply...")
    r = Reter()
    r.load_ontology("""
        ⊢ hasPrice（⌂x，⋈price） ∧ ⍚multiply（⋈total，⋈price，2） → hasDoublePrice（⌂x，⋈total）
        hasPrice（item1，10）
    """)
    print("   ✓ Passed")

def test_multiple_builtins():
    """Test: hasValue(x, v) ∧ :add(tmp, v, 5) ∧ :multiply(result, tmp, 2) → hasResult(x, result)"""
    print("5. Multiple builtins...")
    r = Reter()
    r.load_ontology("""
        ⊢ hasValue（⌂x，⋈v） ∧ ⍚add（⋈tmp，⋈v，5） ∧ ⍚multiply（⋈result，⋈tmp，2） → hasResult（⌂x，⋈result）
        hasValue（obj1，10）
    """)
    print("   ✓ Passed")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("QUICK SWRL TEST SUITE")
    print("="*60)
    
    try:
        test_basic_swrl()
        test_property_chain()
        test_builtin_add()
        test_builtin_multiply()
        test_multiple_builtins()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED - No infinite loops!")
        print("="*60)
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
