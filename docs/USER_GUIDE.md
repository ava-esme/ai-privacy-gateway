# USER_GUIDE.md

## 1. Overview

The AI Privacy Gateway is a command-line program that protects selected sensitive information before synthetic resume text is processed by an AI-style provider.

The gateway currently uses a deterministic offline mock provider for automated privacy-gateway testing.

The Milestone 3 pipeline is:

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

The program supports four sensitive-information categories:

- `NAME`
- `EMAIL`
- `PHONE`
- `ADDRESS`

Only synthetic data should be used.

---

## 2. Requirements

The program requires:

- Python 3.13.17
- A command-line terminal
- The project files
- The synthetic data files

Check the installed Python version with:

```bash
python --version
```

No external Python packages are required for the current implementation.

---

## 3. Project Files

The main project files are:

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

## 4. Running the Program

Open a terminal in the project root.

Run:

```bash
python main.py
```

The program displays:

```text
AI Privacy Gateway
------------------
Enter a JSON request.
```

Enter the JSON request on one line and press Enter.

Example:

```json
{"request_id":"r1","text":"Jane Smith lives at 123 Example Street, Sampletown, GA 30000. Contact Jane Smith at jane.smith@example.com or 478-555-1234."}
```

---

## 5. JSON Input Format

The program accepts one JSON object.

The required fields are:

- `request_id`
- `text`

The optional field is:

- `policies`

Example:

```json
{
  "request_id": "r1",
  "text": "Jane Smith has Python experience.",
  "policies": {
    "NAME": "MASK",
    "EMAIL": "REMOVE"
  }
}
```

### `request_id`

The request ID must:

- be a string;
- begin with lowercase `r`; and
- be followed by a positive integer.

Valid examples:

```text
r1
r2
r15
```

Invalid examples:

```text
r0
R1
request1
```

### `text`

The `text` field:

- must be present;
- must be a string;
- must not be empty; and
- must not contain reserved `[[...]]` placeholder syntax.

### `policies`

The `policies` field is optional.

When supplied, it must be a JSON object.

Supported categories:

- `NAME`
- `EMAIL`
- `PHONE`
- `ADDRESS`

Supported policy values:

- `MASK`
- `REMOVE`

Any category not included in `policies` defaults to:

```text
MASK
```

---

## 6. Privacy Policies

### MASK

`MASK` replaces the sensitive value with a request-local placeholder before provider processing.

Example:

```text
Jane Smith
```

becomes:

```text
[[r1:NAME:1]]
```

If the provider response is valid, the placeholder may be restored locally.

### REMOVE

`REMOVE` deletes the sensitive value before provider processing.

The value is not stored in the request mapping.

Therefore, REMOVE values are not restored later.

### Example: Mixed Policies

Input:

```json
{"request_id":"r2","text":"Jane Smith lives at 123 Example Street, Sampletown, GA 30000. Contact Jane Smith at jane.smith@example.com or 478-555-1234.","policies":{"NAME":"MASK","ADDRESS":"MASK","EMAIL":"REMOVE","PHONE":"REMOVE"}}
```

Expected protected text:

```text
[[r2:NAME:1]] lives at [[r2:ADDRESS:1]]. Contact [[r2:NAME:1]] at  or .
```

Expected behavior:

- Name is masked.
- Address is masked.
- Email is removed.
- Phone is removed.
- Removed values are not restored.

---

## 7. Successful Output

A successful request returns JSON similar to:

```json
{
  "status": "ok",
  "request_id": "r1",
  "masked_text": "[[r1:NAME:1]] has 3 years of Python experience.",
  "provider_response": "Qualification Summary:\n[[r1:NAME:1]] has 3 years of Python experience.",
  "output": "Qualification Summary:\nJane Smith has 3 years of Python experience."
}
```

### `status`

A successful request returns:

```text
ok
```

### `request_id`

The request ID supplied in the original request.

### `masked_text`

The protected text after MASK and REMOVE policies have been applied.

### `provider_response`

The response returned by the offline mock provider.

It should contain only protected text and valid placeholders.

### `output`

The final locally restored response.

Only authorized MASK placeholders are restored.

REMOVE values are not restored.

---

## 8. Supported Sensitive Information

