# AI Privacy Gateway - Resume Qualification Analysis

## Project Overview

This project is a local AI privacy gateway designed to protect selected sensitive information in resume text before the text is processed by an AI-style provider.

The intended user is a recruiter or Human Resources employee who wants assistance summarizing a candidate's qualifications without exposing selected personally identifiable information to the provider.

The Milestone 3 gateway uses a deterministic offline mock provider for automated gateway testing. A real AI model was used separately for the prompt-comparison experiment using only masked synthetic input.

The complete pipeline is:

```text
Input
  ->
Detection
  ->
Policy
  ->
Request Mapping / Masking
  ->
Offline Mock Provider
  ->
Validation
  ->
Restoration
  ->
Mapping Cleanup
  ->
Output
```

The gateway is designed so that protected original values and the placeholder mapping remain local.

---

## Supported Sensitive Information

The current implementation supports four categories:

- `NAME`
- `EMAIL`
- `PHONE`
- `ADDRESS`

Detection methods:

- `NAME`: exact matching against a local synthetic name list
- `ADDRESS`: exact matching against a local synthetic address list
- `EMAIL`: regular-expression pattern
- `PHONE`: regular-expression pattern

All development and testing data is synthetic.

---

## Privacy Policies

Each supported category can use one of two policies:

- `MASK`
- `REMOVE`

### MASK

`MASK` replaces the original sensitive value with a request-specific placeholder before provider processing.

Example:

```text
Jane Smith
```

becomes:

```text
[[r1:NAME:1]]
```

After the provider response is validated, an authorized MASK placeholder may be restored locally.

### REMOVE

`REMOVE` deletes the value before provider processing.

REMOVE values are not stored in the request mapping and therefore are not restored later.

### Default Policy

If a category is omitted from the `policies` object, it defaults to:

```text
MASK
```

Unsupported policy values produce a controlled:

```text
INVALID_POLICY
```

error.

---

## Placeholder Format

MASK values use:

```text
[[request_id:CATEGORY:index]]
```

Examples:

```text
[[r1:NAME:1]]
[[r1:EMAIL:1]]
[[r1:PHONE:1]]
[[r1:ADDRESS:1]]
```

Repeated occurrences of the same sensitive value reuse the same placeholder within one request.

Different sensitive values within the same category receive different indexes.

Request IDs are included in placeholders so the gateway can verify that a returned placeholder belongs to the current request.

---

## Privacy Boundary

The following remain local:

- Original input text
- Detected sensitive values
- Placeholder-to-original-value mappings
- Policy logic
- Validation logic
- Restoration logic
- Request-local state

The provider receives only the protected outbound text.

The placeholder mapping is never sent to the provider.

A provider response is validated before any MASK value is restored.

If validation or provider processing fails, the gateway does not send an unmasked fallback.

---

## Requirements

- Python 3.13.17
- Command-line terminal
- Project files
- Synthetic data files

No external packages are required for the current implementation.

---

## Project Structure

```text
ai-privacy-gateway/
|
|-- data/
|   |-- synthetic_names.txt
|   |-- synthetic_addresses.txt
|
|-- docs/
|   |-- ASSISTANCE.md
|   |-- DESIGN.md
|   |-- EVALUATION.md
|   |-- USER_GUIDE.md
|
|-- tests/
|   |-- test_pipeline.py
|
|-- detector.py
|-- policy.py
|-- mapping.py
|-- masker.py
|-- mock_provider.py
|-- validator.py
|-- restorer.py
|-- pipeline.py
|-- main.py
|-- evaluation_metrics.py
|-- tech_spike.py
|-- README.md
```

---

## Running the Program

From the project root, run:

```bash
python main.py
```

The program prompts for one JSON request.

Enter the JSON request on one line and press Enter.

---

## Example 1: Default MASK Policies

Input:

```json
{"request_id":"r1","text":"Jane Smith lives at 123 Example Street, Sampletown, GA 30000. Contact Jane Smith at jane.smith@example.com or 478-555-1234."}
```

Because no `policies` object is supplied, all supported categories default to `MASK`.

Expected protected text:

```text
[[r1:NAME:1]] lives at [[r1:ADDRESS:1]]. Contact [[r1:NAME:1]] at [[r1:EMAIL:1]] or [[r1:PHONE:1]].
```

Expected successful response shape:

