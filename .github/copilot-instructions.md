# Copilot Instructions

## Development Tooling

- `pytest` - Testing framework (development dependency)
- `black`
- `isort`
- `mdformat`
- `ruff`
- `pytest`

## Testing Strategy

### Testing Conventions

- Use `pytest` with descriptive test names: `test_slug_generation_handles_unicode_chars()`
- Fixture for sample content: `sample_post_with_tags`, `sample_config`
- Test data in `tests/fixtures/` directory
- One assertion per test when possible for clarity

## Error Handling Approach

### Fail Fast Scenarios (exit immediately)

- Missing or invalid configuration
- Missing or invalid required static files

### Graceful Handling (log warning, continue)

- Missing optional front matter fields (tags, description)
- Invalid dates (skip post or use filename date)
- Missing static files referenced in content

### Error Message Guidelines

- Include file path and line number when possible
- Suggest specific fixes: "Add 'title' field to front matter"
- Use consistent format: "Error in content/posts/my-post.md: Missing required
  field 'date'"

## Coding Standards

### 0. Guiding Ethos

Code should invite understanding.\
Good software is not just functional -- it is *legible thought*.\
Generate and refactor Python code as though explaining an idea to a future
collaborator of good will and limited time.

### 1. AI Behavior Preamble

When writing or refactoring code:

- **Primary Objective:** produce Python that is *clear, minimal, and
  conceptually deep*.
- **Prioritize** long-term readability over short-term cleverness.
- **Avoid** over-generalization, "Clean Code fragmentation," or needless
  patterns.
- **Balance** explicitness with rhythm -- the code should read naturally in
  Python's idiom.
- When rules conflict, follow this hierarchy:
  1. **Clarity of intent**
  1. **Simplicity of structure**
  1. **Depth of abstraction**
  1. **Harmony with the surrounding codebase**

### 2. Structural Rules

- Each module should embody a *single, coherent idea*.
- Prefer **deep modules** (simple interface, rich implementation) over thin
  wrappers.
- **Hide complexity, not meaning** -- interfaces should name the problem
  domain, not internal mechanics.
- Avoid "manager," "util," or "helper" suffixes; express intent.
- Let architecture *emerge* through iteration, not anticipation.

### 3. Functions and Classes

- Keep functions short but **complete in thought**; don't explode logic into
  fragments.
- Function names are **verbs**; class names are **nouns**.
- Classes should clarify boundaries, not multiply them.
- Use `@dataclass` for simple data aggregates; no inheritance unless it pays
  for itself.
- Favor composition over hierarchy.

### 4. Pythonic Practices

- Follow **PEP 8**, but value **clarity over conformance**.
- **Use pure ASCII** in code and documentation when possible - avoid Unicode
  symbols, fancy quotes, em-dashes, etc.
- Prefer:
  - `with` for resource handling
  - f-strings for formatting
  - comprehensions for obvious collection transforms
  - `enumerate`, `zip`, unpacking over index loops
- Return early; flatten control flow.
- Avoid cleverness disguised as terseness.

### 5. Documentation and Comments

- Docstrings describe *purpose and contract*, not implementation.
- Inline comments explain *why this is hard*, not *what this does*.
- If a comment paraphrases the code, delete it.
- If a comment captures reasoning, preserve it.
- **Character encoding**: Use pure ASCII characters in code, comments, and
  documentation when possible. Replace Unicode symbols with ASCII equivalents:
  - Use `->` instead of `->`
  - Use `--` instead of `--` (em-dash)
  - Use regular quotes `"` instead of smart quotes `""`
  - Use `...` instead of `...` (ellipsis character)

### 6. Testing

- Write tests that reveal **behavior**, not internals.
- Use **pytest** with descriptive names and parametrization.
- Keep tests **fast, isolated, and explicit**.
- A test should read like an example of correct reasoning.

### 7. Refactoring Guidance

When improving code:

- Simplify public interfaces first; internal cleanup follows.
- Inline trivial abstractions; extract only when repeated or conceptually distinct.
- Rename freely for clarity -- words cost less than confusion.
- Prefer deletion to addition when removing noise clarifies intent.
- Never optimize before measuring.
- Preserve correctness above aesthetic purity.

### 8. Review Checklist

Before accepting or generating code:

1. Can the purpose be explained in one sentence?
1. Is the naming intentional and domain-aligned?
1. Is complexity hidden behind a simple surface?
1. Could a new contributor follow the flow without external context?
1. Would this design make the *next change easier*?

### 9. Synthesis

> **Goal:** Clean + Pythonic + Deep.\
> **Formula:** clarity x intent x simplicity x encapsulated complexity.\
> **Motto:** *Write code that respects the reader.*
