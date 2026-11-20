# DESIGN.md

## 1. Intended User
Recruiter or HR employee reviewing job applications.

## 2. AI-Assisted Task
Generate a qualification summary of a candidate's resume while
preventing personally identifiable information from being sent
to the external AI provider.

For automated gateway testing, the provider is a deterministic offline mock provider.
This allows the complete privacy-gateway pipeline to be tested without sending
data to an external service. A real AI model was used separately for the
Milestone 3 prompt-comparison experiment using only masked synthetic input.

## 3. Motivation
Recruiters may want AI assistance summarizing qualifications,
but resumes contain personal information that does not need to
be exposed to the AI provider.

The goal of the privacy gateway is to keep selected sensitive values local
while still allowing the resume's non-sensitive qualifications, skills,
education, and experience to be processed.

## 4. Sensitive Information Categories
- Person's name
- Email address
- Phone number
- Street address

All names, addresses, phone numbers, and email addresses used
during development and testing will be synthetic.

### Person's Name
Names will be detected using exact matching against a local synthetic
term list.

Example:

`Jane Smith`

Placeholder:

`[[r1:NAME:1]]`

### Email Address
Email addresses will be detected using a structured regular-expression
pattern.

Supported example:

`jane.smith@example.com`

Placeholder:

`[[r1:EMAIL:1]]`

Initial pattern:

`[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}`

### Phone Number
Phone numbers will be detected using a structured regular-expression
pattern.

For Milestone 2, the supported phone-number format is:

`###-###-####`

Example:

`478-555-1234`

Placeholder:

`[[r1:PHONE:1]]`

Initial pattern:

`\d{3}-\d{3}-\d{4}`

The current implementation does not attempt to recognize every possible
phone-number format.

### Physical Address
Physical addresses will be detected using exact matching against a local
synthetic address term list.

Example:

`123 Example Street, Sampletown, GA 30000`

Placeholder:

`[[r1:ADDRESS:1]]`

The current implementation only detects physical addresses that appear
in the local synthetic term list. It does not attempt to recognize every
possible address format.

## 5. Success Criteria
- Supported sensitive values are detected.
- `MASK` values are replaced locally before they reach the provider.
- `REMOVE` values are deleted before provider processing and are not restored.
- Missing policy rules default to `MASK`.
- Invalid policy values produce controlled errors.
- The placeholder-to-original-value mapping remains local.
- Repeated sensitive values receive the same placeholder within one request.
- Different sensitive values within the same category receive different placeholders.
- Overlapping detections are resolved deterministically.
- Each request has its own mapping and the mapping is cleared after processing.
- Foreign-request placeholders are rejected.
- Provider errors, timeouts, and malformed responses produce controlled errors.
- No provider or validation failure causes an unmasked fallback.
- Valid authorized placeholders are restored locally.
- The final output remains useful for resume qualification analysis.
- Automated and manual evaluation evidence supports the implemented behavior.

## 6. Non-Goals
The following are outside the current project scope:

- Hiring decisions
- Candidate ranking
- Background checks
- Sending real employee/applicant data to AI
- Detecting every possible representation of sensitive information
- Universal named-entity recognition
- PDF or DOCX parsing
- OCR
- A graphical user interface
- A required live AI API adapter
- Multi-turn conversations
- Persistent cross-request mappings
- Production deployment


## 7. Milestone 3 Scope

Milestone 3 implements and evaluates the hardened privacy-gateway flow:

`Input -> Detection -> Policy -> Mapping/Masking -> Offline Mock Provider -> Validation -> Restoration -> Mapping Cleanup -> Output`

The implementation includes:

- `NAME`, `EMAIL`, `PHONE`, and `ADDRESS`
- Exact matching using local synthetic term lists
- Structured regular-expression matching
- Deterministic overlap resolution
- `MASK` and `REMOVE` category policies
- Default `MASK` behavior for missing rules
- Controlled `INVALID_POLICY` errors
- Request-local placeholder mappings
- Repeated-value and different-entity handling
- Independent request isolation
- Mapping cleanup after processing
- Foreign-request placeholder rejection
- Unknown and malformed placeholder rejection
- Provider error and timeout simulation
- Malformed provider-response handling
- No unmasked fallback
- Local restoration of authorized MASK placeholders
- JSON input and output
- Automated tests
- Detection metrics and privacy-leak counting
- Prompt comparison using the same three masked synthetic cases

## 8. Programming Language Choice
### Selected Language: Python
Python was selected because the project primarily performs text processing,
regular-expression matching, JSON handling, request-local state management,
testing, and provider-interface simulation.

