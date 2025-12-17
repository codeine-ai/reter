# Description Logic Grammar Specification

## Overview

RETER uses a custom Description Logic (DL) language for defining OWL 2 RL ontologies. The language supports:

- **Concept (class) definitions** with subsumption and equivalence
- **Role (property) definitions** including object and data properties
- **Individual (instance) assertions**
- **SWRL rules** for complex inference
- **Rich datatypes** including numbers, strings, dates, and durations
- **Complex restrictions** including cardinality, value, and existential/universal quantification

### Why Unicode Operators?

The DL language uses Unicode mathematical symbols (⊑, ≡, ∀, ∃, etc.) to provide:
- **Compact syntax** - Mathematical notation is concise
- **Readability** - Symbols match standard DL literature
- **Unambiguous parsing** - No keyword conflicts with identifiers

---

## Lexer Rules (Tokens)

### Special Symbols

| Token | Symbol | Description |
|-------|--------|-------------|
| `OPEN` | （ | Full-width left parenthesis |
| `CLOSE` | ） | Full-width right parenthesis |
| `COMMA` | ， | Full-width comma |
| `SOPEN` | ｛ | Full-width left brace (set notation) |
| `SCLOSE` | ｝ | Full-width right brace |
| `QOPEN` | ［ | Full-width left bracket (unnamed instances) |
| `QCLOSE` | ］ | Full-width right bracket |

**Why full-width symbols?** To avoid conflicts with ASCII characters in identifiers and string literals.

### Concept (Class) Operators

| Token | Symbol | Meaning | Example |
|-------|--------|---------|---------|
| `SUB` | ⊑ᑦ | Subsumption (subclass) | `Dog ⊑ᑦ Animal` |
| `SUP` | ⊒ᑦ | Supersumption (superclass) | `Animal ⊒ᑦ Dog` |
| `EQV` | ≡ᑦ | Equivalence | `Cat ≡ᑦ Feline` |
| `AND` | ⊓ | Intersection | `Pet ⊓ Dog` |
| `OR` | ⊔ | Union | `Cat ⊔ Dog` |
| `NOT` | ¬ | Complement | `¬Animal` |
| `TOP` | ⊤ | Universal concept (Thing) | `⊤` |
| `BOTTOM` | ⊥ | Empty concept (Nothing) | `⊥` |

### Role (Property) Operators

| Token | Symbol | Meaning | Example |
|-------|--------|---------|---------|
| `SUBR` | ⊑ᴿ | Role inclusion (object property) | `hasDog ⊑ᴿ hasPet` |
| `SUPR` | ⊒ᴿ | Role super-inclusion | `hasPet ⊒ᴿ hasDog` |
| `EQVR` | ≡ᴿ | Role equivalence | `owns ≡ᴿ hasOwned` |
| `SUBD` | ⊑ᴰ | Data role inclusion | `age ⊑ᴰ numericProperty` |
| `SUPD` | ⊒ᴰ | Data role super-inclusion | `numericProperty ⊒ᴰ age` |
| `EQVD` | ≡ᴰ | Data role equivalence | `birthYear ≡ᴰ yearBorn` |
| `INVERSE` | ⁻ | Role inversion | `hasChild⁻` (= isChildOf) |
| `CIRCLE` | ∘ | Role composition | `hasParent ∘ hasSibling` |

### Restriction Operators

| Token | Symbol | Meaning | Example |
|-------|--------|---------|---------|
| `SOME` | ∃ | Existential quantification | `∃ hasChild ․ Doctor` |
| `ONLY` | ∀ | Universal quantification | `∀ hasChild ․ Doctor` |
| `EQ` | ﹦ | Equality / Exact cardinality | `﹦ 2 hasChild ․ ⊤` |
| `LT` | ﹤ | Less than | `﹤ 3 hasChild ․ ⊤` |
| `GT` | ﹥ | Greater than | `﹥ 1 hasChild ․ ⊤` |
| `LE` | ≤ | Less than or equal | `≤ 2 hasChild ․ ⊤` |
| `GE` | ≥ | Greater than or equal | `≥ 1 hasChild ․ ⊤` |
| `NE` | ≠ | Not equal / Different from | `≠ 0 hasChild ․ ⊤` |
| `DOT` | ․ | Role separator | `∃ hasPet ․ Dog` |