```json
{
  "status": "ok",
  "request_id": "r1",
  "masked_text": "[[r1:NAME:1]] lives at [[r1:ADDRESS:1]]. Contact [[r1:NAME:1]] at [[r1:EMAIL:1]] or [[r1:PHONE:1]].",
  "provider_response": "Qualification Summary:\n[[r1:NAME:1]] lives at [[r1:ADDRESS:1]]. Contact [[r1:NAME:1]] at [[r1:EMAIL:1]] or [[r1:PHONE:1]].",
  "output": "Qualification Summary:\nJane Smith lives at 123 Example Street, Sampletown, GA 30000. Contact Jane Smith at jane.smith@example.com or 478-555-1234."
}
```

---

## Example 2: Mixed MASK and REMOVE Policies

Input:

```json
{"request_id":"r2","text":"Jane Smith lives at 123 Example Street, Sampletown, GA 30000. Contact Jane Smith at jane.smith@example.com or 478-555-1234.","policies":{"NAME":"MASK","ADDRESS":"MASK","EMAIL":"REMOVE","PHONE":"REMOVE"}}
```

Expected protected text:

```text
[[r2:NAME:1]] lives at [[r2:ADDRESS:1]]. Contact [[r2:NAME:1]] at  or .
```

Expected behavior:

- `NAME` is masked.
- `ADDRESS` is masked.
- `EMAIL` is removed.
- `PHONE` is removed.
- Removed email and phone values are not stored in the mapping.
- Removed values are not restored in the final output.

---

## JSON Input Format

A request has this form:

```json
{
  "request_id": "r1",
  "text": "resume text",
  "policies": {
    "NAME": "MASK",
    "EMAIL": "REMOVE"
  }
}
```

### `request_id`

Required.

The request ID must:

- be a string;
- begin with lowercase `r`; and
- be followed by a positive integer.

Examples:

```text
r1
r2
r15
```

### `text`

Required.

The `text` field:

- must be present;
- must be a string; and
- must not be empty.

Reserved `[[...]]` placeholder syntax is not allowed in original input.

### `policies`

Optional.

When supplied, `policies` must be an object.

Supported categories:

- `NAME`
- `EMAIL`
- `PHONE`
- `ADDRESS`

Supported policy values:

- `MASK`
- `REMOVE`

Missing category rules default to `MASK`.

---

## JSON Output Format

Successful requests return:

```json
{
  "status": "ok",
  "request_id": "r1",
  "masked_text": "...",
  "provider_response": "...",
  "output": "..."
}
```

Controlled failures return:

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

The local placeholder mapping is intentionally excluded from both successful and error output.

---

## Controlled Error Codes

The current gateway handles these controlled error conditions:

- `INVALID_JSON`
- `INVALID_REQUEST`
- `RESERVED_PLACEHOLDER_IN_INPUT`
- `INVALID_POLICY`
- `INVALID_PLACEHOLDER`
- `UNKNOWN_PLACEHOLDER`
- `FOREIGN_REQUEST_PLACEHOLDER`
- `MALFORMED_PROVIDER_RESPONSE`
- `PROVIDER_ERROR`
- `PROVIDER_TIMEOUT`

### Example: Invalid Policy

Input policy:

```json
{
  "NAME": "HIDE"
}
```

Expected error code:

```text
INVALID_POLICY
```

### Example: Unknown Placeholder

Example provider token:

```text
[[r5:NAME:999]]
```

Expected error:

```text
UNKNOWN_PLACEHOLDER
```

### Example: Foreign-Request Placeholder

If the current request is `r5`, a provider token such as:

```text
[[r999:NAME:1]]
```

produces:

```text
FOREIGN_REQUEST_PLACEHOLDER
```

---

## Detection and Overlap Rules

### Name

Detected using exact matching against:

```text
data/synthetic_names.txt
```

### Physical Address

Detected using exact matching against:

```text
data/synthetic_addresses.txt
```

### Email Address

Detected using a structured regular-expression pattern.

### Phone Number

The currently supported format is:

```text
###-###-####
```

Example:

```text
478-555-1234
```

A format such as:

```text
(478) 555-0199
```

is currently unsupported.

### Deterministic Overlap Resolution

When detected values overlap, the gateway resolves them deterministically:

1. Earlier starting position wins.
2. If two detections start at the same position, the longer match wins.
3. If start and length are equal, category priority is used.
4. A later candidate overlapping an accepted detection is discarded.

Category priority:

1. `EMAIL`
2. `PHONE`
3. `ADDRESS`
4. `NAME`

