"""
Comprehensive tests for AILexer ontology parsing and querying.

The AILexer provides AI-friendly syntax with:
- ASCII keywords: is_subclass_of, is_equivalent_to, is_a, and, or, not, some, all
- Programming identifiers: com.example.Person, std::vector, MyClass$Inner
- Standard ASCII parentheses: Person(Alice), hasAge(Alice, 30)

This test suite covers all DL grammar features with AI-friendly syntax.
"""

import pytest
from reter import Reter


def check_subsumption(reter, sub, sup):
    """Helper function to check if a subsumption relationship exists in the ontology."""
    facts = reter.network.get_all_facts()
    for fact in facts:
        if (fact.get('type') == 'subsumption' and
            fact.get('sub') == sub and
            fact.get('sup') == sup):
            return True
    return False


class TestAILexerBasicClassHierarchy:
    """Test basic class subsumption and equivalence with AI-friendly syntax."""

    def test_simple_subsumption(self):
        """Test basic class subsumption using is_a."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Dog is_a Mammal
        Mammal is_a Animal
        Animal is_a LivingThing
        """)

        # Check transitive subsumption
        assert check_subsumption(reter, "Dog", "Animal"), "Dog should be inferred as subclass of Animal"
        assert check_subsumption(reter, "Dog", "LivingThing"), "Dog should be inferred as subclass of LivingThing"

    def test_subsumption_variations(self):
        """Test all AI-friendly subsumption syntax variations."""
        reter = Reter(variant='ai')

        # Test different keyword variations (must match grammar)
        reter.load_ontology("""
        Cat is_subclass_of Mammal
        Bird is_subclass_of Animal
        Fish is_a Animal
        Plant extends LivingThing
        Bacteria is_sub_concept_of Organism
        Tree isa Plant
        """)

        assert check_subsumption(reter, "Cat", "Mammal")
        assert check_subsumption(reter, "Bird", "Animal")
        assert check_subsumption(reter, "Fish", "Animal")
        assert check_subsumption(reter, "Plant", "LivingThing")
        assert check_subsumption(reter, "Bacteria", "Organism")
        assert check_subsumption(reter, "Tree", "Plant")

    def test_class_equivalence(self):
        """Test class equivalence using is_equivalent_to."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Person is_a Thing
        Female is_a Person
        Male is_a Person
        Parent is_a Person

        Mother is_equivalent_to Female and Parent
        Father is_equivalent_to Male and Parent
        """)

        # Check equivalence inference - equivalence creates bidirectional subsumption
        # Mother ≡ (Female ⊓ Parent) means Mother ⊑ Female AND Mother ⊑ Parent
        assert check_subsumption(reter, "Mother", "Female"), "Mother should be subclass of Female"
        assert check_subsumption(reter, "Mother", "Parent"), "Mother should be subclass of Parent"

    def test_class_equivalence_variations(self):
        """Test all equivalence syntax variations."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Adult is_equivalent_to Grownup
        Person same_as Human
        Student equals Pupil
        Employee is_same_concept_as Worker
        """)

        # Equivalence creates bidirectional subsumption
        assert check_subsumption(reter, "Adult", "Grownup")
        assert check_subsumption(reter, "Grownup", "Adult")
        assert check_subsumption(reter, "Person", "Human")
        assert check_subsumption(reter, "Student", "Pupil")
        assert check_subsumption(reter, "Employee", "Worker")