### SWRL Operators

| Token | Symbol | Meaning |
|-------|--------|---------|
| `SWRLSTART` | ⊢ | Start of SWRL rule |
| `SWRLTHEN` | → | Implication (then) |
| `SWRLAND` | ∧ | Conjunction (and) |
| `HOUSE` | ⌂ | Variable prefix |
| `COLON` | ： | Namespace separator |

### Other Symbols

| Token | Symbol | Description |
|-------|--------|-------------|
| `SUBK` | ⊑ᴷ | Has key (functional dependency) |
| `EQV2` | ≡ᵀ | Datatype definition |
| `TOPBOUND` | Ω | Top datatype (all values) |
| `LEN` | ⏘ | String length facet |
| `PAT` | ℞ | Pattern (regex) facet |
| `CUR` | ¤ | Currency prefix for decimals |

### Datatype Literals

| Token | Pattern | Example | Type |
|-------|---------|---------|------|
| `BOL` | `𝙵` \| `𝚃` | `𝚃` | Boolean (false/true) |
| `NAT` | `[0-9]+` | `42` | Natural number |
| `NUM` | `[+-]?[0-9]+` | `-17` | Integer |
| `DBL` | `[+-]?[0-9]*\.[0-9]+` | `3.14` | Double (float) |
| `DEC` | `¤[0-9]*\.[0-9]+` | `¤19.99` | Decimal (currency) |
| `DTM` | `⧗YYYY-MM-DD...` | `⧗2025-10-26` | DateTime |
| `DUR` | `⧖P...` | `⧖P1Y2M3D` | Duration (ISO 8601) |
| `STR` | `'...'` | `'hello'` | String (single quotes) |

**DateTime format**: `⧗YYYY-MM-DDTHH:MM:SS.sss±HH:MM`
**Duration format**: `⧖PnYnMnDTnHnMnS` (ISO 8601)

### Identifiers

| Token | Pattern | Example |
|-------|---------|---------|
| `ID` | `NAME` \| `NINT` | `Person`, `"Complex Name"` |
| `NAME` | ASCII without spaces | `Dog`, `hasPet`, `Person_123` |
| `NINT` | `"..."` | `"Complex Name"`, `"123 Main St"` |

**NAME rules**:
- ASCII characters only (0x21-0x7E)
- Cannot start with: digit, `'`, `"`, `+`, `-`
- Cannot contain: whitespace, quotes

**NINT (Named Internationalized)**:
- Quoted identifiers for complex names
- Allows spaces, Unicode, special characters
- Escaped quotes: `"He said \"hello\""`

---

## Parser Rules (Grammar)

### Statement Types

The top-level grammar accepts a `paragraph` (sequence of statements):

```antlr
start : paragraph EOF ;

paragraph
    : statement
    | paragraph statement
    ;
```

Each `statement` can be one of:

#### 1. Concept Axioms

**Subsumption** (SubClassOf):
```
Dog ⊑ᑦ Animal
```

**Equivalence** (EquivalentClasses):
```
Cat ≡ᑦ Feline
≡ᑦ（Cat，Feline，FelisCatus）  // Multi-class equivalence
```

**Disjointness**:
```
¬≡ᑦ（Cat，Dog，Bird）  // Pairwise disjoint
```

**Disjoint Union**:
```
Animal ¬≡ᑦ（Mammal，Bird，Reptile）  // Partitions Animal
```

#### 2. Role Axioms

**Object Property Inclusion**:
```
hasDog ⊑ᴿ hasPet
```

**Object Property Equivalence**:
```
owns ≡ᴿ hasOwnership
≡ᴿ（owns，hasOwnership，possesses）  // Multi-property equivalence
```

**Object Property Disjointness**:
```
¬≡ᴿ（hasFather，hasMother）
```

**Data Property Inclusion**:
```
age ⊑ᴰ numericValue
```

**Role Chain** (SubObjectPropertyOf composition):
```
hasParent ∘ hasSibling ⊑ᴿ hasUncleOrAunt
```

#### 3. Concept Expressions

**Atomic**:
```
Person
⊤  // Thing (top concept)
⊥  // Nothing (bottom concept)
```