---

## Request-Local Mapping

Each request receives a separate `RequestMapping`.

The mapping is used to:

- create placeholders;
- reuse placeholders for repeated values;
- verify provider-returned placeholders; and
- restore authorized MASK values.

Mappings are not shared between requests.

At the end of processing, the mapping is cleared in a `finally` block.

This cleanup occurs after both successful and failed requests.

---

## Offline Mock Provider

The deterministic offline mock provider allows the privacy-gateway pipeline to be tested without:

- Internet access
- API keys
- Live AI services
- Real private data

The provider supports test modes for:

- normal response;
- unknown placeholder;
- malformed placeholder;
- foreign-request placeholder;
- missing placeholder;
- modified placeholder;
- malformed provider response;
- provider error; and
- provider timeout.

The provider receives only protected text.

---

## Running the Automated Tests

From the project root, run:

```bash
python -m unittest discover -s tests -v
```

Current observed result:

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

The tests cover:

- normal input;
- repeated sensitive values;
- no sensitive information;
- different entities;
- deterministic overlap handling;
- default MASK behavior;
- REMOVE behavior;
- invalid policies;
- unknown placeholders;
- malformed placeholders;
- foreign-request placeholders;
- missing placeholders;
- modified placeholders;
- independent requests;
- mapping cleanup;
- reserved placeholder syntax;
- provider errors;
- provider timeouts;
- malformed provider responses; and
- invalid JSON.

---

## Running the Detection Evaluation

From the project root, run:

```bash
python evaluation_metrics.py
```

Current overall result:

```text
TP: 10
FP: 0
FN: 1
Precision: 1.000
Recall: 0.909
Outbound privacy leaks: 1
```

The single false negative and outbound leak came from the deliberately tested unsupported phone format:

```text
(478) 555-0199
```

Supported labeled cases produced zero outbound privacy leaks.

---

## Prompt Evaluation

Two prompt versions were compared using the same three masked synthetic resume cases.

The automated gateway tests used the offline mock provider.

The prompt comparison used a real AI model only after the inputs had been masked.

Prompt Version 2 was selected because it:

- preserved placeholders correctly;
- used a consistent recruiter-friendly format;
- stayed closer to facts in the supplied input; and
- reduced unsupported interpretation compared with Prompt Version 1.

The full prompt comparison is documented in:

```text
docs/EVALUATION.md
```

The selected prompt is documented in:

```text
docs/DESIGN.md
```

---

## Current Limitations

The current implementation does not support:

- PDF files
- DOCX files
- OCR
- Graphical interfaces
- Multi-turn conversations
- Universal sensitive-information detection
- Every possible name
- Every possible physical address
- Every possible phone-number format
- Production deployment

Additional limitations:

- Name detection depends on exact, case-sensitive matches in the local synthetic name list.
- Address detection depends on exact, case-sensitive matches in the local synthetic address list.
- Phone detection currently supports only `###-###-####`.
- The email pattern supports common formats but does not attempt to validate every possible legal email address.
- Automated gateway testing uses an offline mock provider.
- The mock provider does not perform real qualification analysis.
- Correct privacy masking does not guarantee perfectly constrained AI output, so prompt design is evaluated separately.

---

## Privacy and Data Warning

Use synthetic data only.

Do not include:

- Real applicant information
- Real employee information
- Social Security numbers
- Passwords
- API keys
- Live credentials
- Other confidential records

This project is a course prototype and is not intended for production use.

---

## Documentation

Additional project documentation is located in the `docs` folder.

### `docs/DESIGN.md`

Contains:

- Requirements
- Architecture and privacy boundary
- Sensitive-information categories
- Policy design
- Placeholder format
- JSON I/O contract
- Request-local state
- Provider failure handling
- Selected prompt
- Programming-language analysis
- Design decisions
- Milestone changes
- Current limitations

### `docs/EVALUATION.md`

Contains:

- Planned and executed cases
- Automated test results
- Detection metrics
- Privacy-leak counts
- Policy evaluation
- Placeholder/restoration evaluation
- Provider failure results
- Prompt comparison
- Failures and limitations

### `docs/USER_GUIDE.md`

Contains:

- Detailed instructions for running the program
- Supported formats
- Example inputs and outputs
- Warnings
- Troubleshooting

### `docs/ASSISTANCE.md`

Records important AI, peer, library, and source assistance along with how that assistance was checked or verified.
