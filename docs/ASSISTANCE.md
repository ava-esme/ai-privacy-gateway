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

Python was kept as the project language and was successfully used through Milestone 3.

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

The implemented sensitive-information categories are:

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

Use a deterministic offline mock provider rather than requiring a live AI service.

The mock provider should:

- preserve masked placeholders;
- return predictable output;
- support simulated invalid-placeholder responses; and
- support simulated provider failure.

### Decision

Accepted.

The initial mock modes included:

- `normal`
- `unknown_placeholder`
- `malformed_placeholder`
- `provider_error`

Milestone 3 later added:

- `foreign_placeholder`
- `missing_placeholder`
- `modified_placeholder`
- `malformed_response`
- `provider_timeout`

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

Recommended controlled errors initially included:

- `INVALID_JSON`
- `INVALID_REQUEST`
- `RESERVED_PLACEHOLDER_IN_INPUT`
- `INVALID_PLACEHOLDER`
- `UNKNOWN_PLACEHOLDER`
- `PROVIDER_ERROR`

Milestone 3 later added:

- `INVALID_POLICY`
- `FOREIGN_REQUEST_PLACEHOLDER`
- `MALFORMED_PROVIDER_RESPONSE`
- `PROVIDER_TIMEOUT`

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

## Entry 11 - MASK / REMOVE Policy Design

### Source

Course project handbook and ChatGPT

### Topic

Milestone 3 category-policy behavior

### Suggestion

Separate detection from privacy policy.

The detector should decide which sensitive values are present, while a separate policy component should decide whether each category is:

- `MASK`; or
- `REMOVE`.

Missing category rules should default to `MASK`.

Invalid categories or unsupported policy values should produce a controlled error rather than continuing.

### Decision

Accepted.

A separate `policy.py` module was implemented.

Supported policy values are:

- `MASK`
- `REMOVE`

Missing category rules default to:

```text
MASK
```

Invalid policy input returns:

```text
INVALID_POLICY
```

### Verification

The policy behavior was checked manually and through the automated test suite.

The tests verified:

- normal MASK behavior;
- REMOVE behavior;
- missing policies defaulting to MASK; and
- invalid policy input.

Example invalid policy:

```json
{"NAME":"HIDE"}
```

produced:

```text
INVALID_POLICY
```

### Result

Accepted and verified through automated execution.

---

## Entry 12 - RequestMapping and Cross-Request Isolation

### Source

Course project handbook and ChatGPT

### Topic

Request-local state and mapping lifetime

### Suggestion

Move request-local placeholder state into a dedicated mapping object.

Each request should have its own mapping, and the mapping should support:

- placeholder -> original value lookup;
- `(category, value)` -> placeholder lookup;
- repeated-value reuse;
- per-category indexing; and
- explicit cleanup after processing.

A placeholder created for one request must not be authorized in another request.

### Decision

Accepted.

A dedicated `RequestMapping` class was implemented in:

```text
mapping.py
```

Mappings are created per request and cleared after processing.

### Verification

Independent request behavior was tested using different request IDs.

For example:

```text
r13 -> [[r13:NAME:1]]
r14 -> [[r14:NAME:1]]
```

The second request did not recognize the first request's placeholder.

The automated suite also verified direct mapping cleanup and pipeline cleanup.

Foreign-request placeholders produced:

```text
FOREIGN_REQUEST_PLACEHOLDER
```

### Result

Accepted and verified.

---

## Entry 13 - Deterministic Overlap Resolution

### Source

Course project handbook and ChatGPT

### Topic

Detection overlap behavior

### Suggestion

Resolve overlapping detections deterministically so the same input always produces the same accepted matches.

Suggested rules:

1. Earlier starting position wins.
2. If detections begin at the same position, the longer match wins.
3. If start position and length are equal, use category priority.
4. Discard later candidates that overlap an already accepted detection.

### Decision

Accepted.

The detector was updated to use deterministic overlap handling.

Category priority was defined as:

1. `EMAIL`
2. `PHONE`
3. `ADDRESS`
4. `NAME`

### Verification

Manual detector tests and automated tests confirmed:

- the longer same-start match wins;
- the earlier-starting match wins; and
- the behavior is reproducible.

### Result

Accepted and implemented.

---

## Entry 14 - Provider Failure and Response Simulation

### Source

Course project handbook and ChatGPT

### Topic

Provider failure handling

### Suggestion

Expand the offline mock provider so the gateway can test more realistic response failures without using a live API.

The provider should simulate:

- foreign-request placeholders;
- missing placeholders;
- modified placeholders;
- malformed non-text responses;
- provider errors; and
- provider timeouts.

The gateway should never send an unmasked fallback after provider failure.

### Decision

Accepted.

The mock provider was expanded with the required Milestone 3 failure modes.

### Verification

The provider modes were exercised manually and through automated tests.

Verified outcomes included:

```text
FOREIGN_REQUEST_PLACEHOLDER
MALFORMED_PROVIDER_RESPONSE
PROVIDER_ERROR
PROVIDER_TIMEOUT
```

The missing-placeholder case completed without restoring the omitted value.

The modified-placeholder case produced:

```text
UNKNOWN_PLACEHOLDER
```

No unmasked fallback was used.

### Result

Accepted and verified.

---

## Entry 15 - Expanded Milestone 3 Automated Test Suite

### Source

Course project handbook and ChatGPT

### Topic