**Boolean Operators**:
```
Person ⊓ Adult        // Intersection (and)
Cat ⊔ Dog             // Union (or)
¬Animal               // Complement (not)
```

**Restrictions**:

**Existential (∃ - SomeValuesFrom)**:
```
∃ hasChild ․ Doctor   // Has at least one child who is a Doctor
```

**Universal (∀ - AllValuesFrom)**:
```
∀ hasChild ․ Doctor   // All children are Doctors
```

**Self-reference**:
```
∃ likes ․ ∘          // Likes itself (hasSelf)
```

**Cardinality**:
```
﹦ 2 hasChild ․ ⊤     // Exactly 2 children
≥ 1 hasChild ․ ⊤      // At least 1 child (minCardinality)
≤ 3 hasChild ․ ⊤      // At most 3 children (maxCardinality)
```

**Data Property Restrictions**:
```
∃ age Ω               // Has age property (SomeValuesFrom)
∀ age ≥18             // All age values ≥ 18 (AllValuesFrom)
```

**Role Inversion**:
```
hasChild⁻             // Inverse of hasChild (= isChildOf)
```

#### 4. Individual Assertions

**Class Assertion** (InstanceOf):
```
Person（john）        // john is a Person
```

**Object Property Assertion**:
```
hasChild（mary，john）  // mary hasChild john
```

**Data Property Assertion**:
```
age（john，25）         // john's age is 25
```

**Individual Equality**:
```
john ﹦ johnSmith      // Same individual
﹦｛john，johnSmith，j․smith｝  // All same
```

**Individual Inequality**:
```
john ≠ mary           // Different individuals
≠｛alice，bob，charlie｝  // Pairwise different
```

#### 5. Keys (HasKey)

**Functional Dependencies**:
```
Person ⊑ᴷ（ssn）                      // SSN uniquely identifies Person
Person ⊑ᴷ（firstName，lastName）      // First+last name is unique
Person ⊑ᴷ（email）⊓（birthDate）      // Email + birthdate is unique
```

#### 6. SWRL Rules

**Syntax**:
```
⊢ antecedent → consequent
```

**Variables**:
- Object variables: `⌂x`, `⌂person`
- Data variables: `⌂：age`, `⌂：value`

**Atoms**:
```
Person（⌂x）                          // Class atom
hasChild（⌂x，⌂y）                   // Object property atom
age（⌂x，⌂：age）                    // Data property atom
﹦（⌂x，⌂y）                          // Same individual
≠（⌂x，⌂y）                          // Different individuals
```

**Built-ins**:
```
：greaterThan（⌂：age，18）          // Data comparison
：add（⌂：sum，⌂：a，⌂：b）          // Arithmetic
```

**Example SWRL Rule**:
```
⊢ Person（⌂x）∧ age（⌂x，⌂：a）∧ ：greaterThan（⌂：a，18） → Adult（⌂x）
```
*"If x is a Person with age greater than 18, then x is an Adult"*

#### 7. Datatype Definitions

**Custom Datatypes**:
```
AdultAge ≡ᵀ ≥18                      // Integer ≥ 18
PositiveDecimal ≡ᵀ ﹥0.0             // Float > 0
ShortString ≡ᵀ ⏘≤50                  // String length ≤ 50
EmailPattern ≡ᵀ ℞'.*@.*\..*'        // Regex pattern
```

**Facets**:
- `≥ value` - minInclusive
- `﹥ value` - minExclusive
- `≤ value` - maxInclusive
- `﹤ value` - maxExclusive
- `⏘≥ n` - minLength
- `⏘≤ n` - maxLength
- `℞ 'pattern'` - pattern (regex)

**Datatype Combinations**:
```
（≥18，≤65）                          // Integer between 18 and 65
｛1，2，3，5，7｝                      // Enumeration
≤100 ⊔ ≥200                          // Union of ranges
```

---

## Grammar Precedence and Associativity

### Concept Expressions

**Precedence** (highest to lowest):
1. Primary (atomic, parentheses, instance sets)
2. Role inversion (`⁻`)
3. Restrictions (`∃`, `∀`, cardinality)
4. Negation (`¬`)
5. Intersection (`⊓`)
6. Union (`⊔`)