Python's built-in strings, dictionaries, `re`, `json`, exceptions, dataclasses,
and `unittest` support allow the gateway components to remain small and
explainable.

### Alternative: TypeScript
Two important trade-offs are:

- TypeScript provides stronger compile-time type checking, while Python relies
  more heavily on runtime validation, type hints, exceptions, and tests.
- Python provides concise text-processing and testing support for the current
  command-line system, while TypeScript would be especially useful if the
  gateway were later integrated into a larger browser/server web application.

For the current text-processing-focused project, Python remains the better fit.

## 9. Architecture / Data Flow

### Local / Trusted System

1. `main.py` receives a JSON request.
2. `pipeline.py` validates the request structure and reserved syntax.
3. `policy.py` resolves supplied category policies.
4. Missing policy rules default to `MASK`; invalid policies return a controlled error.
5. `mapping.py` creates a request-local `RequestMapping`.
6. `detector.py` finds supported sensitive values.
7. Overlapping detections are resolved deterministically.
8. `masker.py` applies `MASK` or `REMOVE`.
9. `MASK` values receive request-specific placeholders.
10. `REMOVE` values are deleted and are not entered into the mapping.
11. Only protected text is passed to the provider.

`---- PROVIDER BOUNDARY ----`

### Offline Mock Provider

12. `mock_provider.py` receives only protected text.
13. Normal mode returns a deterministic response.
14. Test modes simulate invalid placeholders, provider errors, timeouts, and malformed responses.

`---- PROVIDER BOUNDARY ----`

### Local / Trusted System

15. `pipeline.py` verifies the provider response type.
16. `validator.py` checks placeholder syntax, request ownership, and whether the current request issued each token.
17. `restorer.py` restores only valid authorized MASK placeholders.
18. `REMOVE` values are never restored because they were never stored.
19. `pipeline.py` returns a successful result or a controlled JSON error.
20. A `finally` block clears the request mapping after processing.

The placeholder-to-original-value mapping never crosses the provider boundary.

## 10. Component Responsibilities

### `main.py`
Reads one JSON request from the command line and passes it to the pipeline.

### `pipeline.py`
Coordinates request validation, policy resolution, mapping creation, detection,
masking/removal, provider invocation, validation, restoration, controlled error
handling, and guaranteed mapping cleanup.

### `detector.py`
Finds supported sensitive information.

- `NAME`: exact matching from a local synthetic name list
- `ADDRESS`: exact matching from a local synthetic address list
- `EMAIL`: regular-expression pattern
- `PHONE`: regular-expression pattern

It also removes duplicate detections and resolves overlaps deterministically.

### `policy.py`
Defines the supported category policies:

- `MASK`
- `REMOVE`

Missing rules default to `MASK`. Invalid categories or values produce
`INVALID_POLICY`.

### `mapping.py`
Defines `RequestMapping`, which stores request-local placeholder state.

It keeps:

- placeholder -> original value
- `(category, value)` -> placeholder
- per-category counters

Repeated values reuse the same placeholder. The mapping is cleared after the
request completes.

### `masker.py`
Applies the resolved policy to accepted detections.

- `MASK`: create/reuse a placeholder and replace the original value.
- `REMOVE`: delete the value and do not store it in the mapping.

### `mock_provider.py`
Receives only protected text and returns deterministic responses.

Test modes simulate:

- unknown placeholder
- malformed placeholder
- foreign-request placeholder
- missing placeholder
- modified placeholder
- malformed provider response
- provider error
- provider timeout

### `validator.py`
Checks placeholder syntax, request ownership, and whether a placeholder was
actually issued for the current request.

Controlled errors include:

- `INVALID_PLACEHOLDER`
- `UNKNOWN_PLACEHOLDER`
- `FOREIGN_REQUEST_PLACEHOLDER`

### `restorer.py`
Validates the provider response and restores only authorized MASK placeholders.
REMOVE values are never restored.

### `evaluation_metrics.py`
Reports TP, FP, FN, precision, recall, and outbound protected-value leaks for
labeled synthetic detection cases.

### `tests/test_pipeline.py`
Contains the automated Milestone 3 gateway suite. The completed suite contains
22 passing tests.

## 11. Placeholder Format
The placeholder format is:

`[[request_id:CATEGORY:index]]`

Examples:

`[[r1:NAME:1]]`

`[[r1:EMAIL:1]]`

`[[r1:PHONE:1]]`

`[[r1:ADDRESS:1]]`