Milestone 3 testing

### Suggestion

Expand the existing automated tests to cover the Milestone 3 requirements, including:

- overlap behavior;
- MASK and REMOVE;
- default policies;
- invalid policies;
- foreign placeholders;
- request isolation;
- mapping cleanup;
- provider timeout;
- malformed provider responses;
- missing placeholders; and
- modified placeholders.

### Decision

Accepted.

The automated suite was expanded from 10 tests to 22 tests.

### Verification

The final test command was:

```bash
python -m unittest discover -s tests -v
```

Observed result:

```text
Ran 22 tests in 0.009s

OK
```

All 22 tests passed.

### Result

Accepted and verified through automated execution.

---

## Entry 16 - Quantitative Detection Evaluation

### Source

Course project handbook and ChatGPT

### Topic

Detection metrics and privacy-leak evaluation

### Suggestion

Create a separate labeled evaluation for detection quality.

For each synthetic case, compare expected sensitive-value occurrences with actual detections and report:

- true positives;
- false positives;
- false negatives;
- precision;
- recall; and
- protected-value occurrences that remain in the outbound payload.

### Decision

Accepted.

A separate evaluation script was created:

```text
evaluation_metrics.py
```

### Verification

The script was run with:

```bash
python evaluation_metrics.py
```

Overall observed result:

```text
TP: 10
FP: 0
FN: 1
Precision: 1.000
Recall: 0.909
Outbound privacy leaks: 1
```

The one false negative and leak came from the deliberately unsupported phone format:

```text
(478) 555-0199
```

Supported labeled cases produced zero outbound leaks.

### Result

Accepted and documented in `EVALUATION.md`.

---

## Entry 17 - Prompt Comparison

### Source

Course project handbook and ChatGPT

### Topic

Prompt usefulness evaluation

### Suggestion

Compare two prompt versions using the same three masked synthetic resume cases.

Evaluate each response for:

- usefulness;
- inclusion of required information;
- output format;
- correct placeholder preservation; and
- unsupported or invented information.

The prompt experiment should be reported separately from the deterministic offline mock-provider tests.

### Decision

Accepted.

Two prompt versions were tested manually using a real AI model with masked synthetic input.

### Verification

Both prompts preserved placeholders correctly.

Prompt Version 1 produced useful responses but introduced minor unsupported interpretation in all three cases.

Prompt Version 2:

- preserved placeholders;
- stayed closer to explicit facts;
- used a consistent recruiter-friendly structure; and
- reduced unsupported interpretation.

Prompt Version 2 was selected as the preferred prompt.

### Result

Accepted and documented in `DESIGN.md` and `EVALUATION.md`.

---

## Entry 18 - Missing and Modified Placeholder Tests

### Source

Course project handbook and ChatGPT

### Topic

Provider-response completeness and token modification

### Suggestion

Add two response cases that were not yet covered by the first 20 Milestone 3 tests:

1. a provider response that omits a previously issued placeholder;
2. a provider response that changes an issued placeholder into a different valid-looking placeholder.

The missing-placeholder case should show that an omitted value cannot be restored.

The modified-placeholder case should show that an unauthorized changed token is rejected.

### Decision

Accepted.

Two additional mock-provider modes and tests were added.

### Verification

The automated suite produced:

```text
test_missing_placeholder ... ok
test_modified_placeholder ... ok
```

The complete run ended with:

```text
Ran 22 tests in 0.009s

OK
```

### Result

Accepted and verified.

---

## Entry 19 - Milestone 3 Documentation Update

### Source

Course project handbook and ChatGPT

### Topic

Living documentation

### Suggestion

Update the existing project documents rather than creating separate long Milestone 3 reports.

The documentation should reflect the actual implemented system and current evaluation evidence.

### Decision

Accepted.

The following files were updated:

- `README.md`
- `docs/DESIGN.md`
- `docs/EVALUATION.md`
- `docs/USER_GUIDE.md`
- `docs/ASSISTANCE.md`

The updates included:

- MASK/REMOVE policy behavior;
- overlap rules;
- request-local mapping lifetime;
- provider failure handling;
- 22-test results;
- detection metrics;
- prompt comparison;
- selected prompt;
- programming-language concepts; and
- current limitations.

### Verification

Each document was checked against the current implementation and the executed Milestone 3 results.

### Result

Accepted and used as the current project documentation.

---

## Updated Summary

AI assistance was used primarily for:

- planning the implementation;
- selecting data structures;
- designing placeholder behavior;
- defining the JSON contract;
- drafting and refining code;
- separating detection, policy, mapping, provider, validation, and restoration responsibilities;
- designing deterministic overlap behavior;
- designing request-local state and cleanup;
- creating provider-failure simulations;
- designing automated tests;
- designing the detection evaluation;
- comparing prompt versions; and
- updating project documentation.

Suggestions were not treated as automatically correct.

Major suggestions were checked by running the relevant component, inspecting the output, or executing the automated test suite.

At the end of Milestone 3:

```text
22 tests executed
22 tests passed
0 tests failed
```

The detection evaluation produced:

```text
TP: 10
FP: 0
FN: 1
Precision: 1.000
Recall: 0.909
Outbound privacy leaks: 1
```

Prompt Version 2 was selected after a three-case comparison because it produced more structured, fact-constrained output while preserving placeholders.

The project documentation now reflects the implemented Milestone 3 gateway and its observed results.