**Associativity**:
- `⊓` and `⊔` are **left-associative**
- Restriction operators are **non-associative** (use parentheses)

**Examples**:
```
A ⊓ B ⊔ C        // Parsed as: (A ⊓ B) ⊔ C
¬A ⊓ B           // Parsed as: (¬A) ⊓ B
∃ r ․ A ⊔ B      // Parsed as: (∃ r ․ A) ⊔ B
∃ r ․ （A ⊔ B）   // Explicitly: ∃ r ․ (A ⊔ B)
```

### Role Chains

**Syntax**:
```
role_chain: node ∘ node
          | role_chain ∘ node
```

**Left-associative**:
```
r ∘ s ∘ t  // Parsed as: (r ∘ s) ∘ t
```

---

## OWL 2 RL Coverage

The DL grammar covers **OWL 2 RL** (Rule Language) profile:

### Supported OWL 2 Constructs

✅ **Classes**: SubClassOf, EquivalentClasses, DisjointClasses, DisjointUnion
✅ **Properties**: SubObjectPropertyOf, EquivalentObjectProperties, InverseObjectProperties
✅ **Property Characteristics**: Transitive, Symmetric, Asymmetric, Reflexive, Irreflexive, Functional, InverseFunctional
✅ **Restrictions**: SomeValuesFrom, AllValuesFrom, HasValue, HasSelf
✅ **Cardinality**: MinCardinality, MaxCardinality, ExactCardinality
✅ **Individuals**: ClassAssertion, ObjectPropertyAssertion, DataPropertyAssertion, SameIndividual, DifferentIndividuals
✅ **Keys**: HasKey
✅ **SWRL**: Safe SWRL rules with built-ins

### OWL 2 RL Restrictions

**NOT supported** (OWL 2 Full/DL only):
- ❌ Unrestricted existential/universal on left side of axioms
- ❌ Transitive properties with cardinality restrictions
- ❌ Property chains with unrestricted transitivity

These restrictions ensure **polynomial-time reasoning**.

---

## Examples

### Example 1: Family Ontology

```
// Classes
Person ⊑ᑦ ⊤
Adult ⊑ᑦ Person
Child ⊑ᑦ Person
¬≡ᑦ（Adult，Child）

// Properties
hasChild ⊑ᴿ hasRelative
hasParent ≡ᴿ hasChild⁻

// Restrictions
Parent ≡ᑦ Person ⊓ ∃ hasChild ․ Person
Grandparent ≡ᑦ Person ⊓ ∃ hasChild ․ Parent

// Individuals
Person（john）
Person（mary）
hasChild（john，mary）

// SWRL Rule: hasGrandchild
⊢ hasChild（⌂x，⌂y）∧ hasChild（⌂y，⌂z） → hasGrandchild（⌂x，⌂z）
```

### Example 2: Numeric Datatypes

```
// Datatype definitions
AdultAge ≡ᵀ ≥18
ChildAge ≡ᵀ （≥0，﹤18）

// Class restrictions
Adult ≡ᑦ Person ⊓ ∃ age AdultAge
Child ≡ᑦ Person ⊓ ∃ age ChildAge

// Individuals
Person（alice）
age（alice，25）

// SWRL Rule: Classify adults
⊢ Person（⌂x）∧ age（⌂x，⌂：a）∧ ：greaterThanOrEqual（⌂：a，18） → Adult（⌂x）
```

### Example 3: Complex Restrictions

```
// Cardinality
HasTwoParents ≡ᑦ ﹦ 2 hasParent ․ Person
HasChildren ≡ᑦ ≥ 1 hasChild ․ Person

// Universal restriction
AllChildrenDoctors ≡ᑦ ∀ hasChild ․ Doctor

// Role composition
hasUncle ≡ᴿ hasParent ∘ hasBrother
hasGrandparent ≡ᴿ hasParent ∘ hasParent

// Keys
Person ⊑ᴷ（ssn）
Person ⊑ᴷ（email）
```

---

## Next Steps

- **[API Reference](02_api_reference.md)** - Python API documentation
- **[REQL Queries](03_reql.md)** - SPARQL-like query language
- **[Syntax Variants](04_syntax_variants.md)** - Unicode vs ASCII syntax

---

**Last Updated**: December 2025