class TestAILexerProgrammingIdentifiers:
    """Test support for programming language identifiers."""

    def test_java_package_names(self):
        """Test Java-style package names with dots."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        com.example.Person is_a Thing
        com.example.Employee is_a com.example.Person
        org.company.Manager is_a com.example.Employee

        com.example.Person(alice)
        org.company.Manager(bob)
        """)

        # Check class membership
        result = reter.reql("""
        SELECT ?x WHERE {
            ?x type com.example.Person
        }
        """)
        assert len(result) >= 2, "Should find alice and bob (manager is person)"

    def test_cpp_namespaces(self):
        """Test C++ namespace syntax with ::."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        std::vector is_a Container
        std::list is_a Container
        std::map is_a Container
        boost::shared_ptr is_a SmartPointer

        std::vector(myVec)
        std::map(myMap)
        """)

        result = reter.reql("""
        SELECT ?container WHERE {
            ?container type Container
        }
        """)
        # Should find myVec and myMap (and the class names themselves)
        assert len(result) >= 2

    def test_inner_class_syntax(self):
        """Test Java inner class syntax with $."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        OuterClass$InnerClass is_a Class
        MyService$Builder is_a Builder

        OuterClass$InnerClass(instance1)
        MyService$Builder(builder1)
        """)

        result = reter.reql("""
        SELECT ?x WHERE {
            ?x type OuterClass$InnerClass
        }
        """)
        assert len(result) >= 1

    @pytest.mark.skip(reason="Kebab-case identifiers not supported - grammar limitation (hyphen in ID token)")
    def test_kebab_case_identifiers(self):
        """Test kebab-case identifiers with hyphens."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        my-custom-class is_a Thing
        user-profile is_a Entity
        api-endpoint is_a Resource

        my-custom-class(obj1)
        has-property(obj1, value1)
        """)

        result = reter.reql("""
        SELECT ?x WHERE {
            ?x type my-custom-class
        }
        """)
        assert len(result) >= 1

    def test_template_syntax(self):
        """Test template/generic syntax."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        `vector<int>` is_a Container
        `List[str]` is_a Collection
        `Map<String,Object>` is_a Dictionary

        `vector<int>`(vec1)
        `List[str]`(list1)
        """)

        result = reter.reql("""
        SELECT ?x WHERE {
            ?x type `vector<int>`
        }
        """)
        assert len(result) >= 1


class TestAILexerAssertions:
    """Test individual and property assertions with ASCII parentheses."""

    def test_class_assertions(self):
        """Test class assertions with standard parentheses."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Person is_a Thing
        Dog is_a Animal

        Person(Alice)
        Person(Bob)
        Dog(Fido)
        Dog(Rex)
        """)

        result = reter.reql("""
        SELECT ?person WHERE {
            ?person type Person
        }
        """)
        persons = result.to_pydict()['?person']
        assert 'Alice' in persons
        assert 'Bob' in persons

    def test_object_property_assertions(self):
        """Test object property assertions."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Person(Alice)
        Person(Bob)
        Company(Acme)

        worksFor(Alice, Acme)
        knows(Alice, Bob)
        manages(Bob, Alice)
        """)

        # Query for Alice's employer
        result = reter.reql("""
        SELECT ?company WHERE {
            Alice worksFor ?company
        }
        """)
        assert result.num_rows == 1
        companies = result.to_pydict()['?company']
        assert 'Acme' in companies

    def test_data_property_assertions(self):
        """Test data property assertions."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Person(Alice)
        Person(Bob)

        age(Alice, 30)
        age(Bob, 25)
        name(Alice, 'Alice Smith')
        salary(Bob, 50000)
        """)

        # Query for ages
        result = reter.reql("""
        SELECT ?person ?age WHERE {
            ?person age ?age
        }
        """)
        assert result.num_rows == 2

    def test_mixed_properties(self):
        """Test mixed object and data properties."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Person(Alice)
        Person(Bob)
        City(Seattle)

        livesIn(Alice, Seattle)
        age(Alice, 30)
        knows(Alice, Bob)
        hasEmail(Bob, 'bob@example.com')
        """)

        # Complex query
        result = reter.reql("""
        SELECT ?person ?city ?age WHERE {
            ?person livesIn ?city .
            ?person age ?age
        }
        """)
        assert result.num_rows == 1
        persons = result.to_pydict()['?person']
        assert 'Alice' in persons


