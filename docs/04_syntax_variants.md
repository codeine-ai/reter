# DL Syntax Variants

RETER supports two syntax variants for Description Logic:

1. **Unicode** - Mathematical symbols (default)
2. **ASCII** - Self-documenting English keywords

Both compile to the same internal representation and share identical semantics.

### ASCII Syntax Design Philosophy

The ASCII variant uses **verbose, self-documenting keywords** that read like natural English:

```
Dog IS_SUB_CONCEPT_OF Animal
Parent IS_SAME_CONCEPT_AS Person INTERSECTION_WITH SOME hasChild THAT_IS Person
```

This makes ontologies immediately understandable without needing to learn Unicode symbols or DL notation conventions.

---

## Quick Comparison

| Construct | Unicode Syntax | ASCII Syntax |
|-----------|----------------|--------------|
| **Subsumption** | `Dog ⊑ᑦ Animal` | `Dog IS_SUB_CONCEPT_OF Animal` |
| **Intersection** | `Person ⊓ Adult` | `Person INTERSECTION_WITH Adult` |
| **Union** | `Cat ⊔ Dog` | `Cat UNION_WITH Dog` |
| **Complement** | `¬Animal` | `COMPLEMENT_OF Animal` |
| **Existential** | `∃ hasChild ․ Doctor` | `SOME hasChild THAT_IS Doctor` |
| **Universal** | `∀ hasChild ․ Doctor` | `ALL hasChild THAT_IS Doctor` |
| **Parentheses** | `（...）` | `(...)` |
| **Curly braces** | `｛...｝` | `{...}` |
| **Square brackets** | `［...］` | `[...]` |
| **SWRL rule** | `⊢ ... → ...` | `IF ... THEN ...` |
| **SWRL and** | `∧` | `AND` |
| **Top/Bottom** | `⊤` / `⊥` | `TOP` / `BOTTOM` |

---

## Complete Token Mapping

### Concept Operators

| Unicode | ASCII | Meaning |
|---------|-------|---------|
| `⊑ᑦ` | `IS_SUB_CONCEPT_OF` | SubClassOf |
| `⊒ᑦ` | `IS_SUPER_CONCEPT_OF` | SuperClassOf |
| `≡ᑦ` | `IS_SAME_CONCEPT_AS` | EquivalentClasses |
| `⊓` | `INTERSECTION_WITH` | Intersection (AND) |
| `⊔` | `UNION_WITH` | Union (OR) |
| `¬` | `COMPLEMENT_OF` | Complement (NOT) |
| `⊤` | `TOP` | Thing (top concept) |
| `⊥` | `BOTTOM` | Nothing (bottom concept) |

### Role Operators

| Unicode | ASCII | Meaning |
|---------|-------|---------|
| `⊑ᴿ` | `IS_SUB_ROLE_OF` | SubObjectPropertyOf |
| `⊒ᴿ` | `IS_SUPER_ROLE_OF` | SuperObjectPropertyOf |
| `≡ᴿ` | `IS_SAME_ROLE_AS` | EquivalentObjectProperties |
| `⊑ᴰ` | `IS_SUB_ATTRIBUTE_OF` | SubDataPropertyOf |
| `⊒ᴰ` | `IS_SUPER_ATTRIBUTE_OF` | SuperDataPropertyOf |
| `≡ᴰ` | `IS_SAME_ATTRIBUTE_AS` | EquivalentDataProperties |
| `∘` | `COMPOSITION_WITH` | Role composition |
| `⁻` | `INVERSE` | Inverse property |

### Restrictions

| Unicode | ASCII | Meaning |
|---------|-------|---------|
| `∃` | `SOME` | SomeValuesFrom (existential) |
| `∀` | `ALL` | AllValuesFrom (universal) |
| `․` | `THAT_IS` | Role-filler separator |

### Comparison Operators

| Unicode | ASCII | Meaning |
|---------|-------|---------|
| `﹦` | `=` | Equal |
| `≠` | `!=` | Not equal |
| `﹤` | `<` | Less than |
| `﹥` | `>` | Greater than |
| `≤` | `<=` | Less than or equal |
| `≥` | `>=` | Greater than or equal |

### SWRL Operators

| Unicode | ASCII | Meaning |
|---------|-------|---------|
| `⊢` | `IF` | Rule start |
| `→` | `THEN` | Implication |
| `∧` | `AND` | Conjunction |
| `⌂` | `?` | Variable prefix |

### Special Symbols

| Unicode | ASCII | Meaning |
|---------|-------|---------|
| `（` | `(` | Left parenthesis |
| `）` | `)` | Right parenthesis |
| `，` | `,` | Comma |
| `｛` | `{` | Left brace |
| `｝` | `}` | Right brace |
| `［` | `[` | Left bracket |
| `］` | `]` | Right bracket |
| `：` | `:` | Colon |
| `¤` | `$` | Currency symbol |

