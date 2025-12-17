"""
Test property domain and range detection and propagation
Tests for detect-domain, detect-range, scm-dom1, scm-dom2, scm-rng1, scm-rng2
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from reter import Reter

def test_domain_detection():
    """Test: detect-domain - Extract domain from ∃R․⊤ ⊑ C pattern
    Pattern: ∃hasParent․⊤ ⊑ Person means hasParent has domain Person
    """
    print("=" * 60)
    print("TEST: detect-domain (Domain Extraction)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    ∃hasParent․owl:Thing ⊑ᑦ Person
    ∃works․owl:Thing ⊑ᑦ Employee
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check for detected domains
    domains = reasoner.query(type='property_domain')
    print(f"\nProperty domains detected: {len(domains)}")

    expected_domains = {
        ('hasParent', 'Person'),
        ('works', 'Employee')
    }
    found_domains = set()

    for domain in domains:
        prop = domain.get('property')
        dom = domain.get('domain')
        inferred_by = domain.get('inferred_by', '')
        print(f"  {prop} has domain {dom} (by {inferred_by})")
        found_domains.add((prop, dom))

    success = expected_domains.issubset(found_domains)
    print(f"\n✓ Expected: {expected_domains}")
    print(f"✓ Found: {found_domains}")
    print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_range_detection():
    """Test: detect-range - Extract range from ⊤ ⊑ ∀R․C pattern
    Pattern: ⊤ ⊑ ∀hasParent․Person means hasParent has range Person
    """
    print("\n" + "=" * 60)
    print("TEST: detect-range (Range Extraction)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    owl:Thing ⊑ᑦ ∀hasParent․Person
    owl:Thing ⊑ᑦ ∀worksFor․Company
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check for detected ranges
    ranges = reasoner.query(type='property_range')
    print(f"\nProperty ranges detected: {len(ranges)}")

    expected_ranges = {
        ('hasParent', 'Person'),
        ('worksFor', 'Company')
    }
    found_ranges = set()

    for range_fact in ranges:
        prop = range_fact.get('property')
        rng = range_fact.get('range')
        inferred_by = range_fact.get('inferred_by', '')
        print(f"  {prop} has range {rng} (by {inferred_by})")
        found_ranges.add((prop, rng))

    success = expected_ranges.issubset(found_ranges)
    print(f"\n✓ Expected: {expected_ranges}")
    print(f"✓ Found: {found_ranges}")
    print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_scm_dom1():
    """Test: scm-dom1 - Domain subsumption
    If P has domain C1 and C1 ⊑ C2, then P has domain C2
    """
    print("\n" + "=" * 60)
    print("TEST: scm-dom1 (Domain Subsumption)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Student ⊑ᑦ Person
    Person ⊑ᑦ Animal
    ∃hasParent․owl:Thing ⊑ᑦ Student
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check for propagated domains
    domains = reasoner.query(type='property_domain', property='hasParent')
    print(f"\nDomains of hasParent: {len(domains)}")

    found_domains = set()
    scm_dom1_found = False

    for domain in domains:
        dom = domain.get('domain')
        inferred_by = domain.get('inferred_by', '')
        print(f"  hasParent has domain {dom} (by {inferred_by})")
        found_domains.add(dom)
        if inferred_by == 'scm-dom1':
            scm_dom1_found = True

    # Should have Student (from detect-domain), Person and Animal (from scm-dom1)
    expected = {'Student', 'Person', 'Animal'}
    success = expected.issubset(found_domains) and scm_dom1_found

    print(f"\n✓ Expected domains: {expected}")
    print(f"✓ Found domains: {found_domains}")
    print(f"✓ scm-dom1 fired: {scm_dom1_found}")
    print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_scm_dom2():
    """Test: scm-dom2 - Domain propagation via property subsumption
    If P2 has domain C and P1 ⊏ P2, then P1 has domain C
    """
    print("\n" + "=" * 60)
    print("TEST: scm-dom2 (Domain Propagation)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    hasMother ⊑ᴿ hasParent
    hasParent ⊑ᴿ hasAncestor
    ∃hasAncestor․owl:Thing ⊑ᑦ Person
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check for propagated domains
    mother_domains = reasoner.query(type='property_domain', property='hasMother')
    parent_domains = reasoner.query(type='property_domain', property='hasParent')

    print(f"\nDomains of hasMother: {len(mother_domains)}")
    for domain in mother_domains:
        dom = domain.get('domain')
        inferred_by = domain.get('inferred_by', '')
        print(f"  hasMother has domain {dom} (by {inferred_by})")

    print(f"\nDomains of hasParent: {len(parent_domains)}")
    for domain in parent_domains:
        dom = domain.get('domain')
        inferred_by = domain.get('inferred_by', '')
        print(f"  hasParent has domain {dom} (by {inferred_by})")

    # Both hasMother and hasParent should have domain Person (propagated from hasAncestor)
    scm_dom2_found = any(d.get('inferred_by') == 'scm-dom2' for d in mother_domains)
    mother_has_person = any(d.get('domain') == 'Person' for d in mother_domains)
    parent_has_person = any(d.get('domain') == 'Person' for d in parent_domains)

    success = scm_dom2_found and mother_has_person and parent_has_person

    print(f"\n✓ scm-dom2 fired: {scm_dom2_found}")
    print(f"✓ hasMother has domain Person: {mother_has_person}")
    print(f"✓ hasParent has domain Person: {parent_has_person}")
    print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_scm_rng1():
    """Test: scm-rng1 - Range subsumption
    If P has range C1 and C1 ⊑ C2, then P has range C2
    """
    print("\n" + "=" * 60)
    print("TEST: scm-rng1 (Range Subsumption)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Student ⊑ᑦ Person
    Person ⊑ᑦ Animal
    owl:Thing ⊑ᑦ ∀hasChild․Student
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check for propagated ranges
    ranges = reasoner.query(type='property_range', property='hasChild')
    print(f"\nRanges of hasChild: {len(ranges)}")

    found_ranges = set()
    scm_rng1_found = False

    for range_fact in ranges:
        rng = range_fact.get('range')
        inferred_by = range_fact.get('inferred_by', '')
        print(f"  hasChild has range {rng} (by {inferred_by})")
        found_ranges.add(rng)
        if inferred_by == 'scm-rng1':
            scm_rng1_found = True

    # Should have Student (from detect-range), Person and Animal (from scm-rng1)
    expected = {'Student', 'Person', 'Animal'}
    success = expected.issubset(found_ranges) and scm_rng1_found

    print(f"\n✓ Expected ranges: {expected}")
    print(f"✓ Found ranges: {found_ranges}")
    print(f"✓ scm-rng1 fired: {scm_rng1_found}")
    print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_scm_rng2():
    """Test: scm-rng2 - Range propagation via property subsumption
    If P2 has range C and P1 ⊏ P2, then P1 has range C
    """
    print("\n" + "=" * 60)
    print("TEST: scm-rng2 (Range Propagation)")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    hasDaughter ⊑ᴿ hasChild
    hasChild ⊑ᴿ hasDescendant
    owl:Thing ⊑ᑦ ∀hasDescendant․Person
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check for propagated ranges
    daughter_ranges = reasoner.query(type='property_range', property='hasDaughter')
    child_ranges = reasoner.query(type='property_range', property='hasChild')

    print(f"\nRanges of hasDaughter: {len(daughter_ranges)}")
    for range_fact in daughter_ranges:
        rng = range_fact.get('range')
        inferred_by = range_fact.get('inferred_by', '')
        print(f"  hasDaughter has range {rng} (by {inferred_by})")

    print(f"\nRanges of hasChild: {len(child_ranges)}")
    for range_fact in child_ranges:
        rng = range_fact.get('range')
        inferred_by = range_fact.get('inferred_by', '')
        print(f"  hasChild has range {rng} (by {inferred_by})")

    # Both hasDaughter and hasChild should have range Person (propagated from hasDescendant)
    scm_rng2_found = any(r.get('inferred_by') == 'scm-rng2' for r in daughter_ranges)
    daughter_has_person = any(r.get('range') == 'Person' for r in daughter_ranges)
    child_has_person = any(r.get('range') == 'Person' for r in child_ranges)

    success = scm_rng2_found and daughter_has_person and child_has_person

    print(f"\n✓ scm-rng2 fired: {scm_rng2_found}")
    print(f"✓ hasDaughter has range Person: {daughter_has_person}")
    print(f"✓ hasChild has range Person: {child_has_person}")
    print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    return success

def test_combined_domain_range():
    """Test: Combined domain and range rules working together"""
    print("\n" + "=" * 60)
    print("TEST: Combined Domain and Range Rules")
    print("=" * 60)

    reasoner = Reter()
    ontology = """
    Student ⊑ᑦ Person
    Teacher ⊑ᑦ Person
    teaches ⊑ᴿ interactsWith

    ∃teaches․owl:Thing ⊑ᑦ Teacher
    owl:Thing ⊑ᑦ ∀teaches․Student
    """
    reasoner.load_ontology(ontology)
    # Reasoning is automatic/incremental - no need to call reason()

    # Check domain and range for teaches
    domains = reasoner.query(type='property_domain', property='teaches')
    ranges = reasoner.query(type='property_range', property='teaches')

    print(f"\nDomains of teaches: {len(domains)}")
    for domain in domains:
        dom = domain.get('domain')
        inferred_by = domain.get('inferred_by', '')
        print(f"  teaches has domain {dom} (by {inferred_by})")

    print(f"\nRanges of teaches: {len(ranges)}")
    for range_fact in ranges:
        rng = range_fact.get('range')
        inferred_by = range_fact.get('inferred_by', '')
        print(f"  teaches has range {rng} (by {inferred_by})")

    # teaches should have domain Teacher, Person and range Student, Person
    domain_concepts = {d.get('domain') for d in domains}
    range_concepts = {r.get('range') for r in ranges}

    has_teacher_domain = 'Teacher' in domain_concepts
    has_person_domain = 'Person' in domain_concepts
    has_student_range = 'Student' in range_concepts
    has_person_range = 'Person' in range_concepts

    success = has_teacher_domain and has_person_domain and has_student_range and has_person_range

    print(f"\n✓ teaches has domain Teacher: {has_teacher_domain}")
    print(f"✓ teaches has domain Person: {has_person_domain}")
    print(f"✓ teaches has range Student: {has_student_range}")
    print(f"✓ teaches has range Person: {has_person_range}")
    print(f"\n{'✓ PASS' if success else '✗ FAIL'}")
    return success

if __name__ == "__main__":
    results = {
        "Domain Detection": test_domain_detection(),
        "Range Detection": test_range_detection(),
        "scm-dom1": test_scm_dom1(),
        "scm-dom2": test_scm_dom2(),
        "scm-rng1": test_scm_rng1(),
        "scm-rng2": test_scm_rng2(),
        "Combined": test_combined_domain_range()
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
