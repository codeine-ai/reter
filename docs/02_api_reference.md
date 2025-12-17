# Reter API Reference

## Overview

The **Reter** class provides a high-level Python interface to the RETER (OWL 2 RL) reasoning engine:

- **Description Logic parser** with Unicode and ASCII syntax variants
- **Pattern-based queries** with pandas/Arrow export
- **REQL queries** (SPARQL-like syntax)
- **Multi-language code analysis** (Python, C#, C++, JavaScript)

---

## Class: `Reter`

### Constructor

```python
from reter import Reter

# Default: Unicode syntax
reasoner = Reter()

# ASCII syntax variant
reasoner = Reter(variant="ascii")

# AI-friendly syntax variant
reasoner = Reter(variant="ai")
```

**Parameters**:
- `variant` (str, optional): Parser syntax variant - `"unicode"` (default), `"ascii"`, or `"ai"`

**Returns**: A new `Reter` instance with foundational axioms loaded (`owl:Thing`, `owl:Nothing`)

**Example**:
```python
r = Reter()
r.load_ontology("Person ⊑ᑦ Animal")
r.reason()
```

---

## Loading Ontologies

### `load_ontology(text)`

Load Description Logic statements.

**Parameters**:
- `text` (str): DL statements using Unicode or ASCII operators (see [Grammar](01_grammar.md))

**Returns**: `None`

**Example**:
```python
ontology = """
Person ⊑ᑦ Animal
Student ⊑ᑦ Person
Adult ⊑ᑦ Person
¬≡ᑦ（Student，Adult）

hasParent ⊑ᴿ hasRelative

Person（john）
Person（mary）
hasParent（john，mary）
"""

reasoner = Reter()
reasoner.load_ontology(ontology)
```

**Multi-line Support**: Statements can span multiple lines. The parser handles:
- Class axioms
- Property axioms
- Individual assertions
- SWRL rules
- Datatype definitions

**Error Handling**: Raises `RuntimeError` if parsing fails. Error messages include:
- Line and column number
- Offending text
- Expected tokens

---

### `load_ontology_file(filepath)`

Load DL ontology from a file.

**Parameters**:
- `filepath` (str): Path to file containing DL statements

**Returns**: `None`

**Example**:
```python
reasoner = Reter()
reasoner.load_ontology_file("ontologies/family.dl")
```

**Note**: The file should contain DL statements using Unicode operators (same syntax as `load_ontology()`).

---

## Querying

RETER provides multiple query methods for different use cases:

- **`pattern()`** - Main query method for pattern matching (REQL-like)
- **`instances_of()`** - Get all instances of a class
- **`get_all_facts()`** - Get all facts as Arrow table
- **`get_instances()`** - Get instances with Arrow filtering
- **`get_subsumers()`** - Get superclasses
- **`get_role_assertions()`** - Get property assertions

---

### `pattern(*patterns)`

**High-performance pattern matching** for complex queries (REQL-like).

**Parameters**:
- `*patterns`: Variable-length list of triple patterns `(subject, predicate, object)`
- Variables start with `?` (e.g., `?x`, `?person`, `?age`)

**Returns**: `QueryResultSet` - Iterable of variable bindings

**Performance**: ~22μs per query

#### Single Pattern

```python
# Find all instances of Person
results = reasoner.pattern(("?x", "type", "Person"))

for r in results:
    print(r['?x'])  # john, mary, ...
```

#### Multiple Patterns (Joins)

```python
# Find all people and their parents (2-way join)
results = reasoner.pattern(
    ("?person", "type", "Person"),
    ("?person", "hasParent", "?parent")
)

for r in results:
    print(f"{r['?person']} has parent {r['?parent']}")
```

#### Complex Joins

```python
# Find grandchildren (3-way join)
results = reasoner.pattern(
    ("?grandparent", "hasChild", "?parent"),
    ("?parent", "hasChild", "?child"),
    ("?child", "type", "Person")
)

for r in results:
    print(f"{r['?grandparent']} -> {r['?parent']} -> {r['?child']}")
```

**Performance Characteristics**:
- Simple pattern: ~22μs
- Complex joins: scales well
- Query caching: repeated queries are faster

**Variable Naming**: Variables can use any name after `?`:
- `?x`, `?y`, `?z` - Short names
- `?person`, `?parent`, `?child` - Descriptive names
- `?age`, `?value` - Data properties

**Example**:
```python
reasoner = Reter()
reasoner.load_ontology("""
Person（john）
Person（mary）
Person（alice）
hasParent（john，mary）
hasParent（mary，alice）
""")

# Who are John's ancestors?
results = reasoner.pattern(
    ("john", "hasParent", "?parent")
)
for r in results:
    print(r['?parent'])  # mary

# Transitive closure (if hasParent is transitive)
results = reasoner.pattern(
    ("john", "hasAncestor", "?ancestor")  # Inferred by SWRL or property chain
)
```

---

### `instances_of(class_name)`

**Template query** for retrieving all instances of a class.

**Parameters**:
- `class_name` (str): Concept name

**Returns**: `QueryResultSet` - Iterable of instances

**Performance**: **35μs** (template queries are pre-compiled)

**Example**:
```python
reasoner = Reter()
reasoner.load_ontology("""
Person（john）
Person（mary）
Student（john）
Student ⊑ᑦ Person
""")

# Get all persons
persons = reasoner.instances_of("Person")
for p in persons:
    print(p['?x'])  # john, mary

# Get all students
students = reasoner.instances_of("Student")
for s in students:
    print(s['?x'])  # john
```

**Difference from `pattern()`**:
- `instances_of()` is a convenience method
- Equivalent to: `pattern(("?x", "type", class_name))`

---

## Query Result Handling

### `QueryResultSet`

Iterable object returned by `pattern()` and `instances_of()`.

**Properties**:
- **Snapshot semantics**: Results represent state at creation time
- **Lazy iteration**: Results materialized during iteration
- **Variable bindings**: Each result is a dict mapping variables to values

#### Iteration

```python
results = reasoner.pattern(("?x", "type", "Person"))

# Iterate directly
for result in results:
    print(result['?x'])

# Convert to list
all_results = list(results)

# Count results
count = len(list(results))
```

#### Snapshot Semantics

```python
# Query 1: Get current persons
results1 = reasoner.pattern(("?x", "type", "Person"))
list(results1)  # ['john', 'mary']

# Add new person
reasoner.load_ontology("Person（bob）")

# Query 1 still shows snapshot (unchanged)
list(results1)  # Still ['john', 'mary']

# Fresh query shows live results
results2 = reasoner.pattern(("?x", "type", "Person"))
list(results2)  # ['john', 'mary', 'bob']
```

**Why snapshots?**
- Ensures query results don't change during iteration
- Allows multiple simultaneous queries
- Consistent with SQL SELECT semantics

**For live results**: Create a new query after ontology changes

---

### Helper Query Methods

#### `get_instances(concept)`

Get all instances of a concept.

**Parameters**:
- `concept` (str): Concept name

**Returns**: List of instance names

**Example**:
```python
persons = reasoner.get_instances("Person")
# ['john', 'mary', 'alice']
```

---

#### `get_subsumers(concept)`

Get all superclasses of a concept.

**Parameters**:
- `concept` (str): Concept name

**Returns**: List of superclass names

**Example**:
```python
supers = reasoner.get_subsumers("Student")
# ['Person', 'Animal', 'owl:Thing']
```

---

#### `get_subsumed(concept)`

Get all subclasses of a concept.

**Parameters**:
- `concept` (str): Concept name

**Returns**: List of subclass names

**Example**:
```python
subs = reasoner.get_subsumed("Animal")
# ['Person', 'Student', 'Cat', 'Dog']
```

---

#### `get_role_assertions(role=None, subject=None, object=None)`

Get property assertions with optional filtering.

**Parameters**:
- `role` (str, optional): Property name filter
- `subject` (str, optional): Subject individual filter
- `object` (str, optional): Object individual filter

**Returns**: List of (subject, role, object) tuples

**Example**:
```python
# All role assertions
all_roles = reasoner.get_role_assertions()
# [('john', 'hasParent', 'mary'), ('mary', 'hasParent', 'alice'), ...]

# Filter by role
parents = reasoner.get_role_assertions(role='hasParent')
# [('john', 'hasParent', 'mary'), ('mary', 'hasParent', 'alice')]

# Filter by subject
johns_roles = reasoner.get_role_assertions(subject='john')
# [('john', 'hasParent', 'mary'), ('john', 'age', '25')]
```

---

#### `related(subject, property_name)`

Get all objects related to a subject via a property.

**Parameters**:
- `subject` (str): Subject individual
- `property_name` (str): Property name

**Returns**: QueryResultSet with bindings for `?object`

**Example**:
```python
# Who are John's parents?
parents = reasoner.related("john", "hasParent")
for p in parents:
    print(p['?object'])  # mary
```

---

#### `property_value(subject, property_name)`

Get a single property value (for functional properties).

**Parameters**:
- `subject` (str): Subject individual
- `property_name` (str): Property name

**Returns**: String value or None

**Example**:
```python
age = reasoner.property_value("john", "age")
# "25"
```

---

#### `instances_with_property(class_name, property_name)`

Get all instances of a class that have a specific property.

**Parameters**:
- `class_name` (str): Concept name
- `property_name` (str): Property name

**Returns**: QueryResultSet with bindings for `?instance` and `?value`

**Example**:
```python
# All persons with age
persons_with_age = reasoner.instances_with_property("Person", "age")
for p in persons_with_age:
    print(f"{p['?instance']} is {p['?value']} years old")
# john is 25 years old
# mary is 30 years old
```

---

#### `all_property_assertions(property_name)`

Get all assertions for a specific property.

**Parameters**:
- `property_name` (str): Property name

**Returns**: QueryResultSet with bindings for `?subject` and `?object`

**Example**:
```python
# All hasParent relationships
parents = reasoner.all_property_assertions("hasParent")
for p in parents:
    print(f"{p['?subject']} has parent {p['?object']}")
```

---

## Data Export

### `to_pandas()`

Convert query results to Pandas DataFrame.

**Parameters**: None (operates on QueryResultSet)

**Returns**: `pandas.DataFrame`

**Performance**: **387μs** (includes Pandas overhead)

**Example**:
```python
import pandas as pd

results = reasoner.pattern(
    ("?person", "type", "Person"),
    ("?person", "age", "?age")
)

df = results.to_pandas()
print(df)
#      person  age
# 0     john   25
# 1     mary   30
# 2    alice   22

# Use Pandas operations
adults = df[df['age'] >= 18]
mean_age = df['age'].mean()
```

**Performance Note**: Pandas conversion is slower than iteration (387μs vs 22μs). Only use when you need Pandas features.

---

### `to_arrow()`

Convert query results to Apache Arrow table (zero-copy).

**Parameters**: None

**Returns**: `pyarrow.Table`

**Performance**: **~100μs** (faster than Pandas, zero-copy transfer)

**Example**:
```python
import pyarrow as pa

results = reasoner.pattern(("?x", "type", "Person"))
table = results.to_arrow()

# Convert to Pandas with zero-copy
df = table.to_pandas(zero_copy_only=True)

# Use Arrow operations
filtered = table.filter(pa.compute.greater(table['age'], 18))
```

**Why Arrow?**
- **Zero-copy** data transfer
- **Columnar format** for analytics
- **Cross-language** compatibility (Python, R, Java, etc.)
- **Faster** than Pandas for large datasets

---

## SWRL Rules

### Loading SWRL Rules

SWRL rules are loaded via `load_ontology()` using the SWRL syntax:

```
⊢ antecedent → consequent
```

**Example**:
```python
reasoner = Reter()
reasoner.load_ontology("""
Person ⊑ᑦ ⊤
Adult ⊑ᑦ Person

// Define age property
age ⊑ᴰ ⊤

// SWRL Rule: Person with age >= 18 is Adult
⊢ Person（⌂x）∧ age（⌂x，⌂：a）∧ ：greaterThanOrEqual（⌂：a，18） → Adult（⌂x）

// Add instances
Person（john）
age（john，25）

Person（alice）
age（alice，16）
""")

reasoner.reason()

# Query adults
adults = reasoner.instances_of("Adult")
for a in adults:
    print(a['?x'])  # john (alice is excluded)
```

### SWRL Variables

- **Object variables**: `⌂x`, `⌂person`, `⌂parent`
- **Data variables**: `⌂：age`, `⌂：value`, `⌂：sum`

### SWRL Atoms

**Class Atom**:
```
Person（⌂x）  // ?x is a Person
```

**Object Property Atom**:
```
hasParent（⌂x，⌂y）  // ?x hasParent ?y
```

**Data Property Atom**:
```
age（⌂x，⌂：age）  // ?x age ?age
```

**Same Individual**:
```
﹦（⌂x，⌂y）  // ?x and ?y are the same
```

**Different Individuals**:
```
≠（⌂x，⌂y）  // ?x and ?y are different
```

### SWRL Built-ins

Built-in predicates for data comparisons and arithmetic:

**Comparison**:
```
：greaterThan（⌂：x，⌂：y）
：greaterThanOrEqual（⌂：x，⌂：y）
：lessThan（⌂：x，⌂：y）
：lessThanOrEqual（⌂：x，⌂：y）
：equal（⌂：x，⌂：y）
：notEqual（⌂：x，⌂：y）
```

**Arithmetic** (if implemented):
```
：add（⌂：sum，⌂：a，⌂：b）        // sum = a + b
：subtract（⌂：diff，⌂：a，⌂：b）   // diff = a - b
：multiply（⌂：prod，⌂：a，⌂：b）   // prod = a * b
：divide（⌂：quot，⌂：a，⌂：b）     // quot = a / b
```

**Example: Grandparent Rule**:
```python
reasoner.load_ontology("""
⊢ hasChild（⌂x，⌂y）∧ hasChild（⌂y，⌂z） → hasGrandchild（⌂x，⌂z）
""")
```

**Example: Adult Classification**:
```python
reasoner.load_ontology("""
⊢ Person（⌂x）∧ age（⌂x，⌂：a）∧ ：greaterThanOrEqual（⌂：a，18） → Adult（⌂x）
""")
```

---

## Advanced Features

### Incremental Reasoning

Reasoning is performed incrementally as facts are loaded:

```python
reasoner = Reter()

# Load initial ontology
reasoner.load_ontology("Person ⊑ᑦ Animal")

# Query
results1 = reasoner.pattern(("?x", "type", "Animal"))
list(results1)  # []

# Add new instance
reasoner.load_ontology("Person（john）")

# Query again - john is inferred to be Animal
results2 = reasoner.pattern(("?x", "type", "Animal"))
list(results2)  # ['john']
```

---

### Query Caching

Pattern queries are cached for better performance on repeated calls:

```python
# First call
results1 = reasoner.pattern(("?x", "type", "Person"))

# Second call with same pattern is faster
results2 = reasoner.pattern(("?x", "type", "Person"))
```

---

### Query Semantics

#### Snapshot Queries

QueryResultSet represents **snapshot at creation time**:

```python
results = reasoner.pattern(("?x", "type", "Person"))
# Snapshot created here

reasoner.load_ontology("Person（newPerson）")
# Snapshot unchanged

list(results)  # Does NOT include newPerson
```

#### Live Queries

Create **new QueryResultSet** for live results:

```python
def get_live_persons():
    return reasoner.pattern(("?x", "type", "Person"))

results1 = get_live_persons()
list(results1)  # ['john', 'mary']

reasoner.load_ontology("Person（bob）")

results2 = get_live_persons()  # Fresh query
list(results2)  # ['john', 'mary', 'bob']
```

---

## Performance Best Practices

### 1. Reuse Reasoner Instances

**Bad**:
```python
for ontology in ontologies:
    r = Reter()  # Expensive: creates new instance
    r.load_ontology(ontology)
    results = r.pattern(("?x", "type", "Person"))
```

**Good**:
```python
r = Reter()  # Create once
for ontology in ontologies:
    r.load_ontology(ontology)  # Load incrementally
    results = r.pattern(("?x", "type", "Person"))
```

### 2. Batch Fact Loading

**Bad**:
```python
for person in persons:
    reasoner.load_ontology(f"Person（{person}）")  # Many small updates
```

**Good**:
```python
ontology = "\n".join(f"Person（{person}）" for person in persons)
reasoner.load_ontology(ontology)  # Single batch update
```

### 3. Use Production Caching

**Reuse patterns**:
```python
# Cache production once
pattern = ("?x", "type", "Person")

# Reuse many times
for _ in range(1000):
    results = reasoner.pattern(pattern)  # Uses cached production
```

### 4. Avoid Unnecessary Pandas Conversion

**Bad**:
```python
results = reasoner.pattern(("?x", "type", "Person"))
df = results.to_pandas()  # 387μs overhead
for _, row in df.iterrows():  # Slow iteration
    print(row['?x'])
```

**Good**:
```python
results = reasoner.pattern(("?x", "type", "Person"))
for r in results:  # 22μs total, fast iteration
    print(r['?x'])
```

**When to use Pandas**: Only when you need Pandas operations (groupby, merge, plot, etc.)

### 5. Profile Before Optimizing

```python
import time

start = time.perf_counter()
results = reasoner.pattern(("?x", "type", "Person"))
list(results)
end = time.perf_counter()

print(f"Query time: {(end - start) * 1e6:.2f} μs")
```

---

## Error Handling

### Parsing Errors

```python
try:
    reasoner.load_ontology("Person ⊑ᑦ")  # Incomplete statement
except RuntimeError as e:
    print(f"Parse error: {e}")
    # Parse error: line 1:10 unexpected EOF, expecting concept expression
```

### Query Errors

```python
# Invalid variable names (must start with ?)
results = reasoner.pattern(("x", "type", "Person"))  # ❌ Should be "?x"

# Variables in results dict must match pattern
results = reasoner.pattern(("?person", "type", "Person"))
for r in results:
    print(r['?x'])  # ❌ KeyError: should be r['?person']
```

---

## Complete Example

```python
from reter import Reter

# Create reasoner
r = Reter()

# Load family ontology
r.load_ontology("""
// Classes
Person ⊑ᑦ ⊤
Adult ⊑ᑦ Person
Child ⊑ᑦ Person
¬≡ᑦ（Adult，Child）

// Properties
hasParent ⊑ᴿ hasRelative
hasChild ≡ᴿ hasParent⁻

// SWRL: hasGrandparent
⊢ hasParent（⌂x，⌂y）∧ hasParent（⌂y，⌂z） → hasGrandparent（⌂x，⌂z）

// Instances
Person（john）
Person（mary）
Person（alice）
hasParent（john，mary）
hasParent（mary，alice）

age（john，25）
age（mary，52）
age（alice，78）

// SWRL: Classify adults
⊢ Person（⌂x）∧ age（⌂x，⌂：a）∧ ：greaterThanOrEqual（⌂：a，18） → Adult（⌂x）
""")

# Ensure reasoning completes
r.reason()

# Query 1: Who are the adults?
adults = r.instances_of("Adult")
print("Adults:")
for a in adults:
    print(f"  {a['?x']}")
# Output:
#   john
#   mary
#   alice

# Query 2: Who are John's grandparents?
grandparents = r.pattern(
    ("john", "hasGrandparent", "?gp")
)
print("\nJohn's grandparents:")
for gp in grandparents:
    print(f"  {gp['?gp']}")
# Output:
#   alice

# Query 3: Family tree (all parent relationships)
family = r.pattern(
    ("?child", "hasParent", "?parent")
)
print("\nFamily tree:")
for f in family:
    print(f"  {f['?child']} -> {f['?parent']}")
# Output:
#   john -> mary
#   mary -> alice

# Export to Pandas
df = family.to_pandas()
print("\nAs DataFrame:")
print(df)
#    child parent
# 0   john   mary
# 1   mary  alice
```

---

## API Summary

### Core Methods

| Method | Purpose | Performance | Returns |
|--------|---------|-------------|---------|
| `Reter()` | Constructor | - | Reter instance |
| `load_ontology(text)` | Load DL statements | Incremental | None |
| `load_ontology_file(path)` | Load DL from file | Incremental | None |

### Query Methods

| Method | Purpose | Performance | Returns |
|--------|---------|-------------|---------|
| `pattern(*patterns)` | Pattern matching (main query method) | **22μs** | QueryResultSet |
| `instances_of(class)` | Template query | 35μs | QueryResultSet |
| `union(*queries)` | Union multiple queries | ~101μs | QueryResultSet |
| `property_path(...)` | Transitive closure queries | Varies | QueryResultSet |

### Helper Methods (Arrow-based)

| Method | Purpose | Performance | Returns |
|--------|---------|-------------|---------|
| `get_all_facts()` | Get all facts | ~10μs | pyarrow.Table |
| `get_instances(class)` | Get class instances | ~10μs | List[str] |
| `get_subsumers(class)` | Get superclasses | ~10μs | List[str] |
| `get_subsumed(class)` | Get subclasses | ~10μs | List[str] |
| `get_role_assertions(...)` | Get property assertions | ~10μs | List[tuple] |
| `related(subject, prop)` | Get related objects | ~25μs | QueryResultSet |
| `property_value(subject, prop)` | Get single value | ~25μs | str |
| `instances_with_property(...)` | Instances with property | ~30μs | QueryResultSet |
| `all_property_assertions(prop)` | All property assertions | ~30μs | QueryResultSet |

### REQL and DL Query Methods

RETER provides high-level query methods using REQL and Description Logic expressions:

| Method | Purpose | Returns |
|--------|---------|---------|
| `reql(query)` | Execute REQL SELECT query | pyarrow.Table |
| `reql_ask(query)` | Execute REQL ASK query (boolean check) | bool |
| `dl_query(expr)` | Execute DL expression query | pyarrow.Table |
| `dl_ask(expr)` | Check existence with DL expression | bool |

---

#### `reql(query_string)`

Execute a REQL SELECT query and return results as an Arrow table.

**Parameters**:
- `query_string` (str): REQL SELECT query

**Returns**: `pyarrow.Table` with query results

**Example**:
```python
# Basic SELECT query
result = r.reql("SELECT ?x WHERE { ?x type Person }")
print(result.to_pydict())
# Output: {'?x': ['Alice', 'Bob']}

# Multiple patterns (join)
result = r.reql('''
    SELECT ?x ?y WHERE {
        ?x type Person .
        ?x hasParent ?y
    }
''')

# UNION (disjunction)
result = r.reql('''
    SELECT ?x WHERE {
        { ?x type Person }
        UNION
        { ?x type Doctor }
    }
''')

# MINUS (negation)
result = r.reql('''
    SELECT ?x WHERE {
        ?x type Person .
        MINUS { ?x type Doctor }
    }
''')

# Result modifiers
result = r.reql('''
    SELECT DISTINCT ?x WHERE { ?x type Person }
    ORDER BY ?x
    LIMIT 10
    OFFSET 5
''')

# Convert to pandas
import pandas as pd
df = result.to_pandas()

# Use Arrow compute functions
import pyarrow.compute as pc
filtered = pc.filter(result, pc.field('?x') != 'bob')
```

**Supported REQL Features**:
- SELECT queries (ASK not supported, use `reql_ask()` instead)
- WHERE triple patterns
- UNION patterns
- MINUS patterns
- DISTINCT, ORDER BY, LIMIT, OFFSET
- FILTER (basic operators)

See [REQL Queries](03_reql.md) for details.

---

#### `reql_ask(query_string)`

Execute a REQL ASK query and return a boolean result indicating whether the pattern exists.

**Parameters**:
- `query_string` (str): REQL ASK query (or SELECT query)

**Returns**: `bool` - True if pattern exists, False otherwise

**Note**: Since the REQL parser currently only supports SELECT queries, this method automatically converts ASK queries to SELECT queries internally. You can also pass a SELECT query directly.

**Example**:
```python
# ASK query (automatically converted to SELECT)
exists = r.reql_ask("ASK { ?x type Person }")
print(exists)  # True or False

# Or use SELECT query directly
exists = r.reql_ask("SELECT ?x WHERE { ?x type Person }")
print(exists)  # True or False

# Complex check with conjunction
exists = r.reql_ask('''
    ASK {
        ?x type Person .
        ?x type Doctor
    }
''')
```

---

#### `dl_query(dl_expression)`

Query using Description Logic expression syntax. Supports atomic concepts, conjunction (⊓), disjunction (⊔), and negation (¬).

**Parameters**:
- `dl_expression` (str): DL expression using Unicode operators

**Returns**: `pyarrow.Table` with column `?x0` containing matching individuals

**Example**:
```python
# Atomic concept
result = r.dl_query("Person")
print(result.to_pydict())
# Output: {'?x0': ['Alice', 'Bob']}

# Conjunction (AND)
result = r.dl_query("Person ⊓ Doctor")
print(result.to_pydict())
# Output: {'?x0': ['Alice']}

# Disjunction (OR)
result = r.dl_query("Person ⊔ Doctor")
print(result.to_pydict())
# Output: {'?x0': ['Alice', 'Bob', 'Charlie']}

# Negation (NOT)
result = r.dl_query("¬Doctor")
print(result.to_pydict())
# Output: {'?x0': ['Bob', 'Charlie']}

# Role restrictions (existential)
result = r.dl_query("∃ hasChild ․ Doctor")
# All individuals that have a child who is a Doctor

# Convert to list
individuals = result.column(0).to_pylist()
```

**Supported DL Operators**:
- Atomic concepts: `Person`, `Doctor`
- Conjunction: `A ⊓ B` (AND)
- Disjunction: `A ⊔ B` (OR)
- Negation: `¬A` (NOT)
- Existential restriction: `∃ R ․ C` (individuals with R-relation to C)
- Value restriction: `∀ R ․ C` (all R-relations go to C)

The DL expression is translated to REQL internally and executed.

---

#### `dl_ask(dl_expression)`

Check existence using a Description Logic expression. Returns True if any individuals match the expression.

**Parameters**:
- `dl_expression` (str): DL expression using Unicode operators

**Returns**: `bool` - True if concept has instances, False otherwise

**Example**:
```python
# Check if Person ⊓ Doctor exists
exists = r.dl_ask("Person ⊓ Doctor")
print(exists)  # True or False

# Check non-existent concept
exists = r.dl_ask("Robot")
print(exists)  # False

# Check complex expression
exists = r.dl_ask("Person ⊓ ¬Doctor")
print(exists)  # True if any non-doctor person exists
```

---

### Data Export

| Method | Purpose | Performance | Returns |
|--------|---------|-------------|---------|
| `to_pandas()` | Convert to DataFrame | 387μs | pandas.DataFrame |
| `to_arrow()` | Convert to Arrow | ~100μs | pyarrow.Table |
| `get_inferred_facts()` | Get only inferred facts | ~15μs | pyarrow.Table |

---

## Next Steps

- **[Grammar Reference](01_grammar.md)** - Description Logic syntax
- **[REQL Queries](03_reql.md)** - SPARQL-like query language
- **[Syntax Variants](04_syntax_variants.md)** - Unicode vs ASCII syntax

---

**Last Updated**: December 2025
