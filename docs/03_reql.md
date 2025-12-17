# REQL Query System

REQL (RETE Query Language) is a SPARQL-inspired query language for querying the reasoner.

## Basic Queries

### SELECT Query

```python
from reter import Reter

r = Reter()
r.load_ontology("""
Person（alice）
Person（bob）
Doctor（alice）
hasAge（alice，30）
hasAge（bob，25）
""")

# Basic SELECT
result = r.reql("SELECT ?x WHERE { ?x type Person }")
print(result.to_pandas())
```

### Multiple Patterns (Join)

```python
# Find persons and their ages
result = r.reql("""
    SELECT ?x ?age WHERE {
        ?x type Person .
        ?x hasAge ?age
    }
""")
```

### ASK Query

```python
# Check if any person exists
result = r.reql("ASK WHERE { ?x type Person }")
exists = result['result'][0].as_py()  # True or False
```

### DESCRIBE Query

```python
# Get all facts about a resource
result = r.reql("DESCRIBE alice")
print(result.to_pandas())
```

---

## Query Modifiers

### DISTINCT

```python
result = r.reql("""
    SELECT DISTINCT ?x WHERE {
        ?x type Person
    }
""")
```

### ORDER BY

```python
result = r.reql("""
    SELECT ?x ?age WHERE {
        ?x type Person .
        ?x hasAge ?age
    }
    ORDER BY ?age
""")
```

### LIMIT and OFFSET

```python
result = r.reql("""
    SELECT ?x WHERE { ?x type Person }
    LIMIT 10
    OFFSET 5
""")
```

---

## Advanced Patterns

### UNION (OR)

```python
# Persons OR Doctors
result = r.reql("""
    SELECT ?x WHERE {
        { ?x type Person }
        UNION
        { ?x type Doctor }
    }
""")
```

### MINUS (NOT)

```python
# Persons who are NOT Doctors
result = r.reql("""
    SELECT ?x WHERE {
        ?x type Person .
        MINUS { ?x type Doctor }
    }
""")
```

### FILTER

```python
# Persons older than 18
result = r.reql("""
    SELECT ?x ?age WHERE {
        ?x type Person .
        ?x hasAge ?age
        FILTER (?age > 18)
    }
""")
```

---

## Working with Results

### Convert to Pandas

```python
result = r.reql("SELECT ?x ?age WHERE { ?x hasAge ?age }")
df = result.to_pandas()
print(df)
```

### Convert to Dictionary

```python
result = r.reql("SELECT ?x WHERE { ?x type Person }")
data = result.to_pydict()
# {'?x': ['alice', 'bob']}
```

### Filter with Arrow Compute

```python
import pyarrow.compute as pc

result = r.reql("SELECT ?x ?age WHERE { ?x hasAge ?age }")
adults = result.filter(pc.greater(result['?age'], 18))
```

---

## Feature Support

| Feature | Status |
|---------|--------|
| SELECT | Supported |
| ASK | Supported |
| DESCRIBE | Supported |
| WHERE | Supported |
| FILTER | Basic operators |
| UNION | Supported |
| MINUS | Supported |
| ORDER BY | Supported |
| LIMIT/OFFSET | Supported |
| DISTINCT | Supported |
| OPTIONAL | Planned |
| GROUP BY | Planned |

---

## Error Handling

```python
try:
    result = r.reql("SELECT ?x WHERE { invalid syntax }")
except RuntimeError as e:
    print(f"Query error: {e}")
```

---

## See Also

- [API Reference](02_api_reference.md) - Python API documentation
- [Grammar Reference](01_grammar.md) - Description Logic syntax
- [Syntax Variants](04_syntax_variants.md) - Unicode vs ASCII syntax

---

**Last Updated**: December 2025
