# EVALUATION.md

## 1. Evaluation Goal

The goal of the evaluation is to verify that the Milestone 2 privacy gateway:

- detects the supported sensitive-information categories;
- masks sensitive values before they reach the provider;
- preserves repeated sensitive values correctly;
- distinguishes different sensitive entities;
- validates provider responses before restoration;
- restores only valid placeholders;
- returns controlled errors for invalid input or provider behavior; and
- produces useful final output while keeping the placeholder mapping local.

The supported Milestone 2 sensitive-information categories are:

- `NAME`
- `EMAIL`
- `PHONE`
- `ADDRESS`

All test data is synthetic.

---

## 2. Test Environment

The prototype is implemented in Python and tested from the command line.

The automated test suite is located in:

`tests/test_pipeline.py`

The test suite is run with:

```bash
python -m unittest discover -s tests -v
```

Observed result:

```text
Ran 10 tests in 0.003s

OK
```

All 10 automated tests passed.

---

## 3. Milestone 1 Acceptance Cases

The four acceptance cases planned during Milestone 1 were converted into automated tests for Milestone 2.

### Case 1: Normal Input

Test:

`test_normal_input`

Purpose:

Verify that the system detects and masks supported sensitive information, passes only masked information to the provider, and restores valid placeholders in the final output.

Input includes:

- name;
- physical address;
- email address; and
- phone number.

Example input:

```text
Jane Smith lives at 123 Example Street, Sampletown, GA 30000.
Contact Jane Smith at jane.smith@example.com or 478-555-1234.
```

Expected masked values:

```text
[[r1:NAME:1]]
[[r1:ADDRESS:1]]
[[r1:EMAIL:1]]
[[r1:PHONE:1]]
```

Expected behavior:

- All supported sensitive values are detected.
- Original sensitive values do not appear in the provider response.
- Valid placeholders are restored in the final output.
- The final status is `ok`.

Result:

**PASS**

---

### Case 2: Repeated Sensitive Values

Test:

`test_repeated_sensitive_value`

Purpose:

Verify that repeated occurrences of the same sensitive value use the same placeholder.

Example input:

```text
Jane Smith has Python experience.
Contact Jane Smith at jane.smith@example.com.
```

Expected masked result:

```text
[[r2:NAME:1]] has Python experience.
Contact [[r2:NAME:1]] at [[r2:EMAIL:1]].
```

The second occurrence of `Jane Smith` must reuse:

```text
[[r2:NAME:1]]
```

It must not create:

```text
[[r2:NAME:2]]
```

Result:

**PASS**

---

### Case 3: No Sensitive Information

Test:

`test_no_sensitive_information`

Purpose:

Verify that text containing no supported sensitive values is not unnecessarily modified.

Example input:

```text
Candidate has four years of Python experience and experience with AWS.
```

Expected behavior:

- No placeholders are created.
- The masked text is identical to the original input.
- The request still completes successfully.

Result:

**PASS**

---

### Case 4: Invalid Placeholder Response

Tests:

- `test_unknown_placeholder_response`
- `test_malformed_placeholder_response`

Purpose:

Verify that the system does not restore provider responses containing unauthorized or malformed placeholders.

#### Unknown Placeholder

Example:

```text
[[r4:NAME:999]]
```

This follows the placeholder format, but it was never issued for the request.

Expected error:

```text
UNKNOWN_PLACEHOLDER
```

Result:

**PASS**

#### Malformed Placeholder

Example:

```text
[[r5:NAME]]
```

This uses reserved placeholder syntax but does not follow the required format.

Expected error:

```text
INVALID_PLACEHOLDER
```

Result:

**PASS**

---

## 4. Additional Milestone 2 Tests

Additional tests were added beyond the four original Milestone 1 cases.

### Different Entities

Test:

`test_different_entities`

Purpose:

Verify that different sensitive values within the same category receive different placeholders.

Example input:

```text
Jane Smith worked with John Davis on a Python project.
```

Expected masked result:

```text
[[r6:NAME:1]] worked with [[r6:NAME:2]] on a Python project.
```

Expected behavior:

- `Jane Smith` and `John Davis` receive different placeholders.
- Both names are restored correctly in the final output.

Result:

**PASS**

---

### Reserved Placeholder in Original Input

Test:

`test_reserved_placeholder_in_input`

Purpose:

Verify that users cannot supply text containing syntax reserved for gateway-generated placeholders.

Example input:

```text
Jane Smith worked on [[r7:NAME:1]].
```

Expected error:

```text
RESERVED_PLACEHOLDER_IN_INPUT
```

Result:

**PASS**

---

### Provider Failure

Test:

`test_provider_error`

Purpose:

Verify that a simulated provider failure produces a controlled error.

The offline mock provider is run in:

```text
provider_error
```

mode.

Expected error:

```text
PROVIDER_ERROR
```

The system must not return an unmasked fallback.

Result:

**PASS**

---

### Invalid JSON

Test:

`test_invalid_json`

Purpose:

Verify that malformed JSON input produces a controlled error rather than crashing.

Expected error:

```text
INVALID_JSON
```

Result:

**PASS**

---

### Missing Required Field

Test:

`test_missing_text_field`

Purpose:

Verify that a request missing the required `text` field is rejected.

Expected error:

```text
INVALID_REQUEST
```

Result:

**PASS**

---

## 5. Automated Test Results

The complete test run produced:

```text
test_different_entities (test_pipeline.TestPrivacyGatewayPipeline.test_different_entities) ... ok
test_invalid_json (test_pipeline.TestPrivacyGatewayPipeline.test_invalid_json) ... ok
test_malformed_placeholder_response (test_pipeline.TestPrivacyGatewayPipeline.test_malformed_placeholder_response) ... ok
test_missing_text_field (test_pipeline.TestPrivacyGatewayPipeline.test_missing_text_field) ... ok
test_no_sensitive_information (test_pipeline.TestPrivacyGatewayPipeline.test_no_sensitive_information) ... ok
test_normal_input (test_pipeline.TestPrivacyGatewayPipeline.test_normal_input) ... ok
test_provider_error (test_pipeline.TestPrivacyGatewayPipeline.test_provider_error) ... ok
test_repeated_sensitive_value (test_pipeline.TestPrivacyGatewayPipeline.test_repeated_sensitive_value) ... ok
test_reserved_placeholder_in_input (test_pipeline.TestPrivacyGatewayPipeline.test_reserved_placeholder_in_input) ... ok
test_unknown_placeholder_response (test_pipeline.TestPrivacyGatewayPipeline.test_unknown_placeholder_response) ... ok

----------------------------------------------------------------------
Ran 10 tests in 0.003s

OK
```

Summary:

- Tests executed: 10
- Tests passed: 10
- Tests failed: 0

---

## 6. End-to-End Pipeline Result

The complete Milestone 2 pipeline was also executed manually.

Input:

```json
{
    "request_id": "r1",
    "text": "Jane Smith lives at 123 Example Street, Sampletown, GA 30000. Jane Smith has 3 years of Python experience. Contact Jane Smith at jane.smith@example.com or 478-555-1234."
}
```

Masked text:

```text
[[r1:NAME:1]] lives at [[r1:ADDRESS:1]]. [[r1:NAME:1]] has 3 years of Python experience. Contact [[r1:NAME:1]] at [[r1:EMAIL:1]] or [[r1:PHONE:1]].
```

Mock provider response:

```text
Qualification Summary:
[[r1:NAME:1]] lives at [[r1:ADDRESS:1]]. [[r1:NAME:1]] has 3 years of Python experience. Contact [[r1:NAME:1]] at [[r1:EMAIL:1]] or [[r1:PHONE:1]].
```

Final locally restored output:

```text
Qualification Summary:
Jane Smith lives at 123 Example Street, Sampletown, GA 30000. Jane Smith has 3 years of Python experience. Contact Jane Smith at jane.smith@example.com or 478-555-1234.
```

Result:

**PASS**

This demonstrates the complete Milestone 2 flow:

```text
Input
  ->
Detection
  ->
Masking
  ->
Offline Mock Provider
  ->
Validation
  ->
Restoration
  ->
Output
```

---

## 7. Privacy Boundary Evaluation

The normal-input test verifies that original sensitive values do not appear in the mock provider response.

For the tested request, the provider sees:

```text
[[r1:NAME:1]]
[[r1:ADDRESS:1]]
[[r1:EMAIL:1]]
[[r1:PHONE:1]]
```

rather than the original values.

The local placeholder mapping is not included in the provider request or the successful JSON output.

The mapping remains local and is used only after validation succeeds.

---

## 8. Controlled Error Behavior

Milestone 2 includes the following controlled errors:

| Error Code | Tested | Result |
|---|---|---|
| `INVALID_JSON` | Yes | PASS |
| `INVALID_REQUEST` | Yes | PASS |
| `RESERVED_PLACEHOLDER_IN_INPUT` | Yes | PASS |
| `INVALID_PLACEHOLDER` | Yes | PASS |
| `UNKNOWN_PLACEHOLDER` | Yes | PASS |
| `PROVIDER_ERROR` | Yes | PASS |

When provider validation fails, the program does not produce a restored final output.

---

## 9. Detection Methods Evaluated

The Milestone 2 prototype uses two detection approaches.

### Exact Term-List Matching

Used for:

- `NAME`
- `ADDRESS`

These values are loaded from local synthetic data files.

This makes detection deterministic and easy to reproduce, but it only detects values that appear in the local lists.

### Structured Pattern Matching

Used for:

- `EMAIL`
- `PHONE`

Email addresses are detected using a documented regular-expression pattern.

Phone numbers are currently limited to the format:

```text
###-###-####
```

The current prototype does not attempt to recognize every possible phone-number or physical-address format.

---

## 10. Current Limitations

The following limitations remain at the end of Milestone 2:

- Names must appear in the local synthetic name list.
- Physical addresses must appear in the local synthetic address list.
- Exact name and address matching is case-sensitive.
- Phone-number detection currently supports only `###-###-####`.
- The email pattern supports common email formats but is not intended to validate every possible legal email address.
- Full overlap resolution is not implemented.
- Cross-request isolation is not yet evaluated.
- MASK/REMOVE policy is not implemented.
- A live AI provider is not used.
- The offline mock provider does not perform real qualification analysis.
- Prompt usefulness comparison is not part of Milestone 2.
- PDF, DOCX, OCR, and graphical interfaces are not supported.
- Only synthetic data is used.

These limitations are consistent with the intended Milestone 2 scope and will be reconsidered during later milestones where required.

---

## 11. Milestone 2 Evaluation Conclusion

The Milestone 2 prototype successfully completes one full request through the privacy-gateway pipeline.

All 10 automated tests passed.

The evaluation shows that the current prototype can:

- detect the supported sensitive-information categories;
- replace supported sensitive values with request-specific placeholders;
- preserve repeated sensitive values;
- distinguish different entities;
- prevent original sensitive values from appearing in the normal provider response;
- validate provider placeholders;
- reject unknown and malformed placeholders;
- restore valid values locally; and
- return controlled errors for tested invalid input and provider failures.

The current results support the conclusion that the Milestone 2 pipeline behaves correctly for the documented synthetic cases and supported input formats.