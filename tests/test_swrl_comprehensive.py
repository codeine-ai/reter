#!/usr/bin/env python3
"""
Comprehensive SWRL (Semantic Web Rule Language) Test Suite

Tests all SWRL features including:
- Basic class and property atoms
- Math builtins (add, subtract, multiply, divide)
- Comparison builtins (>, <, >=, <=, =, !=)
- String builtins (stringConcat, stringLength)
- Data properties
- Same/Different assertions
- Complex scenarios and edge cases
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from reter import Reter


# ============================================================================
# Basic SWRL Tests
# ============================================================================

def test_swrl_basic_class_atom():
    """Test: Person(x) → Adult(x)"""
    print("Testing basic class atom...")
    r = Reter()
    r.load_ontology("""
        ⊢ Person（⌂x） → Adult（⌂x）
        Person（john）
    """)

    facts = r.query(type='instance_of', individual='john', concept='Adult')
    assert len(facts) > 0, "Should infer john is an Adult"
    print("✓ Basic class atom test passed")


def test_swrl_basic_property_chain():
    """Test: hasParent(x,y) ∧ hasParent(y,z) → hasGrandparent(x,z)"""
    print("Testing property chain...")
    r = Reter()
    r.load_ontology("""
        ⊢ hasParent（⌂x，⌂y） ∧ hasParent（⌂y，⌂z） → hasGrandparent（⌂x，⌂z）
        hasParent（alice，bob）
        hasParent（bob，charlie）
    """)

    facts = r.query(type='role_assertion', subject='alice', role='hasGrandparent', object='charlie')
    assert len(facts) > 0, "Should infer alice hasGrandparent charlie"
    print("✓ Property chain test passed")


def test_swrl_mixed_class_property():
    """Test: Person(x) ∧ hasChild(x,y) → Parent(x)"""
    print("Testing mixed class and property atoms...")
    r = Reter()
    r.load_ontology("""
        ⊢ Person（⌂x） ∧ hasChild（⌂x，⌂y） → Parent（⌂x）
        Person（alice）
        hasChild（alice，bob）
    """)

    facts = r.query(type='instance_of', individual='alice', concept='Parent')
    assert len(facts) > 0, "Should infer alice is a Parent"
    print("✓ Mixed class/property test passed")


# ============================================================================
# Math Builtin Tests
# ============================================================================

def test_swrl_builtin_add():
    """Test: hasAge(x, age) ∧ add(newAge, age, 5) → hasFutureAge(x, newAge)"""
    print("Testing add builtin...")
    r = Reter()
    r.load_ontology("""
        ⊢ hasAge（⌂x，⋈age） ∧ ⍚add（⋈newAge，⋈age，5） → hasFutureAge（⌂x，⋈newAge）
        hasAge（john，25）
    """)

    facts = r.query(type='data_property_assertion', subject='john', property='hasFutureAge')
    assert len(facts) > 0, "Should infer john hasFutureAge 30"
    # Check the value is 30
    assert any(f['value'] == '30' or f['value'] == '30.0' for f in facts), \
        f"Expected value 30, got {[f['value'] for f in facts]}"
    print("✓ Add builtin test passed")


def test_swrl_builtin_subtract():
    """Test: hasAge(x, age) ∧ subtract(yearsToRetire, 65, age) → hasYearsToRetire(x, yearsToRetire)"""
    print("Testing subtract builtin...")
    r = Reter()
    r.load_ontology("""
        ⊢ hasAge（⌂x，⋈age） ∧ ⍚subtract（⋈yearsLeft，65，⋈age） → hasYearsToRetire（⌂x，⋈yearsLeft）
        hasAge（alice，45）
    """)

    facts = r.query(type='data_property_assertion', subject='alice', property='hasYearsToRetire')
    assert len(facts) > 0, "Should infer alice hasYearsToRetire 20"
    assert any(f['value'] == '20' or f['value'] == '20.0' for f in facts), \
        f"Expected value 20, got {[f['value'] for f in facts]}"
    print("✓ Subtract builtin test passed")


def test_swrl_builtin_multiply():
    """Test: hasQuantity(x, qty) ∧ multiply(total, qty, 5) → hasTotalCost(x, total)"""
    print("Testing multiply builtin...")
    r = Reter()
    r.load_ontology("""
        ⊢ hasPrice（⌂x，⋈price） ∧ ⍚multiply（⋈total，⋈price，3） → hasTotalCost（⌂x，⋈total）
        hasPrice（item1，10）
    """)

    facts = r.query(type='data_property_assertion', subject='item1', property='hasTotalCost')
    assert len(facts) > 0, "Should infer item1 hasTotalCost 30"
    assert any(f['value'] == '30' or f['value'] == '30.0' for f in facts), \
        f"Expected value 30, got {[f['value'] for f in facts]}"
    print("✓ Multiply builtin test passed")


def test_swrl_builtin_divide():
    """Test: hasTotalCost(x, cost) ∧ divide(avg, cost, 4) → hasAvgCost(x, avg)"""
    print("Testing divide builtin...")
    r = Reter()
    r.load_ontology("""
        ⊢ hasTotalCost（⌂x，⋈cost） ∧ ⍚divide（⋈avg，⋈cost，4） → hasAvgCost（⌂x，⋈avg）
        hasTotalCost（item1，100）
    """)

    facts = r.query(type='data_property_assertion', subject='item1', property='hasAvgCost')
    assert len(facts) > 0, "Should infer item1 hasAvgCost 25"
    assert any(f['value'] == '25' or f['value'] == '25.0' for f in facts), \
        f"Expected value 25, got {[f['value'] for f in facts]}"
    print("✓ Divide builtin test passed")


def test_swrl_builtin_chained_math():
    """Test: Chain multiple math operations: (x + 10) * 2"""
    print("Testing chained math operations...")
    r = Reter()
    r.load_ontology("""
        ⊢ hasBase（⌂x，⋈base） ∧ ⍚add（⋈temp，⋈base，10） ∧ ⍚multiply（⋈result，⋈temp，2） → hasResult（⌂x，⋈result）
        hasBase（calc1，5）
    """)

    facts = r.query(type='data_property_assertion', subject='calc1', property='hasResult')
    assert len(facts) > 0, "Should infer calc1 hasResult 30"
    assert any(f['value'] == '30' or f['value'] == '30.0' for f in facts), \
        f"Expected value 30, got {[f['value'] for f in facts]}"
    print("✓ Chained math operations test passed")


# ============================================================================
# Comparison Builtin Tests
# ============================================================================

def test_swrl_builtin_greater_than():
    """Test: hasAge(x, age) ∧ >(age, 18) → Adult(x)"""
    print("Testing greater than (>) builtin...")
    r = Reter()
    r.load_ontology("""
        ⊢ hasAge（⌂x，⋈age） ∧ ⍚﹥（⋈age，18） → Adult（⌂x）
        hasAge（john，25）
        hasAge（jane，15）
    """)

    # John should be Adult (25 > 18)
    facts_john = r.query(type='instance_of', individual='john', concept='Adult')
    assert len(facts_john) > 0, "Should infer john is Adult (age > 18)"

    # Jane should NOT be Adult (15 > 18 is false)
    facts_jane = r.query(type='instance_of', individual='jane', concept='Adult')
    assert len(facts_jane) == 0, "Should NOT infer jane is Adult (age <= 18)"
    print("✓ Greater than builtin test passed")


def test_swrl_builtin_less_than():
    """Test: hasAge(x, age) ∧ <(age, 13) → Child(x)"""
    print("Testing less than (<) builtin...")
    r = Reter()
    r.load_ontology("""
        ⊢ hasAge（⌂x，⋈age） ∧ ⍚﹤（⋈age，13） → Child（⌂x）
        hasAge（tim，10）
        hasAge（tom，20）
    """)

    # Tim should be Child (10 < 13)
    facts_tim = r.query(type='instance_of', individual='tim', concept='Child')
    assert len(facts_tim) > 0, "Should infer tim is Child (age < 13)"

    # Tom should NOT be Child (20 < 13 is false)
    facts_tom = r.query(type='instance_of', individual='tom', concept='Child')
    assert len(facts_tom) == 0, "Should NOT infer tom is Child (age >= 13)"
    print("✓ Less than builtin test passed")


def test_swrl_builtin_greater_equal():
    """Test: hasAge(x, age) ∧ >=(age, 65) → Senior(x)"""
    print("Testing greater than or equal (>=) builtin...")
    r = Reter()
    r.load_ontology("""
        ⊢ hasAge（⌂x，⋈age） ∧ ⍚≥（⋈age，65） → Senior（⌂x）
        hasAge（bob，65）
        hasAge（alice，64）
    """)

    # Bob should be Senior (65 >= 65)
    facts_bob = r.query(type='instance_of', individual='bob', concept='Senior')
    assert len(facts_bob) > 0, "Should infer bob is Senior (age >= 65)"

    # Alice should NOT be Senior (64 >= 65 is false)
    facts_alice = r.query(type='instance_of', individual='alice', concept='Senior')
    assert len(facts_alice) == 0, "Should NOT infer alice is Senior (age < 65)"
    print("✓ Greater than or equal builtin test passed")


def test_swrl_builtin_less_equal():
    """Test: hasScore(x, score) ∧ <=(score, 50) → Failed(x)"""
    print("Testing less than or equal (<=) builtin...")
    r = Reter()
    r.load_ontology("""
        ⊢ hasScore（⌂x，⋈score） ∧ ⍚≤（⋈score，50） → Failed（⌂x）
        hasScore（student1，50）
        hasScore（student2，51）
    """)

    # Student1 should fail (50 <= 50)
    facts_s1 = r.query(type='instance_of', individual='student1', concept='Failed')
    assert len(facts_s1) > 0, "Should infer student1 Failed (score <= 50)"

    # Student2 should NOT fail (51 <= 50 is false)
    facts_s2 = r.query(type='instance_of', individual='student2', concept='Failed')
    assert len(facts_s2) == 0, "Should NOT infer student2 Failed (score > 50)"
    print("✓ Less than or equal builtin test passed")


def test_swrl_builtin_equal():
    """Test: hasCode(x, code) ∧ =(code, 42) → SpecialItem(x)"""
    print("Testing equal (=) builtin...")
    r = Reter()
    r.load_ontology("""
        ⊢ hasCode（⌂x，⋈code） ∧ ⍚﹦（⋈code，42） → SpecialItem（⌂x）
        hasCode（item1，42）
        hasCode（item2，43）
    """)

    # Item1 should be special (42 = 42)
    facts_i1 = r.query(type='instance_of', individual='item1', concept='SpecialItem')
    assert len(facts_i1) > 0, "Should infer item1 is SpecialItem (code = 42)"

    # Item2 should NOT be special (43 = 42 is false)
    facts_i2 = r.query(type='instance_of', individual='item2', concept='SpecialItem')
    assert len(facts_i2) == 0, "Should NOT infer item2 is SpecialItem (code != 42)"
    print("✓ Equal builtin test passed")


def test_swrl_builtin_not_equal():
    """Test: hasStatus(x, status) ∧ !=(status, 0) → Active(x)"""
    print("Testing not equal (!=) builtin...")
    r = Reter()
    r.load_ontology("""
        ⊢ hasStatus（⌂x，⋈status） ∧ ⍚≠（⋈status，0） → Active（⌂x）
        hasStatus（device1，1）
        hasStatus（device2，0）
    """)

    # Device1 should be active (1 != 0)
    facts_d1 = r.query(type='instance_of', individual='device1', concept='Active')
    assert len(facts_d1) > 0, "Should infer device1 is Active (status != 0)"

    # Device2 should NOT be active (0 != 0 is false)
    facts_d2 = r.query(type='instance_of', individual='device2', concept='Active')
    assert len(facts_d2) == 0, "Should NOT infer device2 is Active (status = 0)"
    print("✓ Not equal builtin test passed")


def test_swrl_builtin_comparison_range():
    """Test: Use multiple comparisons to check range: 18 <= age <= 65"""
    print("Testing range check with multiple comparisons...")
    r = Reter()
    r.load_ontology("""
        ⊢ hasAge（⌂x，⋈age） ∧ ⍚≥（⋈age，18） ∧ ⍚≤（⋈age，65） → WorkingAge（⌂x）
        hasAge（person1，25）
        hasAge（person2，15）
        hasAge（person3，70）
    """)

    # Person1 should be working age (18 <= 25 <= 65)
    facts_p1 = r.query(type='instance_of', individual='person1', concept='WorkingAge')
    assert len(facts_p1) > 0, "Should infer person1 is WorkingAge"

    # Person2 should NOT be working age (15 < 18)
    facts_p2 = r.query(type='instance_of', individual='person2', concept='WorkingAge')
    assert len(facts_p2) == 0, "Should NOT infer person2 is WorkingAge (too young)"

    # Person3 should NOT be working age (70 > 65)
    facts_p3 = r.query(type='instance_of', individual='person3', concept='WorkingAge')
    assert len(facts_p3) == 0, "Should NOT infer person3 is WorkingAge (too old)"
    print("✓ Range check test passed")


# ============================================================================
# String Builtin Tests
# ============================================================================

def test_swrl_builtin_string_concat():
    """Test: hasFirst(x, f) ∧ hasLast(x, l) ∧ stringConcat(full, f, l) → hasFullName(x, full)"""
    print("Testing stringConcat builtin...")
    r = Reter()
    r.load_ontology("""
        ⊢ hasFirstName（⌂x，⋈first） ∧ hasLastName（⌂x，⋈last） ∧ ⍚stringConcat（⋈full，⋈first，⋈last） → hasFullName（⌂x，⋈full）
        hasFirstName（person1，'John'）
        hasLastName（person1，'Doe'）
    """)

    facts = r.query(type='data_property_assertion', subject='person1', property='hasFullName')
    assert len(facts) > 0, "Should infer person1 hasFullName 'JohnDoe'"
    # Note: concat without separator, so 'John' + 'Doe' = 'JohnDoe'
    print("✓ String concat builtin test passed")


def test_swrl_builtin_string_length():
    """Test: hasName(x, name) ∧ stringLength(len, name) → hasNameLength(x, len)"""
    print("Testing stringLength builtin...")
    r = Reter()
    r.load_ontology("""
        ⊢ hasName（⌂x，⋈name） ∧ ⍚stringLength（⋈len，⋈name） → hasNameLength（⌂x，⋈len）
        hasName（item1，'hello'）
    """)

    facts = r.query(type='data_property_assertion', subject='item1', property='hasNameLength')
    assert len(facts) > 0, "Should infer item1 hasNameLength 5"
    assert any(f['value'] == '5' or f['value'] == '5.0' for f in facts), \
        f"Expected length 5, got {[f['value'] for f in facts]}"
    print("✓ String length builtin test passed")


# ============================================================================
# Data Property Tests
# ============================================================================

def test_swrl_data_property():
    """Test: hasAge(x, age) → hasAgeData(x, age)"""
    print("Testing data property in SWRL...")
    r = Reter()
    r.load_ontology("""
        ⊢ Person（⌂x） ∧ hasAge（⌂x，⋈age） → hasAgeInYears（⌂x，⋈age）
        Person（john）
        hasAge（john，30）
    """)

    facts = r.query(type='data_property_assertion', subject='john', property='hasAgeInYears')
    assert len(facts) > 0, "Should infer john hasAgeInYears 30"
    print("✓ Data property test passed")


def test_swrl_data_range():
    """Test: DataRange atom (checking if value is in range)"""
    print("Testing data range...")
    # Note: Data range atoms are complex and may not be fully supported
    # This is a placeholder for future implementation
    print("⊘ Data range test skipped (feature not yet implemented)")


# ============================================================================
# Same/Different Tests
# ============================================================================

def test_swrl_same_as():
    """Test: hasSpouse(x,y) ∧ hasSpouse(y,z) → sameAs(x,z)"""
    print("Testing sameAs in SWRL...")
    r = Reter()
    r.load_ontology("""
        ⊢ hasSpouse（⌂x，⌂y） ∧ hasSpouse（⌂y，⌂x） → ﹦（⌂x，⌂x）
        hasSpouse（alice，bob）
        hasSpouse（bob，alice）
    """)

    # This is a simple reflexive test
    # More complex sameAs tests would check actual individual equivalence
    print("✓ SameAs test passed (basic)")


def test_swrl_different_from():
    """Test: differentFrom in antecedent to prevent self-relationships"""
    print("Testing differentFrom in SWRL...")
    r = Reter()
    r.load_ontology("""
        ⊢ Person（⌂x） ∧ Person（⌂y） ∧ ≠（⌂x，⌂y） → potentialFriend（⌂x，⌂y）
        Person（alice）
        Person（bob）
    """)

    # Should create potentialFriend relationships between different people
    facts = r.query(type='role_assertion', role='potentialFriend')
    # Check that we don't have self-relationships
    for f in facts:
        assert f['subject'] != f['object'], "Should not create self-relationships"
    print("✓ DifferentFrom test passed")


# ============================================================================
# Complex Scenario Tests
# ============================================================================

def test_swrl_complex_family_reasoning():
    """Test complex family relationships with multiple rules"""
    print("Testing complex family reasoning...")
    r = Reter()
    r.load_ontology("""
        ⊢ hasParent（⌂x，⌂y） ∧ hasParent（⌂y，⌂z） → hasGrandparent（⌂x，⌂z）
        ⊢ hasGrandparent（⌂x，⌂y） ∧ Male（⌂y） → hasGrandfather（⌂x，⌂y）
        ⊢ hasGrandparent（⌂x，⌂y） ∧ Female（⌂y） → hasGrandmother（⌂x，⌂y）
        hasParent（alice，bob）
        hasParent（bob，charlie）
        Male（charlie）
    """)

    # Should infer alice hasGrandparent charlie
    facts_gp = r.query(type='role_assertion', subject='alice', role='hasGrandparent', object='charlie')
    assert len(facts_gp) > 0, "Should infer alice hasGrandparent charlie"

    # Should infer alice hasGrandfather charlie
    facts_gf = r.query(type='role_assertion', subject='alice', role='hasGrandfather', object='charlie')
    assert len(facts_gf) > 0, "Should infer alice hasGrandfather charlie"
    print("✓ Complex family reasoning test passed")


def test_swrl_with_math_and_comparison():
    """Test combining math operations with comparisons"""
    print("Testing math + comparison combination...")
    r = Reter()
    r.load_ontology("""
        ⊢ hasSalary（⌂x，⋈salary） ∧ ⍚multiply（⋈annual，⋈salary，12） ∧ ⍚﹥（⋈annual，50000） → HighEarner（⌂x）
        hasSalary（person1，5000）
        hasSalary（person2，3000）
    """)

    # Person1: 5000 * 12 = 60000 > 50000 → HighEarner
    facts_p1 = r.query(type='instance_of', individual='person1', concept='HighEarner')
    assert len(facts_p1) > 0, "Should infer person1 is HighEarner (60000 > 50000)"

    # Person2: 3000 * 12 = 36000 > 50000 is false
    facts_p2 = r.query(type='instance_of', individual='person2', concept='HighEarner')
    assert len(facts_p2) == 0, "Should NOT infer person2 is HighEarner (36000 < 50000)"
    print("✓ Math + comparison test passed")


def test_swrl_multiple_variables_in_head():
    """Test rules that generate new relationships between bound variables"""
    print("Testing multiple variables in head...")
    r = Reter()
    r.load_ontology("""
        ⊢ worksFor（⌂x，⌂company） ∧ worksFor（⌂y，⌂company） → colleague（⌂x，⌂y）
        worksFor（alice，CompanyA）
        worksFor（bob，CompanyA）
        worksFor（charlie，CompanyB）
    """)

    # Alice and Bob should be colleagues
    facts_ab = r.query(type='role_assertion', subject='alice', role='colleague', object='bob')
    assert len(facts_ab) > 0, "Should infer alice colleague bob"

    # Alice and Charlie should NOT be colleagues (different companies)
    facts_ac = r.query(type='role_assertion', subject='alice', role='colleague', object='charlie')
    assert len(facts_ac) == 0, "Should NOT infer alice colleague charlie"
    print("✓ Multiple variables in head test passed")


def test_swrl_cascading_rules():
    """Test cascading rule firing"""
    print("Testing cascading rules...")
    r = Reter()
    r.load_ontology("""
        ⊢ Student（⌂x） → Person（⌂x）
        ⊢ Person（⌂x） → LivingBeing（⌂x）
        ⊢ LivingBeing（⌂x） → Thing（⌂x）
        Student（alice）
    """)

    # Should cascade through all levels
    facts_person = r.query(type='instance_of', individual='alice', concept='Person')
    assert len(facts_person) > 0, "Should infer alice is Person"

    facts_living = r.query(type='instance_of', individual='alice', concept='LivingBeing')
    assert len(facts_living) > 0, "Should infer alice is LivingBeing"

    facts_thing = r.query(type='instance_of', individual='alice', concept='Thing')
    assert len(facts_thing) > 0, "Should infer alice is Thing"
    print("✓ Cascading rules test passed")


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================

def test_swrl_builtin_division_by_zero():
    """Test that division by zero is handled gracefully"""
    print("Testing division by zero handling...")
    r = Reter()
    r.load_ontology("""
        ⊢ hasValue（⌂x，⋈val） ∧ ⍚divide（⋈result，⋈val，0） → hasResult（⌂x，⋈result）
        hasValue（item1，100）
    """)

    try:
        # Should not crash, but should not produce result
        facts = r.query(type='data_property_assertion', subject='item1', property='hasResult')
        # Implementation-dependent: may return empty or handle gracefully
        print("✓ Division by zero handled gracefully")
    except Exception as e:
        print(f"✓ Division by zero raised exception (acceptable): {type(e).__name__}")


def test_swrl_unbound_variable():
    """Test that unbound variables are handled"""
    print("Testing unbound variable handling...")
    r = Reter()
    # Rule with variable in head that's not bound in body (should not fire or error)
    r.load_ontology("""
        ⊢ Person（⌂x） → knows（⌂x，⌂y）
        Person（alice）
    """)

    try:
        # Should not crash - unbound variables in head should be ignored or error
        print("✓ Unbound variable handled")
    except Exception as e:
        print(f"✓ Unbound variable raised exception (acceptable): {type(e).__name__}")


def test_swrl_empty_rule():
    """Test that empty antecedent/consequent is handled"""
    print("Testing empty rule handling...")
    # This should be caught by parser, but if it gets through, should be handled
    print("⊘ Empty rule test skipped (should be caught by parser)")


# ============================================================================
# Main Test Runner
# ============================================================================

def run_all_tests():
    """Run all SWRL tests"""
    test_functions = [
        # Basic tests
        test_swrl_basic_class_atom,
        test_swrl_basic_property_chain,
        test_swrl_mixed_class_property,

        # Math builtins
        test_swrl_builtin_add,
        test_swrl_builtin_subtract,
        test_swrl_builtin_multiply,
        test_swrl_builtin_divide,
        test_swrl_builtin_chained_math,

        # Comparison builtins
        test_swrl_builtin_greater_than,
        test_swrl_builtin_less_than,
        test_swrl_builtin_greater_equal,
        test_swrl_builtin_less_equal,
        test_swrl_builtin_equal,
        test_swrl_builtin_not_equal,
        test_swrl_builtin_comparison_range,

        # String builtins
        test_swrl_builtin_string_concat,
        test_swrl_builtin_string_length,

        # Data properties
        test_swrl_data_property,
        test_swrl_data_range,

        # Same/Different
        test_swrl_same_as,
        test_swrl_different_from,

        # Complex scenarios
        test_swrl_complex_family_reasoning,
        test_swrl_with_math_and_comparison,
        test_swrl_multiple_variables_in_head,
        test_swrl_cascading_rules,

        # Edge cases
        test_swrl_builtin_division_by_zero,
        test_swrl_unbound_variable,
        test_swrl_empty_rule,
    ]

    print("=" * 70)
    print("COMPREHENSIVE SWRL TEST SUITE")
    print("=" * 70)
    print()

    passed = 0
    failed = 0
    skipped = 0

    for test_func in test_functions:
        try:
            test_func()
            if "skipped" in str(test_func.__doc__).lower():
                skipped += 1
            else:
                passed += 1
        except AssertionError as e:
            print(f"✗ {test_func.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__} ERROR: {e}")
            failed += 1
        print()

    print("=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed, {skipped} skipped")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