### Other

| Unicode | ASCII | Meaning |
|---------|-------|---------|
| `⊑ᴷ` | `HAS_KEY` | HasKey |
| `≡ᵀ` | `IS_SAME_DATA_TYPE_AS` | Datatype definition |
| `Ω` | `EVERYTHING` | Top datatype |
| `⏘` | `LEN` | String length |
| `℞` | `PATTERN` | Regex pattern |

---

## Example: Family Ontology

### Unicode Syntax

```
// Classes
Person ⊑ᑦ ⊤
Adult ⊑ᑦ Person
Child ⊑ᑦ Person

// Properties
hasChild ⊑ᴿ hasRelative
hasParent ≡ᴿ hasChild⁻

// Restrictions
Parent ≡ᑦ Person ⊓ ∃ hasChild ․ Person

// Individuals
Person（john）
Person（mary）
hasChild（john，mary）

// SWRL Rule
⊢ hasChild（⌂x，⌂y）∧ hasChild（⌂y，⌂z） → hasGrandchild（⌂x，⌂z）
```

### ASCII Syntax

```
// Classes
Person IS_SUB_CONCEPT_OF TOP
Adult IS_SUB_CONCEPT_OF Person
Child IS_SUB_CONCEPT_OF Person

// Properties
hasChild IS_SUB_ROLE_OF hasRelative
hasParent IS_SAME_ROLE_AS hasChild INVERSE

// Restrictions
Parent IS_SAME_CONCEPT_AS Person INTERSECTION_WITH SOME hasChild THAT_IS Person

// Individuals
Person(john)
Person(mary)
hasChild(john, mary)

// SWRL Rule
IF hasChild(?x, ?y) AND hasChild(?y, ?z) THEN hasGrandchild(?x, ?z)
```

---

## Usage in Python

```python
from reter import Reter

# Unicode syntax (default)
r1 = Reter(variant="unicode")
r1.load_ontology("Dog ⊑ᑦ Animal")

# ASCII syntax
r2 = Reter(variant="ascii")
r2.load_ontology("Dog IS_SUB_CONCEPT_OF Animal")

# AI-friendly syntax (supports programming language identifiers)
r3 = Reter(variant="ai")
r3.load_ontology("Dog IS_SUB_CONCEPT_OF Animal")

# Query with DL expressions
result = r1.dl_query("Person ⊓ Doctor")  # Unicode
result = r2.dl_query("Person and Doctor")  # ASCII
```

---

## When to Use Each Syntax

### Use Unicode When:
- ✅ Writing ontologies by hand with IDE support
- ✅ Need compact, mathematical notation
- ✅ Following academic/research conventions
- ✅ Your editor/terminal supports Unicode

### Use ASCII When:
- ✅ Generating ontologies programmatically
- ✅ Working in ASCII-only environments
- ✅ **Maximum readability** - reads like natural English
- ✅ Easier for non-experts to read
- ✅ Avoiding Unicode input complexity
- ✅ Better for diffs/version control (standard ASCII)
- ✅ Self-documenting code (verbose keywords)

---

## File Extensions

Suggested conventions:

- `.dl` - Unicode syntax (default)
- `.dla` - ASCII syntax

---

## Migration Guide

### Converting Unicode → ASCII

Use search/replace (regex recommended):

| Unicode | ASCII Replacement |
|---------|------------------|
| `⊑ᑦ` | ` IS_SUB_CONCEPT_OF ` |
| `⊒ᑦ` | ` IS_SUPER_CONCEPT_OF ` |
| `≡ᑦ` | ` IS_SAME_CONCEPT_AS ` |
| `（` | `(` |
| `）` | `)` |
| `，` | `,` |
| `∃` | `SOME` |
| `∀` | `ALL` |
| `․` | ` THAT_IS ` |
| `⊓` | ` INTERSECTION_WITH ` |
| `⊔` | ` UNION_WITH ` |
| `¬` | `COMPLEMENT_OF ` |

### Converting ASCII → Unicode

Reverse the mapping above.

---

## Performance

Both syntaxes have **identical performance**:
- Same parser grammar
- Same inference rules
- Only lexical difference

---

## Variant Selection

The syntax variant is specified when creating the `Reter` instance:

```python
from reter import Reter

# Choose variant at construction time
r = Reter(variant="unicode")  # Default
r = Reter(variant="ascii")    # ASCII keywords
r = Reter(variant="ai")       # AI-friendly

# The variant affects:
# 1. load_ontology() - how DL statements are parsed
# 2. dl_query() - how DL expressions are parsed
# 3. dl_ask() - how DL expressions are parsed
```

---

## See Also

- [Grammar Reference](01_grammar.md) - Description Logic syntax
- [API Reference](02_api_reference.md) - Python API documentation
- [REQL Queries](03_reql.md) - SPARQL-like query language

---

**Last Updated**: December 2025
