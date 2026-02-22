# Sift Language Compiler

Sift is a declarative Domain-Specific Language (DSL) designed to describe structured web-scraping workflows.

Rather than writing imperative scraping code, users describe **what** they want to extract using targets, action blocks, and filter expressions. Sift handles parsing, AST generation, and compilation into an intermediate representation (IR) suitable for execution or further compilation (e.g., to bytecode).

---

# Overview

A Sift script:

1. Defines **targets** (URLs)
2. Defines **action blocks** per target
3. Uses `extract where` or `extract from ... where`
4. Expresses filter logic using:
   - `tag`
   - `attribute`
   - `text`
   - `and`, `or`, `not`
   - grouping with parentheses

## Compilation Pipeline

```
Raw .sift file
    ↓
HighLevelGrammar (Lark)
    ↓
HighLevelTree
    ↓
ScriptTree (AST)
    ↓
IntermediateRepresentation (IR)
    ↓
(Optional) Bytecode
```

---

# Installation

## Requirements

- Python 3.10+
- `lark`
- `lark_cython`

## Install Dependencies

```bash
pip install lark lark-cython
```

---

# Quick Start

```python
from api.language_api.script_processor import ScriptProcessor

processor = ScriptProcessor("example.sift")
ast, ir = processor.parse()

print(ast)
print(ir)
```

---

# Project Architecture

## 1. Script Entry Point

`ScriptProcessor` is the main API interface.

**File:** `script_processor.py`

### Responsibilities

- Validates script input
- Parses content into `ScriptTree`
- Compiles AST into `IntermediateRepresentation`
- Optionally generates bytecode

---

## 2. Script Abstraction Layer

**File:** `script_representations.py`

### ScriptObject

Abstract base class for script representations.

Supported types:

- `File` – `.sift` files
- `Message` – in-memory script payloads

### Responsibilities

- Validation
- ID management
- Structured metadata handling

---

## 3. Parsing System

### Parser Interface

**File:** `parser.py`

```python
Parser(script_content).parse_content_to_tree()
```

The `Parser`:

- Uses `HighLevelTree`
- Produces a fully-typed `ScriptTree` AST

---

### High-Level AST Stage

**File:** `trees.py`

`HighLevelTree`:

- Parses grammar output
- Validates structure
- Extracts:
  - Target mappings
  - Action blocks

This separates raw grammar parsing from structured AST construction.

---

### ScriptTree (Primary AST)

**File:** `trees.py`

Represents:

```python
ScriptTree(
    targets: Dict[str, str],
    action_blocks: List[ActionBlock]
)
```

Each `ActionBlock` contains:

- Target alias
- List of `Action` objects

---

## 4. Grammar System

**Files:**
- `grammars.py`
- `utils.py`

Sift uses **Lark (LALR parser)** with three grammars:

- `HIGH_LEVEL` – Script structure
- `ACTION_BLOCK` – Action parsing
- `FILTER` – Filter expressions

### Grammar Architecture

- `GrammarContainer`
- `SyntaxProcessor`
- `GrammarHandler`
- `GenericGrammar`
- `GenericTransformer`

This abstraction:

- Converts grammar definitions to Lark grammar strings
- Parses script content
- Transforms parse trees into dictionary representations

---

# Filter System

**File:** `filter.py`

The `Filter` class represents:

- Logical operators (`and`, `or`, `not`)
- Atomic filters:
  - `tag`
  - `attribute`
  - `text`
- Nested expressions

## Example DSL

```sift
extract where (tag "div" and attribute "class":"main") -> result
```

## Internal Processing Steps

1. Regex extracts metadata:
   - `from_alias`
   - `raw_filter`
   - `assignment`
2. `FilterGrammar` parses condition
3. Recursive builder constructs filter tree
4. Tree supports:
   - Traversal
   - Validation
   - Pretty printing
   - ASCII tree drawing

---

# Action System

## Base Action

**File:** `action.py`

All actions:

- Inherit from `Action`
- Implement `_classify`
- Implement `pretty_print`
- Register via plugin registry

---

## ActionBlock

**File:** `action_block.py`

Responsible for:

- Parsing raw block content
- Classifying each statement
- Instantiating correct `Action` subclass
- Using registry-based plugin resolution

---

# Intermediate Representation (IR)

**File:** `intermediate_representation.py`

IR converts AST → executable instruction model.

## IntermediateRepresentation

```python
IntermediateRepresentation(
    identifier: str,
    instruction_list: List[Instruction]
)
```

## Instruction

Each instruction contains:

- URL
- Alias
- Operations

Operations are generated via registry lookups based on `ActionType`.

---

# Bytecode System

**File:** `compiler.py`

Optional compilation layer for execution engines.

## OpCode Examples

- CHECK_TAG
- CHECK_ATTRIBUTE
- CHECK_TEXT
- LOGICAL_AND
- LOGICAL_OR
- LOGICAL_NOT
- STORE_ALIAS
- LOAD_ALIAS
- PUSH_LITERAL
- JUMP_IF_FALSE
- CALL

`FilterBytecode` compiles JSON IR into stack-based instructions.

---

# Logical Operators & HTML Properties

**File:** `enums.py`

## Supported Logical Operators

- `and`
- `or`
- `not`
- `any`

## Supported Property Types

- `tag`
- `attribute`
- `text`

---

# Error Handling

**File:** `internal_exception.py`

Structured exception hierarchy:

- InternalParseError
- GrammarHandlerError
- TransformerParseError
- Action errors
- File validation errors

Provides detailed debugging context including:

- File
- Class
- Method
- Reason

---

# Example Script

```sift
targets = [
    google: "https://google.com"
]

google:
{
    extract where tag "div" and attribute "class":"main" -> result;
}
```

---

# Extending Sift

## Add a New Action Plugin

1. Create a subclass of `Action`
2. Implement:
   - `_classify`
   - `pretty_print`
3. Register via registry
4. Implement IR generator via `Operation.register_op`

---

# Design Principles

- Declarative over imperative
- Strong AST typing
- Multi-stage compilation
- Pluggable action system
- Clear separation:
  - Grammar parsing
  - AST structuring
  - IR construction
  - Execution layer

---

# Future Improvements

- Complete execution engine
- JavaScript rendering support
- Bot-detection mitigation layer
- Distributed scraping runtime
- Static type validation layer

---

# Author

Kane Cleveland  
Sift Language & Compiler Project

---

# License

MIT License