The parts of the placeholder have the following meanings:

- `request_id` identifies the current request.
- `CATEGORY` identifies the sensitive-information category.
- `index` distinguishes different values within the same category.

Supported categories are:

- `NAME`
- `EMAIL`
- `PHONE`
- `ADDRESS`

The request ID must use the format `r` followed by a positive integer.

Examples:

`r1`

`r2`

`r15`

### Repeated Values
Repeated occurrences of the same sensitive value within one request reuse the
same placeholder.

Example input:

`Jane Smith has Python experience. Contact Jane Smith at jane.smith@example.com.`

Masked result:

`[[r1:NAME:1]] has Python experience. Contact [[r1:NAME:1]] at [[r1:EMAIL:1]].`

### Different Entities
Different values within the same category receive different indexes.

Example input:

`Jane Smith worked with John Davis.`

Masked result:

`[[r1:NAME:1]] worked with [[r1:NAME:2]].`

## 12. JSON Input and Output Contract
### Input Format

```json
{
  "request_id": "r1",
  "text": "Jane Smith lives at 123 Example Street, Sampletown, GA 30000. Contact Jane Smith at jane.smith@example.com or 478-555-1234."
}
```

### Input Fields

#### `request_id`
- Required
- Type: string
- Format: `r` followed by a positive integer
- Example: `r1`

#### `text`
- Required
- Type: string
- Must not be empty
- Contains the synthetic plain-text resume content to process

#### `policies`
- Optional
- Type: object when supplied
- Supported values: `MASK` and `REMOVE`
- Missing category rules default to `MASK`

### Successful Output

```json
{
  "status": "ok",
  "request_id": "r1",
  "masked_text": "[[r1:NAME:1]] lives at [[r1:ADDRESS:1]]. Contact [[r1:NAME:1]] at [[r1:EMAIL:1]] or [[r1:PHONE:1]].",
  "provider_response": "Mock qualification summary for [[r1:NAME:1]].",
  "output": "Mock qualification summary for Jane Smith."
}
```

The local placeholder mapping is intentionally excluded from the JSON output.

### Error Output

```json
{
  "status": "error",
  "request_id": "r1",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error description."
  }
}
```

### Status Values
The supported status values are:

- `ok`
- `error`

### Controlled Error Codes

#### `INVALID_JSON`
The input could not be parsed as valid JSON.

#### `INVALID_REQUEST`
A required field is missing, has the wrong type, or contains an invalid value.

#### `RESERVED_PLACEHOLDER_IN_INPUT`
The original input contains syntax reserved for gateway-generated placeholders.

#### `INVALID_PLACEHOLDER`
The provider response contains malformed reserved placeholder syntax.

#### `UNKNOWN_PLACEHOLDER`
The provider response contains a well-formed placeholder that was not issued
for the current request.

#### `FOREIGN_REQUEST_PLACEHOLDER`
The provider response contains a well-formed placeholder belonging to another request.

#### `INVALID_POLICY`
The request contains an unsupported category or policy value.

#### `MALFORMED_PROVIDER_RESPONSE`
The provider returned a non-text response.

#### `PROVIDER_ERROR`
The offline mock provider failed unexpectedly.

#### `PROVIDER_TIMEOUT`
The provider exceeded the simulated timeout.

## 13. Reserved Placeholder Handling

The `[[...]]` form is reserved for gateway-generated placeholders.

If original input already contains reserved placeholder syntax, the program
returns a controlled error rather than attempting to process the request.

Example input:

`Jane Smith worked on project [[r1:NAME:1]].`

Expected error code:

`RESERVED_PLACEHOLDER_IN_INPUT`

Provider responses are also checked before restoration.

If the current request issued:

`[[r1:NAME:1]]`

but the provider returns:

`[[r1:NAME:2]]`

the program returns:

`UNKNOWN_PLACEHOLDER`

If the provider returns malformed reserved syntax such as:

`[[r1:NAME]]`

the program returns:

`INVALID_PLACEHOLDER`

The system does not perform partial restoration or return an unmasked fallback
after validation fails.

## 14. Request-Local State and Lifetime

Each request creates its own `RequestMapping`.

For example:

`r13 -> [[r13:NAME:1]]`

`r14 -> [[r14:NAME:1]]`

Mappings are not shared between requests.

The request-local mapping is used to:

- reuse placeholders for repeated values;
- verify that returned placeholders were actually issued; and
- restore original values after validation.

The mapping lifetime ends when request processing ends.

`pipeline.py` uses a `finally` block to call `request_mapping.clear()`, so
cleanup occurs after both successful and failed processing paths.