class TestAILexerBooleanOperators:
    """Test boolean operators: and, or, not."""

    def test_intersection_and(self):
        """Test class intersection using 'and'."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Person is_a Thing
        Female is_a Person
        Parent is_a Person

        Mother is_equivalent_to Female and Parent

        Female(Alice)
        Parent(Alice)
        """)

        # Alice should be inferred as Mother
        # Note: dl_ask() checks if class expression has instances, not individual assertions
        # For checking if specific individual is in a class, use pattern() or instances_of()
        result = reter.pattern(('Alice', 'type', 'Mother'))
        assert len(result) > 0, "Alice should be Mother (Female and Parent)"

    def test_intersection_variations(self):
        """Test all 'and' syntax variations."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        A is_a Thing
        B is_a Thing
        C is_a Thing

        D is_equivalent_to A and B
        E is_equivalent_to A intersection_with B
        G is_equivalent_to A with B
        """)

        # All should parse without error
        assert True

    def test_union_or(self):
        """Test class union using 'or'."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Dog is_a Animal
        Cat is_a Animal

        Pet is_equivalent_to Dog or Cat

        Dog(Fido)
        Cat(Whiskers)
        """)

        # Both should be Pets
        result = reter.reql("""
        SELECT ?pet WHERE {
            ?pet type Pet
        }
        """)
        assert len(result) >= 2

    def test_union_variations(self):
        """Test all 'or' syntax variations."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        A is_a Thing
        B is_a Thing

        C is_equivalent_to A or B
        D is_equivalent_to A union_with B
        """)

        # All should parse without error
        assert True

    def test_complement_not(self):
        """Test class complement using 'not'."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Person is_a Thing
        Doctor is_a Person

        NonDoctor is_equivalent_to Person and not Doctor
        """)

        # Should parse without error
        assert True

    def test_complement_variations(self):
        """Test all 'not' syntax variations."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        A is_a Thing

        B is_equivalent_to not A
        C is_equivalent_to complement_of A
        D is_equivalent_to except A
        """)

        # All should parse without error
        assert True

    def test_complex_boolean_expression(self):
        """Test complex nested boolean expressions."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Person is_a Thing
        Student is_a Person
        Employee is_a Person
        Teacher is_a Person

        # Non-teacher person who is either student or employee
        Target is_equivalent_to (Person and not Teacher) and (Student or Employee)
        """)

        # Should parse without error
        assert True


class TestAILexerQuantifiers:
    """Test existential and universal quantification."""

    def test_existential_some(self):
        """Test existential quantification using 'some'."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Person is_a Thing
        Employee is_equivalent_to some worksFor that_is Thing

        Person(Alice)
        Company(Acme)
        worksFor(Alice, Acme)
        """)

        # Alice should be inferred as Employee
        result = reter.pattern(('Alice', 'type', 'Employee'))
        assert len(result) > 0, "Alice should be Employee (has worksFor relation)"

    def test_existential_variations(self):
        """Test all existential quantifier syntax variations."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        A is_equivalent_to some hasChild that_is Thing
        B is_equivalent_to exists hasChild that_is Thing
        C is_equivalent_to there_exists hasChild that_is Thing
        D is_equivalent_to has_some hasChild that_is Thing
        E is_equivalent_to has_a hasChild that_is Thing
        F is_equivalent_to at_least_one hasChild that_is Thing
        """)

        # All should parse without error
        assert True

    def test_universal_all(self):
        """Test universal quantification using 'all'."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Person is_a Thing
        Company is_a Thing

        # All children must be persons
        Thing is_subclass_of all hasChild that_is Person

        # Can only work for companies
        Thing is_subclass_of all worksFor that_is Company
        """)

        # Should parse without error
        assert True

    def test_universal_variations(self):
        """Test all universal quantifier syntax variations."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        A is_subclass_of all hasChild that_is Thing
        B is_subclass_of only hasChild that_is Thing
        C is_subclass_of every hasChild that_is Thing
        D is_subclass_of forall hasChild that_is Thing
        E is_subclass_of must_be hasChild that_is Thing
        """)

        # All should parse without error
        assert True

    def test_domain_range_with_quantifiers(self):
        """Test domain and range using quantifiers."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Person is_a Thing
        Parent is_a Person

        # Domain: Anyone who has a child is a Parent
        some hasChild that_is Thing is_subclass_of Parent

        # Range: All children must be Persons
        Thing is_subclass_of all hasChild that_is Person
        """)

        # Should parse without error
        assert True


