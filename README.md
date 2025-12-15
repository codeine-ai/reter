# RETER

High-performance Description Logic reasoner with C++ RETE engine.

## Installation

Install directly from GitHub:

```bash
pip install git+https://github.com/codeine-ai/reter.git --find-links https://github.com/codeine-ai/reter/raw/main/wheels/
```

Or clone and install locally:

```bash
git clone https://github.com/codeine-ai/reter.git
cd reter
pip install . --find-links ./wheels/
```

## Quick Start

```python
from reter import Reter

# Create reasoner
r = Reter()

# Load ontology
r.load_ontology("""
Person ⊑ᑦ Animal
Student ⊑ᑦ Person
Person（John）
Student（Alice）
""")

# Query instances
people = r.instances_of("Person")
for p in people:
    print(p["?x"])

# REQL queries
result = r.reql("SELECT ?x WHERE { ?x type Person }")
print(result.to_pandas())
```

## Features

- Fast OWL 2 RL reasoning using C++ RETE algorithm
- Description Logic parser (C++ implementation)
- SWRL rule support
- Query interface with Arrow integration
- Source tracking for incremental ontology loading
- Python, JavaScript, C#, and C++ code analysis

## License

MIT