### Names

Names are detected using exact matching against:

```text
data/synthetic_names.txt
```

Example:

```text
Jane Smith
```

becomes:

```text
[[r1:NAME:1]]
```

Only names contained in the synthetic term list are detected.

### Physical Addresses

Physical addresses are detected using exact matching against:

```text
data/synthetic_addresses.txt
```

Example:

```text
123 Example Street, Sampletown, GA 30000
```

becomes:

```text
[[r1:ADDRESS:1]]
```

Only addresses contained in the synthetic term list are detected.

### Email Addresses

Email addresses are detected using a structured regular-expression pattern.

Example:

```text
jane.smith@example.com
```

becomes:

```text
[[r1:EMAIL:1]]
```

### Phone Numbers

The current supported phone format is:

```text
###-###-####
```

Example:

```text
478-555-1234
```

becomes:

```text
[[r1:PHONE:1]]
```

Other phone-number formats may not be detected.

For example:

```text
(478) 555-0199
```

is currently unsupported.

---

## 9. Repeated and Different Sensitive Values

### Repeated Values

Repeated occurrences of the same sensitive value use the same placeholder within one request.

Example:

```text
Jane Smith has Python experience. Contact Jane Smith at jane.smith@example.com.
```

Masked result:

```text
[[r1:NAME:1]] has Python experience. Contact [[r1:NAME:1]] at [[r1:EMAIL:1]].
```

Both occurrences of `Jane Smith` use:

```text
[[r1:NAME:1]]
```

### Different Values

Different values within the same category receive different placeholder numbers.

Example:

```text
Jane Smith worked with John Davis.
```

becomes:

```text
[[r1:NAME:1]] worked with [[r1:NAME:2]].
```

---

## 10. Overlap Handling

Detected values can sometimes overlap.

The gateway resolves overlaps deterministically.

Rules:

1. Earlier starting position wins.
2. If two detections begin at the same position, the longer match wins.
3. If start position and length are equal, category priority is used.
4. A later overlapping candidate is discarded.

Category priority:

1. `EMAIL`
2. `PHONE`
3. `ADDRESS`
4. `NAME`

This ensures the same input produces the same accepted detections each time.

---

## 11. Request Isolation and Mapping Cleanup

Each request receives its own `RequestMapping`.

Mappings are not shared between requests.

Example:

```text
r13 -> [[r13:NAME:1]]
r14 -> [[r14:NAME:1]]
```

A placeholder created for `r13` is not authorized for `r14`.

After request processing ends, the mapping is cleared.

Cleanup runs after both successful and failed requests.

---

## 12. Error Responses

Errors are returned as JSON.

Example:

```json
{
  "status": "error",
  "request_id": "r1",
  "error": {
    "code": "UNKNOWN_PLACEHOLDER",
    "message": "Provider response contained an unknown placeholder."
  }
}
```

The current gateway supports these controlled error codes.

### `INVALID_JSON`

The input could not be parsed as valid JSON.

### `INVALID_REQUEST`

The request is missing a required field or contains an invalid value.

### `RESERVED_PLACEHOLDER_IN_INPUT`

The original input contains reserved `[[...]]` placeholder syntax.

Do not include values such as:

```text
[[r1:NAME:1]]
```

in original input.

### `INVALID_POLICY`

A supplied policy contains an unsupported category or value.

Example:

```json
{"NAME":"HIDE"}
```

### `INVALID_PLACEHOLDER`

The provider returned malformed placeholder syntax.

Example:

```text
[[r1:NAME]]
```

### `UNKNOWN_PLACEHOLDER`

The provider returned a valid-looking placeholder that was never issued for the current request.

Example:

```text
[[r1:NAME:999]]
```

### `FOREIGN_REQUEST_PLACEHOLDER`

The provider returned a placeholder belonging to another request.

Example:

```text
[[r999:NAME:1]]
```

### `MALFORMED_PROVIDER_RESPONSE`

The provider returned a response that was not text.

### `PROVIDER_ERROR`

The offline provider reported a simulated failure.

### `PROVIDER_TIMEOUT`

The offline provider reported a simulated timeout.

After a provider or validation failure, the gateway does not send an unmasked fallback.

---

## 13. Missing and Modified Provider Placeholders