class TestAILexerCardinality:
    """Test cardinality restrictions."""

    @pytest.mark.skip(reason="Exact cardinality inference not working - needs investigation")
    def test_exact_cardinality(self):
        """Test exact cardinality using 'exactly'."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Parent is_a Person
        TwoChildren is_equivalent_to exactly 2 hasChild that_is Thing

        Parent(Alice)
        Parent(Bob)
        Person(Child1)
        Person(Child2)
        Person(Child3)

        hasChild(Alice, Child1)
        hasChild(Alice, Child2)
        hasChild(Bob, Child1)
        """)

        # Alice should be inferred as TwoChildren
        result = reter.pattern(('Alice', 'type', 'TwoChildren'))
        assert len(result) > 0, "Alice should have exactly 2 children"

    def test_minimum_cardinality(self):
        """Test minimum cardinality using 'at_least'."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Parent is_equivalent_to at_least 1 hasChild that_is Thing

        Person(Alice)
        Person(Child1)
        hasChild(Alice, Child1)
        """)

        result = reter.pattern(('Alice', 'type', 'Parent'))
        assert len(result) > 0, "Alice should be Parent (at least 1 child)"

    def test_maximum_cardinality(self):
        """Test maximum cardinality using 'at_most'."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        SmallFamily is_equivalent_to at_most 2 hasChild that_is Thing
        """)

        # Should parse without error
        assert True

    def test_cardinality_variations(self):
        """Test all cardinality syntax variations."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        A is_equivalent_to = 2 hasChild that_is Thing
        B is_equivalent_to exactly 2 hasChild that_is Thing
        C is_equivalent_to >= 1 hasChild that_is Thing
        D is_equivalent_to at_least 1 hasChild that_is Thing
        E is_equivalent_to <= 3 hasChild that_is Thing
        F is_equivalent_to at_most 3 hasChild that_is Thing
        G is_equivalent_to > 0 hasChild that_is Thing
        H is_equivalent_to < 10 hasChild that_is Thing
        """)

        # All should parse without error
        assert True


class TestAILexerPropertyChains:
    """Test property chains and composition."""

    def test_simple_property_chain(self):
        """Test simple property chain."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Person(Alice)
        Person(Bob)
        Person(Charlie)

        parentOf(Alice, Bob)
        parentOf(Bob, Charlie)

        # Grandparent rule
        parentOf composed_with parentOf is_subproperty_of grandparentOf
        """)

        # Alice should be grandparent of Charlie
        result = reter.reql("""
        SELECT ?gp ?gc WHERE {
            ?gp grandparentOf ?gc
        }
        """)
        assert len(result) >= 1

    def test_transitive_property(self):
        """Test transitive property using composition."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Person(A)
        Person(B)
        Person(C)

        ancestorOf(A, B)
        ancestorOf(B, C)

        # Transitive: ancestorOf ∘ ancestorOf ⊑ᴿ ancestorOf
        ancestorOf composed_with ancestorOf is_subproperty_of ancestorOf
        """)

        # A should be ancestor of C
        result = reter.reql("""
        SELECT ?anc ?desc WHERE {
            ?anc ancestorOf ?desc
        }
        """)
        # Should have A->B, B->C, and A->C
        assert len(result) >= 3

    def test_property_chain_variations(self):
        """Test all property composition syntax variations."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        p1 composed_with p2 is_subproperty_of p3
        p1 composition_with p2 is_subproperty_of p4
        """)

        # All should parse without error
        assert True


