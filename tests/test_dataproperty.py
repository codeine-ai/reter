"""
Test data property detection and reasoning
Tests for detect-dataproperty and scm-dp rules
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reter import Reter

def test_dataproperty_detection():
    """Test: detect-dataproperty - Detect data properties from data_property_assertion facts"""
    print("=" * 60)
    print("TEST: detect-dataproperty (Data Property Detection)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    age（John， 30）
    name（Alice， 'Alice Smith'）
    height（Bob， 5.9）
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check for detected data properties
    data_props = reasoner.query(type='data_property_declaration')
    print(f"\nData property declarations detected: {len(data_props)}")

    expected_props = {'age', 'name', 'height'}
    found_props = set()

    for prop in data_props:
        prop_name = prop.get('property')
        inferred_by = prop.get('inferred_by', '')
        print(f"  {prop_name} (by {inferred_by})")
        found_props.add(prop_name)

    success = expected_props.issubset(found_props)
    print(f"\n✓ Expected: {expected_props}")
    print(f"✓ Found: {found_props}")
    print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_scm_dp_reflexivity():
    """Test: scm-dp - Data property reflexivity (P ⊏ P and P ≣ P)"""
    print("\n" + "=" * 60)
    print("TEST: scm-dp (Data Property Reflexivity)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    age（John， 30）
    name（Alice， 'Alice Smith'）
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check reflexive subsumptions
    print("\nReflexive property subsumptions:")
    for prop in ['age', 'name']:
        subs = reasoner.query(type='property_subsumption', sub=prop, sup=prop)
        scm_dp_found = any(s.get('inferred_by') == 'scm-dp' for s in subs)
        print(f"  {prop} ⊏ {prop}: {len(subs) > 0} (scm-dp: {scm_dp_found})")

    # Check reflexive equivalences
    print("\nReflexive property equivalences:")
    for prop in ['age', 'name']:
        equivs = reasoner.query(type='property_equivalence', property1=prop, property2=prop)
        scm_dp_found = any(e.get('inferred_by') == 'scm-dp' for e in equivs)
        print(f"  {prop} ≣ {prop}: {len(equivs) > 0} (scm-dp: {scm_dp_found})")

    # Verify all properties have reflexive facts
    age_sub = reasoner.query(type='property_subsumption', sub='age', sup='age')
    name_sub = reasoner.query(type='property_subsumption', sub='name', sup='name')
    age_equiv = reasoner.query(type='property_equivalence', property1='age', property2='age')
    name_equiv = reasoner.query(type='property_equivalence', property1='name', property2='name')

    success = (len(age_sub) > 0 and len(name_sub) > 0 and
               len(age_equiv) > 0 and len(name_equiv) > 0)

    print(f"\n✓ All data properties have reflexive subsumptions: {len(age_sub) > 0 and len(name_sub) > 0}")
    print(f"✓ All data properties have reflexive equivalences: {len(age_equiv) > 0 and len(name_equiv) > 0}")
    print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_mixed_properties():
    """Test: Mixed object and data properties are correctly distinguished"""
    print("\n" + "=" * 60)
    print("TEST: Mixed Object and Data Properties")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    hasParent（John， Mary）
    hasFriend（Alice， Bob）
    age（John， 30）
    name（Alice， 'Alice Smith'）
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check object properties
    obj_props = reasoner.query(type='object_property_declaration')
    print(f"\nObject property declarations: {len(obj_props)}")
    obj_prop_names = set()
    for prop in obj_props:
        prop_name = prop.get('property')
        print(f"  {prop_name}")
        obj_prop_names.add(prop_name)

    # Check data properties
    data_props = reasoner.query(type='data_property_declaration')
    print(f"\nData property declarations: {len(data_props)}")
    data_prop_names = set()
    for prop in data_props:
        prop_name = prop.get('property')
        inferred_by = prop.get('inferred_by', '')
        print(f"  {prop_name} (by {inferred_by})")
        data_prop_names.add(prop_name)

    # Verify correct classification
    expected_obj = {'hasParent', 'hasFriend'}
    expected_data = {'age', 'name'}

    obj_correct = expected_obj.issubset(obj_prop_names)
    data_correct = expected_data.issubset(data_prop_names)
    no_overlap = obj_prop_names.isdisjoint(data_prop_names)

    success = obj_correct and data_correct and no_overlap

    print(f"\n✓ Object properties correct: {obj_correct}")
    print(f"✓ Data properties correct: {data_correct}")
    print(f"✓ No overlap between types: {no_overlap}")
    print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_data_property_with_subsumption():
    """Test: Data properties work with property subsumption reasoning"""
    print("\n" + "=" * 60)
    print("TEST: Data Property with Subsumption")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    age（John， 30）
    weight（Alice， 150）
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check that both data properties are detected
    data_props = reasoner.query(type='data_property_declaration')
    data_prop_names = {p.get('property') for p in data_props}

    print(f"\nData properties detected: {data_prop_names}")

    # Check that scm-dp creates reflexive facts for both
    age_sub = reasoner.query(type='property_subsumption', sub='age', sup='age')
    weight_sub = reasoner.query(type='property_subsumption', sub='weight', sup='weight')

    scm_dp_age = any(s.get('inferred_by') == 'scm-dp' for s in age_sub)
    scm_dp_weight = any(s.get('inferred_by') == 'scm-dp' for s in weight_sub)

    print(f"\nage ⊏ age (by scm-dp): {scm_dp_age}")
    print(f"weight ⊏ weight (by scm-dp): {scm_dp_weight}")

    success = (data_prop_names >= {'age', 'weight'} and
               scm_dp_age and scm_dp_weight)

    print(f"\n✓ Both data properties detected: {data_prop_names >= {'age', 'weight'}}")
    print(f"✓ scm-dp applied to both: {scm_dp_age and scm_dp_weight}")
    print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    return success

if __name__ == "__main__":
    results = {
        "Data Property Detection": test_dataproperty_detection(),
        "scm-dp Reflexivity": test_scm_dp_reflexivity(),
        "Mixed Properties": test_mixed_properties(),
        "Data Property Subsumption": test_data_property_with_subsumption()
    }

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")

    total = len(results)
    passed = sum(1 for p in results.values() if p)
    print(f"\nTotal: {passed}/{total} tests passed")
