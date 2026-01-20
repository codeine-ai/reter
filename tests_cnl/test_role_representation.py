"""Test how CNL roles are represented in the fact store.

This test verifies the morphological form of roles when stored in the fact store
after CNL parsing.
"""
import pytest
import reter_core.owl_rete_cpp as cpp


def get_facts(cnl_text):
    """Parse CNL and return list of fact dicts."""
    result = cpp.parse_cnl(cnl_text)
    facts = []
    for f in result.facts:
        fact_dict = {'type': f.get('type')}
        # Add all known keys
        for key in ['sub', 'sup', 'individual', 'concept', 'subject',
                    'predicate', 'object', 'c1', 'c2', 'property',
                    'filler', 'cardinality', 'id', 'class', 'i1', 'i2',
                    'modality', 'chain', 'super_property', 'value', 'datatype']:
            val = f.get(key)
            if val:
                fact_dict[key] = val
        facts.append(fact_dict)
    return facts


def print_facts(facts, title="Facts"):
    """Pretty print facts."""
    print(f"\n=== {title} ===")
    for f in facts:
        print(f"  {f}")


class TestRoleRepresentation:
    """Test how CNL roles appear in the fact store."""

    def test_hyphenated_role_instance_assertion(self):
        """Test: 'Alfa inheres-in Beta' - how is 'inheres-in' stored?"""
        cnl_text = "Alfa inheres-in Beta."
        facts = get_facts(cnl_text)

        print_facts(facts, "Role Assertion: 'Alfa inheres-in Beta'")

        # Find the role assertion fact
        role_facts = [f for f in facts if f['type'] == 'role_assertion']
        assert len(role_facts) > 0, f"No role_assertion found. Facts: {facts}"

        # Check what the predicate/property is called
        for rf in role_facts:
            print(f"\n  Role fact details:")
            print(f"    subject: {rf.get('subject')}")
            print(f"    predicate: {rf.get('predicate')}")
            print(f"    property: {rf.get('property')}")
            print(f"    object: {rf.get('object')}")

    def test_verb_role_instance_assertion(self):
        """Test: 'John loves Mary' - how is 'loves' stored?"""
        cnl_text = "John loves Mary."
        facts = get_facts(cnl_text)

        print_facts(facts, "Role Assertion: 'John loves Mary'")

        role_facts = [f for f in facts if f['type'] == 'role_assertion']
        assert len(role_facts) > 0, f"No role_assertion found. Facts: {facts}"

        for rf in role_facts:
            print(f"\n  Role fact details:")
            print(f"    subject: {rf.get('subject')}")
            print(f"    predicate: {rf.get('predicate')}")
            print(f"    property: {rf.get('property')}")
            print(f"    object: {rf.get('object')}")

    def test_passive_role_instance_assertion(self):
        """Test: 'Mary is loved by John' - how is 'loved' stored?"""
        cnl_text = "Mary is loved by John."
        facts = get_facts(cnl_text)

        print_facts(facts, "Role Assertion: 'Mary is loved by John'")

        role_facts = [f for f in facts if f['type'] == 'role_assertion']
        assert len(role_facts) > 0, f"No role_assertion found. Facts: {facts}"

        for rf in role_facts:
            print(f"\n  Role fact details:")
            print(f"    subject: {rf.get('subject')}")
            print(f"    predicate: {rf.get('predicate')}")
            print(f"    property: {rf.get('property')}")
            print(f"    object: {rf.get('object')}")

    def test_role_in_subsumption(self):
        """Test: 'Every person loves a thing' - how is 'loves' stored in restriction?"""
        cnl_text = "Every person loves a thing."
        facts = get_facts(cnl_text)

        print_facts(facts, "Subsumption: 'Every person loves a thing'")

        # This creates existential restriction facts
        for f in facts:
            if 'property' in f or 'predicate' in f:
                print(f"\n  Property/predicate fact: {f}")

    def test_compare_active_passive(self):
        """Test that active and passive forms produce the same role."""
        # Active voice
        facts1 = get_facts("John owns Pussy.")
        print_facts(facts1, "Active: 'John owns Pussy'")

        # Passive voice
        facts2 = get_facts("Pussy is owned by John.")
        print_facts(facts2, "Passive: 'Pussy is owned by John'")

        # Extract role names
        role1 = [f for f in facts1 if f['type'] == 'role_assertion']
        role2 = [f for f in facts2 if f['type'] == 'role_assertion']

        print(f"\nActive role facts: {role1}")
        print(f"Passive role facts: {role2}")

        # They should have the same property name (lemmatized)
        if role1 and role2:
            prop1 = role1[0].get('predicate') or role1[0].get('property')
            prop2 = role2[0].get('predicate') or role2[0].get('property')
            print(f"\nActive property: {prop1}")
            print(f"Passive property: {prop2}")
            # Note: We're exploring, not asserting equality yet

    def test_query_by_role_name(self):
        """Test multiple role assertions."""
        cnl_text = """
        John loves Mary.
        Peter loves Susan.
        Alice hates Bob.
        """
        facts = get_facts(cnl_text)

        print_facts(facts, "Multiple Role Assertions")

        role_facts = [f for f in facts if f['type'] == 'role_assertion']
        print(f"\nFound {len(role_facts)} role assertions")

        # Group by predicate/property
        by_role = {}
        for rf in role_facts:
            role_name = rf.get('predicate') or rf.get('property') or 'unknown'
            if role_name not in by_role:
                by_role[role_name] = []
            by_role[role_name].append(rf)

        print(f"\nGrouped by role name:")
        for role_name, role_list in by_role.items():
            print(f"  {role_name}: {len(role_list)} assertions")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