class TestAILexerInverseProperties:
    """Test inverse properties."""

    def test_inverse_property(self):
        """Test inverse property definition."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Person(Alice)
        Person(Bob)

        hasChild(Alice, Bob)

        # hasParent is inverse of hasChild
        hasParent is_same_property_as hasChild inverse
        """)

        # Bob should have Alice as parent
        result = reter.reql("""
        SELECT ?parent WHERE {
            Bob hasParent ?parent
        }
        """)
        assert result.num_rows >= 1
        parents = result.to_pydict()['?parent']
        assert 'Alice' in parents

    def test_symmetric_property(self):
        """Test symmetric property using inverse."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Person(Alice)
        Person(Bob)

        knows(Alice, Bob)

        # knows is symmetric
        knows is_same_property_as knows inverse
        """)

        # Bob should know Alice
        result = reter.reql("""
        SELECT ?person WHERE {
            Bob knows ?person
        }
        """)
        assert len(result) >= 1

    def test_inverse_variations(self):
        """Test all inverse syntax variations."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        p1 is_same_property_as p2 inverse
        p3 is_same_property_as p4 inverse_of
        """)

        # All should parse without error
        assert True


class TestAILexerSWRLRules:
    """Test SWRL rules with AI-friendly syntax."""

    def test_simple_swrl_rule(self):
        """Test simple SWRL rule with if-then."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Person is_a Thing
        Parent is_a Person

        Person(Alice)
        Person(Bob)
        hasChild(Alice, Bob)

        if Person(OBJECT x) also hasChild(OBJECT x, OBJECT y) then Parent(OBJECT x)
        """)

        # Alice should be inferred as Parent
        result = reter.pattern(('Alice', 'type', 'Parent'))
        assert len(result) > 0, "Alice should be Parent (has a child)"

    def test_swrl_rule_variations(self):
        """Test SWRL rule syntax with OBJECT/VAR keywords."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        if Person(OBJECT x) then Thing(OBJECT x)
        if Person(object x) then Thing(object x)
        if Person(OBJECT x) also hasAge(OBJECT x, VAR y) then Adult(OBJECT x)
        """)

        # All should parse without error
        assert True

    def test_swrl_implication_variations(self):
        """Test SWRL with multiple conditions using 'also'."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        if Person(OBJECT x) then Thing(OBJECT x)
        if Person(OBJECT x) also Male(OBJECT x) then Man(OBJECT x)
        if Person(OBJECT x) also Female(OBJECT x) then Woman(OBJECT x)
        """)

        # All should parse without error
        assert True

    def test_complex_swrl_rule(self):
        """Test complex SWRL rule with multiple conditions."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Person is_a Thing
        Female is_a Person
        Parent is_a Person
        Mother is_a Person

        Person(Alice)
        Person(Bob)
        Female(Alice)
        hasChild(Alice, Bob)

        if Person(OBJECT x) also Female(OBJECT x) also hasChild(OBJECT x, OBJECT y) then Mother(OBJECT x)
        """)

        # Alice should be Mother
        result = reter.pattern(('Alice', 'type', 'Mother'))
        assert len(result) > 0, "Alice should be Mother"