### Missing Placeholder

If the provider simply omits a previously issued placeholder, there is no unauthorized token to restore.

The response may still succeed, but the omitted original value cannot be restored.

This is mainly a usefulness/restoration issue rather than a privacy violation.

### Modified Placeholder

If the provider changes an issued token into a different valid-looking token, the modified token is rejected.

Example:

```text
[[r23:NAME:1]]
```

changed to:

```text
[[r23:EMAIL:1]]
```

produces:

```text
UNKNOWN_PLACEHOLDER
```

---

## 14. Running the Automated Tests

From the project root, run:

```bash
python -m unittest discover -s tests -v
```

A successful current test run ends with:

```text
----------------------------------------------------------------------
Ran 22 tests in 0.009s

OK
```

The current suite checks:

- normal input;
- repeated sensitive values;
- no sensitive information;
- different entities;
- overlap handling;
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

## 15. Running the Detection Evaluation

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

The one false negative and leak came from the deliberately unsupported phone format:

```text
(478) 555-0199
```

Supported labeled cases produced zero outbound leaks.

---

## 16. Supported Input

The current gateway supports:

- plain-text synthetic resume content;
- JSON command-line requests;
- optional category policies;
- synthetic names;
- synthetic physical addresses;
- supported email formats;
- phone numbers in `###-###-####` format;
- single-turn requests; and
- deterministic offline provider testing.

---

## 17. Unsupported Features

The current project does not support:

- PDF files;
- DOCX files;
- images;
- OCR;
- a required live AI API;
- graphical interfaces;
- multi-turn conversations;
- universal sensitive-information detection;
- every possible name or address;
- every possible phone-number format; or
- production deployment.

---

## 18. Privacy Warning

Use synthetic data only.

Do not enter or commit:

- real applicant information;
- real employee records;
- Social Security numbers;
- passwords;
- API keys;
- live credentials; or
- other private or confidential records.

This project is a course prototype and is not intended for production use.

---

## 19. Troubleshooting

### Python is not recognized

Run:

```bash
python --version
```

If Python is installed but the command is not recognized, verify that Python is added to the system PATH and restart the terminal or Visual Studio Code.

### Synthetic data file not found

Verify that these files exist:

```text
data/synthetic_names.txt
data/synthetic_addresses.txt
```

Also verify that the filenames exactly match the names expected by `detector.py`.

### A name is not masked

Verify that the exact name appears in:

```text
data/synthetic_names.txt
```

Name matching is exact and case-sensitive.

### An address is not masked

Verify that the exact address appears in:

```text
data/synthetic_addresses.txt
```

Address matching is exact and case-sensitive.

### A phone number is not masked

Verify that it uses:

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

will not currently be detected.

### The program returns `RESERVED_PLACEHOLDER_IN_INPUT`

The original input contains `[[...]]` syntax reserved for gateway-generated placeholders.

Remove that syntax and try again.

### The program returns `INVALID_POLICY`

Check that:

- the category is one of `NAME`, `EMAIL`, `PHONE`, or `ADDRESS`; and
- the policy value is either `MASK` or `REMOVE`.

### The program returns `FOREIGN_REQUEST_PLACEHOLDER`

The provider response contains a placeholder belonging to a different request.

The gateway intentionally refuses to restore it.

### The program returns `UNKNOWN_PLACEHOLDER`

The provider response contains a valid-looking placeholder that was not issued for the current request.

The gateway intentionally refuses to restore it.

### Tests fail

Run:

```bash
python -m unittest discover -s tests -v
```

Review the failing test name and error message.

Also verify that:

- `Jane Smith` exists in `data/synthetic_names.txt`;
- `John Davis` exists in `data/synthetic_names.txt`;
- the expected synthetic address exists in `data/synthetic_addresses.txt`; and
- all required Python files are in the project root.

---

## 20. Additional Documentation

See:

- `README.md` for project setup and quick examples.
- `docs/DESIGN.md` for architecture, policies, state, prompt design, and programming-language analysis.
- `docs/EVALUATION.md` for automated test evidence, detection metrics, privacy-leak results, and prompt comparison.
- `docs/ASSISTANCE.md` for documented AI, peer, library, and source assistance.