Automated tests verify independent requests, direct mapping cleanup, and
pipeline cleanup behavior.

## 15. Offline Mock Provider Design and Failure Handling

The deterministic offline mock provider makes gateway behavior reproducible.

It supports normal behavior plus simulated:

- unknown placeholders;
- malformed placeholders;
- foreign-request placeholders;
- missing placeholders;
- modified placeholders;
- malformed non-text responses;
- provider errors; and
- provider timeouts.

Provider failures never cause an unmasked retry or fallback.

Controlled provider errors include:

- `PROVIDER_ERROR`
- `PROVIDER_TIMEOUT`
- `MALFORMED_PROVIDER_RESPONSE`

## 16. Prompt Design and Selected Prompt

Milestone 3 compared two prompt versions using the same three masked synthetic
resume cases.

Prompt Version 1 produced useful summaries and preserved placeholders, but it
introduced minor unsupported interpretation in all three cases.

Prompt Version 2 was more structured and stayed closer to the supplied facts,
so it was selected as the preferred prompt.

### Selected Prompt: Version 2

You are a recruiting assistant evaluating a candidate using only the information provided below.

Return your response using exactly these sections:

Qualification Summary:
Write 2-3 sentences summarizing the candidate's relevant qualifications.

Key Qualifications:
- List up to 4 qualifications explicitly supported by the provided information.

Missing Information:
- List important qualification information that is not provided, if applicable.

Requirements:
1. Use only facts contained in the provided text.
2. Do not infer or invent experience, skills, education, certifications, or accomplishments.
3. Preserve every placeholder exactly as written.
4. A placeholder such as `[[r1:NAME:1]]` represents protected information. Do not modify, expand, interpret, or replace it.
5. Do not expose or guess the original value represented by a placeholder.
6. Keep the response concise and suitable for a recruiter.

Input:

`{MASKED_TEXT}`

The real-model prompt experiment is separate from the deterministic offline
mock-provider tests.

## 17. Design Decisions

- The placeholder mapping remains local so original protected values are not sent to the provider.
- Plain-text input keeps the project focused on privacy-gateway behavior rather than document parsing.
- Names and physical addresses use exact local synthetic term lists so detection is deterministic and explainable.
- Email addresses and phone numbers use documented structured patterns.
- Request IDs are included in placeholders so ownership can be checked.
- Repeated values reuse existing placeholders.
- Different values within the same category receive different indexes.
- Overlapping detections are resolved deterministically before masking.
- Privacy policy is separated from detection.
- Missing category rules default to `MASK`.
- `REMOVE` values are not stored in the request mapping.
- Each request receives a separate mapping.
- Mappings are cleared after request processing.
- Provider responses are validated before restoration.
- Foreign-request placeholders are rejected even when syntactically valid.
- The provider is a deterministic offline mock so gateway tests are reproducible.
- Provider failures do not trigger an unmasked retry or fallback.
- JSON is used for a consistent, testable input/output interface.
- Reserved `[[...]]` syntax in original input is rejected.
- Prompt Version 2 was selected because it was more structured and less likely to introduce unsupported interpretation.

## 18. Milestone 3 Programming-Language Analysis

Milestone 3 connects programming-language concepts directly to the implemented
gateway.

### Types and Contracts

The system relies on explicit contracts between components.

Examples include:

- `request_id` must be a valid string;
- `text` must be a non-empty string;
- `policies` must be a dictionary when supplied;
- provider output must be text before placeholder validation;
- placeholders must follow `[[request_id:CATEGORY:index]]`;
- `Detection` represents one detected sensitive-value occurrence;
- `MaskingResult` represents the result of policy application; and
- `process_request()` returns either a successful JSON-style dictionary or a controlled error dictionary.

Python is dynamically typed, so these contracts are enforced through runtime
checks, constructors, dataclasses, exceptions, and automated tests.

Execution evidence includes:

- invalid JSON -> `INVALID_JSON`
- invalid request data -> `INVALID_REQUEST`
- malformed provider type -> `MALFORMED_PROVIDER_RESPONSE`
- malformed placeholder -> `INVALID_PLACEHOLDER`

### State Lifetime

`RequestMapping` is the main request-local mutable state.

It stores placeholder/value relationships and per-category counters while one
request is active.

The mapping is required during masking, validation, and restoration, then it is
cleared in a `finally` block when processing ends.

This limited lifetime reduces unnecessary retention of sensitive state.

Tests verify independent requests, direct mapping cleanup, and pipeline cleanup.

