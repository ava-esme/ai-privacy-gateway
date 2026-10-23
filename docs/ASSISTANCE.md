# ASSISTANCE.md

## Purpose

This document records important assistance used during the development of the AI Privacy Gateway.

For each important suggestion, the following are recorded:

- source of assistance;
- suggestion or guidance received;
- decision made;
- how the suggestion was verified; and
- final result.

Only significant assistance that affected the design, implementation, testing, or documentation is included.

---

## Entry 1 - Programming Language Selection

### Source

ChatGPT

### Topic

Programming language selection

### Suggestion

Python was suggested as the implementation language because the project relies heavily on:

- text processing;
- regular expressions;
- JSON handling;
- automated testing; and
- future AI-related integration.

TypeScript was suggested as a realistic alternative because it provides stronger static type checking and can be used for both front-end and back-end development.

### Decision

Accepted.

Python was selected as the implementation language.

### Verification

The decision was checked by confirming that Python provides:

- `re` for regular-expression matching;
- `json` for JSON parsing and generation;
- dictionaries for placeholder mappings; and
- `unittest` for automated tests.

A Tech Spike was also completed to verify that the installed Python runtime could read and print text correctly.

### Result

Python was kept as the project language and was successfully used to implement the Milestone 2 prototype.

---

## Entry 2 - Sensitive-Information Detection Strategy

### Source

ChatGPT

### Topic

Detection design

### Suggestion

Use two different detection methods:

- exact matching from local synthetic term lists for names and physical addresses;
- structured regular-expression patterns for email addresses and phone numbers.

### Decision

Accepted.

The implemented Milestone 2 categories are:

- `NAME`
- `ADDRESS`
- `EMAIL`
- `PHONE`

Names and addresses use exact matching.

Emails and phone numbers use regular expressions.

### Verification

The `detector.py` file was run directly using:

```bash id="8cnui9"
python detector.py
```

The detector correctly identified:

- Jane Smith as `NAME`;
- 123 Example Street, Sampletown, GA 30000 as `ADDRESS`;
- jane.smith@example.com as `EMAIL`; and
- 478-555-1234 as `PHONE`.

The detector also correctly found repeated occurrences of the same name.

### Result

Accepted and implemented.

---

## Entry 3 - Request-Specific Placeholder Format

### Source

Course project handbook and ChatGPT

### Topic

Placeholder design

### Suggestion

Use request-specific placeholders in the form:

```text id="y5x0dl"
[[request_id:CATEGORY:index]]
```

Examples:

```text id="o7c48v"
[[r1:NAME:1]]
[[r1:EMAIL:1]]
[[r1:PHONE:1]]
[[r1:ADDRESS:1]]
```

The request ID helps associate placeholders with the request that created them.

### Decision

Accepted.

The placeholder format was added to the design and implementation.

### Verification

The masking component was tested with repeated and different sensitive values.

Example result:

```text id="ee7bxj"
[[r1:NAME:1]] lives at [[r1:ADDRESS:1]].
[[r1:NAME:1]] has 3 years of Python experience.
```

The repeated value `Jane Smith` reused:

```text id="nnne4s"
[[r1:NAME:1]]
```

A different person, `John Davis`, received:

```text id="sqejnj"
[[r1:NAME:2]]
```

### Result

Accepted and implemented successfully.

---

## Entry 4 - Request-Local Placeholder Mapping

### Source

ChatGPT

### Topic

Masking and local state

### Suggestion

Maintain the placeholder mapping locally using data structures that allow:

- placeholder-to-original-value lookup; and
- repeated values to reuse an existing placeholder.

Example:

```text id="9f726y"
[[r1:NAME:1]] -> Jane Smith
```

### Decision

Accepted.

The masker stores local mappings and does not include them in the provider request or normal JSON output.

### Verification

Running:

```bash id="wza2be"
python masker.py
```

produced a local map containing:

```text id="wvhz1p"
[[r1:NAME:1]] -> Jane Smith
[[r1:ADDRESS:1]] -> 123 Example Street, Sampletown, GA 30000
[[r1:EMAIL:1]] -> jane.smith@example.com
[[r1:PHONE:1]] -> 478-555-1234
[[r1:NAME:2]] -> John Davis
```

The provider response was also checked and contained only placeholders rather than the original sensitive values.

### Result

Accepted and implemented.

---

## Entry 5 - Deterministic Offline Mock Provider

### Source

ChatGPT

### Topic

Provider simulation

### Suggestion

Use a deterministic offline mock provider for Milestone 2 rather than a live AI service.

The mock provider should:

- preserve masked placeholders;
- return predictable output;
- support simulated invalid-placeholder responses; and
- support simulated provider failure.

### Decision

Accepted.

The following mock modes were implemented:

- `normal`
- `unknown_placeholder`
- `malformed_placeholder`
- `provider_error`

### Verification

Running:

```bash id="ysuq6k"
python mock_provider.py
```

produced:

- a normal response with valid placeholders;
- an unknown placeholder such as `[[r1:NAME:999]]`; and
- a malformed placeholder such as `[[r1:NAME]]`.