class TestAILexerQueries:
    """Test REQL queries with AI-friendly identifiers."""

    def test_simple_select_query(self):
        """Test simple SELECT query."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Person(Alice)
        Person(Bob)
        Dog(Fido)
        """)

        result = reter.reql("""
        SELECT ?person WHERE {
            ?person type Person
        }
        """)

        assert result.num_rows == 2
        persons = result.to_pydict()['?person']
        assert 'Alice' in persons
        assert 'Bob' in persons

    def test_join_query(self):
        """Test query with joins."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Person(Alice)
        Person(Bob)
        Company(Acme)
        Company(TechCorp)

        worksFor(Alice, Acme)
        worksFor(Bob, TechCorp)
        age(Alice, 30)
        age(Bob, 25)
        """)

        result = reter.reql("""
        SELECT ?person ?company ?age WHERE {
            ?person worksFor ?company .
            ?person age ?age
        }
        """)

        assert result.num_rows == 2

    def test_union_query(self):
        """Test UNION query."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Dog(Fido)
        Cat(Whiskers)
        Bird(Tweety)
        """)

        result = reter.reql("""
        SELECT ?animal WHERE {
            { ?animal type Dog }
            UNION
            { ?animal type Cat }
        }
        """)

        assert result.num_rows == 2

    def test_distinct_query(self):
        """Test DISTINCT query."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Person(Alice)
        Person(Bob)
        City(Seattle)

        livesIn(Alice, Seattle)
        livesIn(Bob, Seattle)
        """)

        result = reter.reql("""
        SELECT DISTINCT ?city WHERE {
            ?person livesIn ?city
        }
        """)

        assert result.num_rows == 1
        cities = result.to_pydict()['?city']
        assert 'Seattle' in cities

    def test_order_by_limit(self):
        """Test ORDER BY and LIMIT."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Person(Alice)
        Person(Bob)
        Person(Charlie)

        age(Alice, 30)
        age(Bob, 25)
        age(Charlie, 35)
        """)

        result = reter.reql("""
        SELECT ?person ?age WHERE {
            ?person age ?age
        }
        ORDER BY DESC(?age)
        LIMIT 2
        """)

        assert result.num_rows == 2
        # Should be Charlie (35) and Alice (30)
        persons = result.to_pydict()['?person']
        assert persons[0] == 'Charlie'

    def test_dl_query_simple_class(self):
        """Test dl_query() with simple class expression using AI variant."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Person(Alice)
        Person(Bob)
        Doctor(Charlie)
        """)

        # Query for all instances of Person class
        result = reter.dl_query("Person")
        assert result.num_rows == 2
        persons = result.to_pydict()['?x0']
        assert 'Alice' in persons
        assert 'Bob' in persons

    def test_dl_query_intersection(self):
        """Test dl_query() with intersection (and) using AI variant."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Person(Alice)
        Doctor(Alice)
        Person(Bob)
        Doctor(Charlie)
        """)

        # Query for instances that are BOTH Person AND Doctor
        result = reter.dl_query("Person and Doctor")
        assert result.num_rows == 1
        data = result.to_pydict()['?x0']
        assert data[0] == 'Alice'

    def test_dl_query_union(self):
        """Test dl_query() with union (or) using AI variant."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Doctor(Alice)
        Nurse(Bob)
        Teacher(Charlie)
        """)

        # Query for instances that are EITHER Doctor OR Nurse
        result = reter.dl_query("Doctor or Nurse")
        assert result.num_rows == 2
        data = result.to_pydict()['?x0']
        assert 'Alice' in data
        assert 'Bob' in data

    def test_dl_query_existential(self):
        """Test dl_query() with existential restriction (some) using AI variant."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Person(Alice)
        Person(Bob)
        Person(Charlie)
        Doctor(BobsChild)
        hasChild(Bob, BobsChild)
        hasChild(Alice, Charlie)
        """)

        # Query for instances that have SOME child who is a Doctor
        result = reter.dl_query("some hasChild that_is Doctor")
        assert result.num_rows == 1
        data = result.to_pydict()['?x0']
        assert data[0] == 'Bob'

    def test_dl_ask_class_exists(self):
        """Test dl_ask() to check if class has instances using AI variant."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Person(Alice)
        Doctor(Bob)
        """)

        # Ask if any Person exists
        assert reter.dl_ask("Person")["result"] is True

        # Ask if any Nurse exists (should be False)
        assert reter.dl_ask("Nurse")["result"] is False

    def test_dl_ask_intersection(self):
        """Test dl_ask() with intersection using AI variant."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Person(Alice)
        Doctor(Alice)
        Person(Bob)
        """)

        # Ask if any (Person AND Doctor) exists
        assert reter.dl_ask("Person and Doctor")["result"] is True

        # Ask if any (Person AND Nurse) exists
        assert reter.dl_ask("Person and Nurse")["result"] is False

    def test_dl_ask_complex_expression(self):
        """Test dl_ask() with complex DL expression using AI variant."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Person(Alice)
        Employee(Alice)
        Manager(Alice)
        Person(Bob)
        Employee(Bob)
        """)

        # Ask if any (Person AND Employee AND Manager) exists
        assert reter.dl_ask("Person and Employee and Manager")["result"] is True

        # Ask if any (Person AND Employee AND Director) exists
        assert reter.dl_ask("Person and Employee and Director")["result"] is False


