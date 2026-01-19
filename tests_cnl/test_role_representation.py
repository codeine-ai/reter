"""Test how CNL roles are represented in REQL queries.

This test verifies the morphological form of roles when stored in the fact store
and queried via REQL.
"""
import pytest
import sys
import os

# Windows DLL fix
if sys.platform == 'win32':
    try:
        import pyarrow as pa
        os.add_dll_directory(pa.get_library_dirs()[0])
    except Exception:
        pass

from reter.reasoner import Reter


class TestRoleRepresentation:
    """Test how CNL roles appear in REQL queries."""

    def test_hyphenated_role_instance_assertion(self):
        """Test: 'Alfa inheres-in Beta' - how is 'inheres-in' stored?"""
        r = Reter()

        # Parse CNL with hyphenated role
        cnl_text = "Alfa inheres-in Beta."
        r.network.parse_cnl(cnl_text)

        # Query all role assertions
        result = r.reql("SELECT ?s ?role ?o WHERE { ?s ?role ?o }")

        print("\n=== Role Assertion: 'Alfa inheres-in Beta' ===")
        for row in result:
            print(f"  Subject: {row['?s']}")
            print(f"  Role: {row['?role']}")
            print(f"  Object: {row['?o']}")
            print()

        # Check the role value
        roles = [row['?role'] for row in result]
        assert len(roles) > 0, "No role assertions found"

        # What form is it stored as?
        print(f"Roles found: {roles}")

    def test_verb_role_instance_assertion(self):
        """Test: 'John loves Mary' - how is 'loves' stored?"""
        r = Reter()

        cnl_text = "John loves Mary."
        r.network.parse_cnl(cnl_text)

        result = r.reql("SELECT ?s ?role ?o WHERE { ?s ?role ?o }")

        print("\n=== Role Assertion: 'John loves Mary' ===")
        for row in result:
            print(f"  Subject: {row['?s']}")
            print(f"  Role: {row['?role']}")
            print(f"  Object: {row['?o']}")
            print()

        roles = [row['?role'] for row in result]
        print(f"Roles found: {roles}")

    def test_passive_role_instance_assertion(self):
        """Test: 'Mary is loved by John' - how is 'loved' stored?"""
        r = Reter()

        cnl_text = "Mary is loved by John."
        r.network.parse_cnl(cnl_text)

        result = r.reql("SELECT ?s ?role ?o WHERE { ?s ?role ?o }")

        print("\n=== Role Assertion: 'Mary is loved by John' ===")
        for row in result:
            print(f"  Subject: {row['?s']}")
            print(f"  Role: {row['?role']}")
            print(f"  Object: {row['?o']}")
            print()

        roles = [row['?role'] for row in result]
        print(f"Roles found: {roles}")

    def test_role_in_subsumption(self):
        """Test: 'Every person loves a thing' - how is 'loves' stored in restriction?"""
        r = Reter()

        cnl_text = "Every person loves a thing."
        r.network.parse_cnl(cnl_text)

        # Query for restrictions or role-related facts
        result = r.reql("SELECT ?s ?p ?o WHERE { ?s ?p ?o }")

        print("\n=== Subsumption: 'Every person loves a thing' ===")
        for row in result:
            print(f"  {row['?s']} -- {row['?p']} --> {row['?o']}")

        # Look specifically for role-related predicates
        role_facts = [row for row in result if 'role' in str(row['?p']).lower() or 'loves' in str(row).lower()]
        print(f"\nRole-related facts: {role_facts}")

    def test_compare_active_passive(self):
        """Test that active and passive forms produce the same role."""
        r1 = Reter()
        r2 = Reter()

        # Active voice
        r1.network.parse_cnl("John owns Pussy.")
        result1 = r1.reql("SELECT ?s ?role ?o WHERE { ?s ?role ?o }")

        # Passive voice
        r2.network.parse_cnl("Pussy is owned by John.")
        result2 = r2.reql("SELECT ?s ?role ?o WHERE { ?s ?role ?o }")

        print("\n=== Active vs Passive Comparison ===")
        print("Active 'John owns Pussy':")
        for row in result1:
            print(f"  {row['?s']} -- {row['?role']} --> {row['?o']}")

        print("\nPassive 'Pussy is owned by John':")
        for row in result2:
            print(f"  {row['?s']} -- {row['?role']} --> {row['?o']}")

        # Extract roles
        roles1 = set(row['?role'] for row in result1)
        roles2 = set(row['?role'] for row in result2)

        print(f"\nActive roles: {roles1}")
        print(f"Passive roles: {roles2}")

    def test_query_by_role_name(self):
        """Test querying facts by specific role name."""
        r = Reter()

        cnl_text = """
        John loves Mary.
        Peter loves Susan.
        Alice hates Bob.
        """
        r.network.parse_cnl(cnl_text)

        # First, see all roles
        all_facts = r.reql("SELECT ?s ?role ?o WHERE { ?s ?role ?o }")
        print("\n=== All Role Assertions ===")
        for row in all_facts:
            print(f"  {row['?s']} -- {row['?role']} --> {row['?o']}")

        # Try to query by role name - what form works?
        for role_name in ['loves', 'love', 'hates', 'hate']:
            result = r.reql(f'SELECT ?s ?o WHERE {{ ?s {role_name} ?o }}')
            if result:
                print(f"\nQuery with '{role_name}' succeeded: {len(result)} results")
                for row in result:
                    print(f"  {row['?s']} --> {row['?o']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