These responses were later used to test validation behavior.

### Result

Accepted and implemented.

---

## Entry 6 - Provider Response Validation

### Source

ChatGPT

### Topic

Placeholder validation

### Suggestion

Validate provider responses before restoring any sensitive values.

The validator should distinguish between:

- a valid issued placeholder;
- a valid-looking but unknown placeholder; and
- malformed reserved placeholder syntax.

### Decision

Accepted.

The following controlled errors were implemented:

- `UNKNOWN_PLACEHOLDER`
- `INVALID_PLACEHOLDER`

### Verification

Running:

```bash id="iui0xk"
python validator.py
```

produced:

```text id="ivtl1g"
VALID RESPONSE
Validation successful.
```

For:

```text id="m6txcs"
[[r1:NAME:999]]
```

the result was:

```text id="b9p4qh"
UNKNOWN_PLACEHOLDER
```

For:

```text id="u2oiys"
[[r1:NAME]]
```

the result was:

```text id="yxsg7f"
INVALID_PLACEHOLDER
```

### Result

Accepted and implemented.

---

## Entry 7 - Validate Before Restoration

### Source

ChatGPT

### Topic

Restoration safety

### Suggestion

The restoration component should call the validator before replacing any placeholders.

If validation fails, no sensitive values should be restored.

### Decision

Accepted.

`restorer.py` validates the provider response before replacing placeholders with original local values.

### Verification

Running:

```bash id="g38nfb"
python restorer.py
```

showed that:

- valid placeholders were restored;
- unknown placeholders produced `UNKNOWN_PLACEHOLDER`; and
- malformed placeholders produced `INVALID_PLACEHOLDER`.

No restored final output was produced for invalid provider responses.

### Result

Accepted and implemented.

---

## Entry 8 - JSON I/O Contract

### Source

ChatGPT

### Topic

Input and output contract

### Suggestion

Use JSON for both requests and responses.

Recommended input format:

```json id="jx2i5b"
{
  "request_id": "r1",
  "text": "resume text"
}
```

Recommended successful output format:

```json id="ia3e7f"
{
  "status": "ok",
  "request_id": "r1",
  "masked_text": "...",
  "provider_response": "...",
  "output": "..."
}
```

Recommended controlled errors include:

- `INVALID_JSON`
- `INVALID_REQUEST`
- `RESERVED_PLACEHOLDER_IN_INPUT`
- `INVALID_PLACEHOLDER`
- `UNKNOWN_PLACEHOLDER`
- `PROVIDER_ERROR`

### Decision

Accepted with the fields documented in `DESIGN.md`.

### Verification

The full pipeline was executed successfully with:

```bash id="6vlf3a"
python pipeline.py
```

The output followed the documented JSON structure.

The command-line entry point was also tested with:

```bash id="zu1b1p"
python main.py
```

and produced the expected JSON response.

### Result

Accepted and implemented.

---

## Entry 9 - Automated Acceptance Tests

### Source

ChatGPT

### Topic

Milestone 2 testing

### Suggestion

Convert the Milestone 1 acceptance cases into automated tests and add additional controlled-error cases.

The suggested tests included:

- normal input;
- repeated sensitive values;
- no sensitive information;
- unknown placeholder;
- malformed placeholder;
- different entities;
- reserved placeholder input;
- provider failure;
- invalid JSON; and
- missing required field.

### Decision

Accepted.

Ten automated tests were added to:

```text id="gx440z"
tests/test_pipeline.py
```

### Verification

The test suite was run using:

```bash id="u6ybcx"
python -m unittest discover -s tests -v
```

Observed result:

```text id="i7ccu2"
Ran 10 tests in 0.003s

OK
```

All 10 tests passed.

### Result

Accepted and verified through automated execution.

---

## Entry 10 - Documentation Organization

### Source

Course project handbook and ChatGPT

### Topic

Project documentation

### Suggestion

Keep the project documentation separated by purpose:

- `DESIGN.md` for architecture, requirements, language choice, state, prompt, and design decisions;
- `EVALUATION.md` for planned and executed tests, results, failures, and limitations;
- `USER_GUIDE.md` for running the program, supported formats, warnings, and troubleshooting;
- `ASSISTANCE.md` for significant development assistance and verification; and
- `README.md` for project scope, setup, commands, and copyable examples.

### Decision

Accepted.

The existing Milestone 1 documents were updated rather than replaced with new milestone-specific reports.

### Verification

Each document was reviewed against the implemented Milestone 2 behavior to ensure that commands, examples, error codes, supported categories, and limitations matched the actual program.

### Result

Accepted and used as the documentation structure for Milestone 2.

---

## Summary

AI assistance was used primarily for:

- planning the implementation;
- selecting data structures;
- designing placeholder behavior;
- defining the JSON contract;
- writing initial code drafts;
- designing validation logic;
- creating automated tests; and
- organizing project documentation.

Suggestions were not treated as automatically correct.

Each major implementation suggestion was checked by running the related component or automated test suite.

At the end of Milestone 2:

- the complete pipeline runs successfully;
- all 10 automated tests pass; and
- the documentation reflects the implemented prototype.