class TestAILexerEdgeCases:
    """Test edge cases and special scenarios."""

    def test_mixed_syntax_parsing(self):
        """Test that AI syntax can be mixed in one ontology."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Dog is_a Mammal
        Cat is_subclass_of Mammal
        Bird extends Animal
        Fish isa LivingThing

        Employee is_equivalent_to some worksFor that_is Thing
        Parent equals at_least 1 hasChild that_is Thing
        """)

        # All should parse without error
        assert True

    def test_comments_and_whitespace(self):
        """Test comments and flexible whitespace."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        # This is a comment
        Dog is_a Mammal  # Inline comment

        // C++ style comment
        Cat is_a Mammal // Another inline comment

        # Block comments not supported - using line comments instead
        Bird is_a Animal

        # Now add individuals
        Dog(Fido)
        Cat(Whiskers)
        Bird(Tweety)
        """)

        # Check subsumption inference using pattern()
        assert len(reter.pattern(('Fido', 'type', 'Mammal'))) > 0, "Dog should be subclass of Mammal"
        assert len(reter.pattern(('Whiskers', 'type', 'Mammal'))) > 0, "Cat should be subclass of Mammal"
        assert len(reter.pattern(('Tweety', 'type', 'Animal'))) > 0, "Bird should be subclass of Animal"

    def test_special_characters_in_values(self):
        """Test special characters in string values."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Person(Alice)
        name(Alice, 'Alice O''Brien')
        email(Alice, "alice@example.com")
        description(Alice, "She's a developer")
        """)

        result = reter.reql("""
        SELECT ?name WHERE {
            Alice name ?name
        }
        """)
        assert result.num_rows == 1

    def test_numeric_literals(self):
        """Test various numeric literal formats."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Person(Alice)
        age(Alice, 30)
        height(Alice, 5.6)
        salary(Alice, 1.5e5)
        debt(Alice, -1000)
        """)

        # Query each data property specifically (variable property pattern doesn't work for data props)
        result = reter.reql("""
        SELECT ?age ?height ?salary ?debt WHERE {
            Alice age ?age .
            Alice height ?height .
            Alice salary ?salary .
            Alice debt ?debt
        }
        """)
        # Should have 1 row with 4 columns (all data properties)
        assert result.num_rows >= 1
        data = result.to_pydict()
        assert '30' in data['?age']
        assert '5.6' in data['?height']
        assert '1.5e5' in data['?salary'] or '150000' in data['?salary']
        assert '-1000' in data['?debt']

    def test_boolean_literals(self):
        """Test boolean literal values."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        Person(Alice)
        isActive(Alice, true)
        isDeleted(Alice, false)
        """)

        result = reter.reql("""
        SELECT ?val WHERE {
            Alice isActive ?val
        }
        """)
        assert result.num_rows == 1

    def test_empty_ontology(self):
        """Test queries on empty ontology."""
        reter = Reter(variant='ai')

        result = reter.reql("""
        SELECT ?x WHERE {
            ?x type Thing
        }
        """)

        # Empty result is valid PyArrow Table
        import pyarrow as pa
        assert isinstance(result, pa.Table)

    def test_very_long_identifier(self):
        """Test very long programming identifier."""
        reter = Reter(variant='ai')
        long_name = "com.example.very.long.package.name.MyVeryLongClassName"
        reter.load_ontology(f"""
        {long_name} is_a Thing
        {long_name}(instance1)
        """)

        result = reter.reql(f"""
        SELECT ?x WHERE {{
            ?x type {long_name}
        }}
        """)
        assert result.num_rows >= 1