### Effects

Observable effects include:

- reading local synthetic term-list files;
- mutating request-local mapping dictionaries and counters;
- invoking the provider interface;
- simulating provider failure and timeout behavior;
- command-line JSON input/output; and
- clearing request-local state.

Keeping these effects separated makes the transformation and validation logic
easier to test.

### Interfaces

The implementation uses narrow module interfaces:

`pipeline -> detector`

`pipeline -> policy`

`masker -> RequestMapping`

`pipeline -> mock_provider`

`restorer -> validator`

`restorer -> RequestMapping`

Because these responsibilities are separated, provider failure modes can be
tested without changing detection or masking logic.

### Error Handling

The implementation uses controlled exceptions including:

- `PolicyError`
- `ValidationError`
- `MockProviderError`
- `TimeoutError`
- `ValueError`

`pipeline.py` converts these failures into stable JSON error results.

Examples include:

- `INVALID_POLICY`
- `UNKNOWN_PLACEHOLDER`
- `INVALID_PLACEHOLDER`
- `FOREIGN_REQUEST_PLACEHOLDER`
- `PROVIDER_ERROR`
- `PROVIDER_TIMEOUT`
- `MALFORMED_PROVIDER_RESPONSE`

This design prevents raw exceptions from becoming the public program interface
and prevents restoration after validation failure.

## 19. Milestone 3 Policy and Overlap Rules

### MASK and REMOVE

Detection answers what protected values are present.

Policy answers what should happen to each category.

`MASK` replaces the value with a request-local placeholder.

`REMOVE` deletes the value and does not create a mapping entry, so the value
cannot be restored later.

Missing policy rules default to `MASK`.

Unsupported rules such as `HIDE` produce `INVALID_POLICY`.

### Deterministic Overlap Resolution

The detector uses these rules:

1. Earlier start position wins.
2. If two detections begin at the same position, the longer match wins.
3. If start position and length are equal, category priority is used.
4. A later candidate overlapping an accepted detection is discarded.

Category priority is:

1. `EMAIL`
2. `PHONE`
3. `ADDRESS`
4. `NAME`

This makes overlap behavior reproducible.

## 20. Changes Across Milestones

### Milestone 1

Milestone 1 defined the intended user, task, motivation, sensitive categories,
placeholder design, language choice, initial architecture, acceptance cases, and
initial prompt.

### Milestone 2

Milestone 2 created the working prototype with:

- four implemented sensitive categories;
- exact and structured detection;
- request-local mappings;
- repeated-value handling;
- JSON input/output;
- deterministic mock-provider behavior;
- placeholder validation;
- local restoration; and
- automated pipeline tests.

### Milestone 3

Milestone 3 added:

- deterministic overlap resolution;
- `MASK` and `REMOVE` policies;
- default `MASK` behavior;
- invalid-policy handling;
- separate policy and mapping modules;
- cross-request isolation;
- foreign-request rejection;
- guaranteed mapping cleanup;
- provider timeout and error handling;
- malformed provider-response handling;
- missing- and modified-placeholder tests;
- no unmasked fallback;
- detection metrics and outbound leak counting;
- a two-prompt, three-case real-model comparison;
- selection of Prompt Version 2; and
- programming-language analysis tied to code and traces.

## 21. Evaluation Evidence

The completed Milestone 3 automated suite produced:

```text
Ran 22 tests in 0.009s

OK
```

Summary:

```text
22 tests executed
22 tests passed
0 tests failed
```

The labeled detection evaluation produced:

```text
TP: 10
FP: 0
FN: 1
Precision: 1.000
Recall: 0.909
Outbound privacy leaks: 1
```

The one false negative and privacy leak came from the deliberately unsupported
phone format:

`(478) 555-0199`

Detailed results are documented in `docs/EVALUATION.md`.

## 22. Current Limitations

- Names must appear in the local synthetic name list.
- Physical addresses must appear in the local synthetic address list.
- Exact name and address matching is case-sensitive.
- Phone detection currently supports only `###-###-####`.
- Parenthesized formats such as `(478) 555-0199` are not detected.
- The email pattern supports common formats but does not attempt to validate every legal email format.
- The system is single-turn.
- Automated gateway tests use an offline mock provider.
- The mock provider does not perform real qualification analysis.
- A live AI provider adapter is not required.
- PDF, DOCX, OCR, and graphical interfaces are not supported.
- Only synthetic data is used.
- Correct privacy masking does not guarantee perfectly fact-constrained AI output, so prompt design remains a separate concern.