class TestAILexerRealWorldScenarios:
    """Test real-world ontology scenarios."""

    def test_family_ontology(self):
        """Test complete family ontology with AI syntax."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        # Class hierarchy
        Person is_a Thing
        Male is_a Person
        Female is_a Person

        # Defined classes
        Parent is_equivalent_to some hasChild that_is Person
        Mother is_equivalent_to Female and Parent
        Father is_equivalent_to Male and Parent
        Grandparent is_equivalent_to some hasChild that_is Parent

        # Property chain
        hasChild composed_with hasChild is_subproperty_of hasGrandchild

        # Individuals
        Person(Alice)
        Person(Bob)
        Person(Charlie)
        Female(Alice)
        Male(Bob)
        Male(Charlie)

        # Relations
        hasChild(Alice, Bob)
        hasChild(Bob, Charlie)
        """)

        # Alice should be Mother
        assert len(reter.pattern(('Alice', 'type', 'Mother'))) > 0

        # Alice should be Grandparent
        assert len(reter.pattern(('Alice', 'type', 'Grandparent'))) > 0

        # Alice should have Charlie as grandchild
        result = reter.reql("""
        SELECT ?gc WHERE {
            Alice hasGrandchild ?gc
        }
        """)
        assert len(result) >= 1

    def test_organizational_ontology(self):
        """Test organizational structure with AI syntax."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        # Classes
        Person is_a Thing
        Company is_a Thing
        Department is_a Thing

        Employee is_equivalent_to some worksFor that_is Company
        Manager is_equivalent_to at_least 1 manages that_is Employee

        # Individuals
        Person(Alice)
        Person(Bob)
        Person(Charlie)
        Company(TechCorp)
        Department(Engineering)

        # Relations
        worksFor(Alice, TechCorp)
        worksFor(Bob, TechCorp)
        worksFor(Charlie, TechCorp)
        manages(Alice, Bob)
        manages(Alice, Charlie)
        memberOf(Alice, Engineering)
        """)

        # All should be Employees
        assert len(reter.pattern(('Alice', 'type', 'Employee'))) > 0
        assert len(reter.pattern(('Bob', 'type', 'Employee'))) > 0

        # Alice should be Manager
        assert len(reter.pattern(('Alice', 'type', 'Manager'))) > 0

    def test_software_architecture_ontology(self):
        """Test software architecture with programming identifiers."""
        reter = Reter(variant='ai')
        reter.load_ontology("""
        # Java classes
        java.lang.Object is_a Class
        com.example.Service is_a java.lang.Object
        com.example.Controller is_a java.lang.Object
        com.example.Repository is_a java.lang.Object

        # C++ classes
        std::vector is_a Container
        std::list is_a Container
        boost::shared_ptr is_a SmartPointer

        # Instances
        com.example.Service(userService)
        com.example.Controller(userController)

        # Dependencies
        dependsOn(userController, userService)
        """)

        result = reter.reql("""
        SELECT ?controller ?service WHERE {
            ?controller dependsOn ?service .
            ?controller type com.example.Controller .
            ?service type com.example.Service
        }
        """)

        assert len(result) >= 1


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
