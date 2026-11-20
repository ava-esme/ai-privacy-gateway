# EVALUATION.md

## 1. Evaluation Goal

The goal of the evaluation is to verify that the Milestone 3 AI Privacy Gateway:

- detects the supported sensitive-information categories;
- masks or removes protected values before they reach the provider;
- preserves repeated sensitive values correctly;
- distinguishes different sensitive entities;
- resolves overlapping detections deterministically;
- keeps request mappings separate and releases request-local state after processing;
- validates provider responses before restoration;
- rejects malformed, unknown, and foreign-request placeholders;
- handles provider errors, timeouts, and malformed responses without an unmasked fallback;
- restores only valid MASK placeholders;
- does not restore REMOVE values; and
- produces useful AI output while preserving the privacy boundary.

The supported sensitive-information categories are:

- `NAME`
- `EMAIL`
- `PHONE`
- `ADDRESS`

All test data is synthetic.

---

## 2. Evaluation Environment

The gateway is implemented in Python and tested from the command line.

The automated test suite is located in:

`tests/test_pipeline.py`

Run the automated tests with:

```bash
python -m unittest discover -s tests -v
```

The detection-metrics evaluation is located in:

`evaluation_metrics.py`

Run it with:

```bash
python evaluation_metrics.py
```

The automated privacy-gateway tests use the deterministic offline mock provider.

A real AI model was used separately for the prompt-comparison experiment. Only masked synthetic input was used for that experiment.

---

## 3. Planned and Executed Evaluation Coverage

Milestone 3 expands the Milestone 2 evaluation to include detection accuracy, policy behavior, state lifetime, cross-request isolation, provider failures, response validation, and prompt usefulness.

The current automated suite includes tests for:

- normal supported input;
- repeated sensitive values;
- no sensitive information;
- different entities;
- deterministic overlap resolution;
- default MASK behavior;
- REMOVE behavior;
- invalid policy values;
- unknown placeholders;
- malformed placeholders;
- foreign-request placeholders;
- independent requests;
- mapping cleanup;
- reserved placeholder syntax in original input;
- provider errors;
- provider timeouts;
- malformed provider responses; and
- invalid JSON.

Two additional response cases required by the M3 evaluation plan were also executed:

- provider response with a missing previously issued placeholder;
- provider response with a modified previously issued placeholder.

Both cases passed.

---

## 4. Milestone 1 and Milestone 2 Acceptance Cases

The original acceptance cases remain part of the M3 regression suite.

### Normal Input

Purpose:

Verify that supported sensitive values are detected and protected before the provider receives the text, and that valid MASK placeholders are restored locally.

Example input:

```text
Jane Smith lives at 123 Example Street, Sampletown, GA 30000.
Contact Jane Smith at jane.smith@example.com or 478-555-1234.
```

Expected protected values:

```text
[[r1:NAME:1]]
[[r1:ADDRESS:1]]
[[r1:EMAIL:1]]
[[r1:PHONE:1]]
```

Result:

**PASS**

### Repeated Sensitive Values

Purpose:

Verify that repeated occurrences of the same value reuse the same request-local placeholder.

Example:

```text
Jane Smith has Python experience.
Contact Jane Smith at jane.smith@example.com.
```

The repeated name reuses:

```text
[[r2:NAME:1]]
```

and does not create `[[r2:NAME:2]]`.

Result:

**PASS**

### No Sensitive Information

Purpose:

Verify that ordinary text is not unnecessarily changed.

Example:

```text
Candidate has four years of Python experience and experience with AWS.
```

Result:

**PASS**

### Different Entities

Purpose:

Verify that different sensitive values within the same category receive different placeholders.

Example:

```text
Jane Smith worked with John Davis on a Python project.
```

Result:

**PASS**

### Reserved Placeholder Syntax in Input

Purpose:

Verify that a user cannot supply text containing syntax reserved for gateway-generated placeholders.

Example:

```text
Jane Smith worked on [[r17:NAME:1]].
```

Expected error:

```text
RESERVED_PLACEHOLDER_IN_INPUT
```

Result:

**PASS**

### Invalid JSON

Purpose:

Verify that malformed JSON produces a controlled error.

Expected error:

```text
INVALID_JSON
```

Result:

**PASS**

---

## 5. Milestone 3 Automated Gateway Tests

The M3 suite contains 22 executed automated tests.

Observed result:

```text
Ran 22 tests in 0.009s

OK
```

Summary:

- Tests executed: 22
- Tests passed: 22
- Tests failed: 0

### Executed Test Summary

| Test | Purpose | Result |
|---|---|---|
| Normal input | Full supported pipeline behavior | PASS |
| Repeated sensitive value | Reuse same placeholder | PASS |
| No sensitive information | Leave ordinary text unchanged | PASS |
| Different entities | Distinct placeholders for distinct values | PASS |
| Longer overlapping match | Longer same-start detection wins | PASS |
| Earlier overlapping match | Earlier-starting detection wins | PASS |
| Missing policies default to MASK | Verify default policy | PASS |
| REMOVE policy | Removed value is not sent or restored | PASS |
| Invalid policy | Controlled `INVALID_POLICY` error | PASS |
| Unknown placeholder | Reject unissued placeholder | PASS |
| Malformed placeholder | Reject malformed reserved token | PASS |
| Foreign-request placeholder | Reject another request's placeholder | PASS |
| Independent requests | Keep mappings isolated | PASS |
| Mapping clear | Release mapping contents | PASS |
| Pipeline mapping cleanup | Cleanup occurs after processing | PASS |
| Reserved placeholder in input | Reject reserved syntax in original input | PASS |
| Provider error | Controlled provider failure | PASS |
| Provider timeout | Controlled timeout | PASS |
| Malformed provider response | Reject non-text provider result | PASS |
| Invalid JSON | Controlled JSON error | PASS |

### Additional M3 Response Tests

Two additional response cases were added and executed:

| Test | Intended Behavior | Result |
|---|---|---|
| Missing placeholder response | Provider omits an issued placeholder; omitted value is not restored | PASS |
| Modified placeholder response | Provider changes an issued placeholder; changed token is rejected | PASS |

---

## 6. Deterministic Overlap Evaluation

Milestone 3 added deterministic overlap handling.

The documented rules are:

1. Earlier starting position wins.
2. If two detections begin at the same position, the longer detection wins.
3. If the start position and length are equal, category priority is used.
4. A later candidate that overlaps an already accepted detection is discarded.

### Longer Same-Start Match

Example candidates:

```text
123 Example Street
123 Example Street, Sampletown, GA 30000
```

Both begin at the same position.

Observed winner:

```text
123 Example Street, Sampletown, GA 30000
```

Result:

**PASS**

### Earlier-Starting Match

When two detections overlap but one begins earlier, the earlier match is retained.

Result:

**PASS**

---

## 7. Policy Evaluation

The gateway supports two category policies:

- `MASK`
- `REMOVE`

### MASK

The sensitive value is replaced with a request-local placeholder before the provider receives the text.

A valid authorized placeholder may be restored locally after provider-response validation succeeds.

### REMOVE

The sensitive value is removed before the provider receives the text.

REMOVE values are not stored in the request mapping and therefore cannot be restored later.

### Missing Policy Rule

If a category is not included in the supplied policy object, the category defaults to:

```text
MASK
```

Observed result:

**PASS**

### Invalid Policy Rule

Example invalid policy:

```text
HIDE
```

Observed error:

```text
INVALID_POLICY
```

Result:

**PASS**

---

## 8. Request State and Mapping Lifetime

Each request receives its own `RequestMapping`.

Testing confirmed that placeholders generated for one request are not shared with another request.

Example:

```text
Request r13 -> [[r13:NAME:1]]
Request r14 -> [[r14:NAME:1]]
```

The pipeline releases request-local mapping state after processing.

The mapping cleanup is placed in a `finally` block, so cleanup occurs after both successful and failed processing paths.

Testing confirmed that a mapping can be cleared to zero stored entries.

Result:

**PASS**

---

## 9. Placeholder Validation and Restoration

The validator distinguishes multiple placeholder conditions.

### Valid Placeholder

Example:

```text
[[r1:NAME:1]]
```

If the placeholder belongs to the current request and was issued by its mapping, it may be restored.

Result:

**PASS**

### Unknown Placeholder

Example:

```text
[[r5:NAME:999]]
```

The syntax is valid, but the placeholder was never issued for the current request.

Observed error:

```text
UNKNOWN_PLACEHOLDER
```

Result:

**PASS**

### Malformed Placeholder

Example:

```text
[[r11:NAME]]
```

Observed error:

```text
INVALID_PLACEHOLDER
```

Result:

**PASS**

### Foreign-Request Placeholder

Example:

```text
[[r999:NAME:1]]
```

When the current request has another request ID, the token is well formed but unauthorized.

Observed error:

```text
FOREIGN_REQUEST_PLACEHOLDER
```

Result:

**PASS**

### Missing Placeholder Response

Planned behavior:

If the provider simply omits a placeholder that was present in the masked request, there is no unauthorized token to restore. The response may still pass privacy validation, but the omitted original value cannot be restored.

This is treated as a task-usefulness/restoration issue rather than an outbound privacy leak.

Result:

**PASS**

### Modified Placeholder Response

Planned behavior:

If the provider changes an issued token into a different valid-looking token that was not issued for the request, the modified token must not be restored.

Expected error:

```text
UNKNOWN_PLACEHOLDER
```

Result:

**PASS**

---

## 10. Provider Failure Evaluation

The offline mock provider was used to simulate controlled failure modes.

### Provider Error

Observed error:

```text
PROVIDER_ERROR
```

Result:

**PASS**

### Provider Timeout

Observed error:

```text
PROVIDER_TIMEOUT
```

Result:

**PASS**

### Malformed Provider Response

A non-text response produced:

```text
MALFORMED_PROVIDER_RESPONSE
```

Result:

**PASS**

### Malformed Placeholder Response

Observed error:

```text
INVALID_PLACEHOLDER
```

Result:

**PASS**

### Foreign Placeholder Response

Observed error:

```text
FOREIGN_REQUEST_PLACEHOLDER
```

Result:

**PASS**

In each tested failure case, processing stops with a controlled error. The gateway does not send the original unmasked input as a fallback.

---

## 11. Detection Methods Evaluated

The system uses two documented detection approaches.

### Exact Term-List Matching

Used for:

- `NAME`
- `ADDRESS`

These values are loaded from local synthetic data files.

This method is deterministic and reproducible, but it only detects exact values that appear in the local lists.

### Structured Pattern Matching

Used for:

- `EMAIL`
- `PHONE`

Email addresses are detected with a regular-expression pattern.

Phone numbers currently support:

```text
###-###-####
```

---

## 12. Quantitative Detection Evaluation

Detection was evaluated using labeled synthetic cases.

A true positive (TP) is a protected-value occurrence that was correctly detected.

A false positive (FP) is a value incorrectly detected as sensitive.

A false negative (FN) is a labeled sensitive-value occurrence that was not detected.

Precision:

```text
TP / (TP + FP)
```

Recall:

```text
TP / (TP + FN)
```

### Case 1: Normal Supported Input

Observed result:

```text
TP: 5
FP: 0
FN: 0
Precision: 1.000
Recall: 1.000
Outbound privacy leaks: 0
```

The repeated name is counted as two separate occurrences.

### Case 2: Repeated Value with Punctuation

Observed result:

```text
TP: 3
FP: 0
FN: 0
Precision: 1.000
Recall: 1.000
Outbound privacy leaks: 0
```

### Case 3: Unicode Text

The case included Unicode text such as `Résumé`.

Observed result:

```text
TP: 2
FP: 0
FN: 0
Precision: 1.000
Recall: 1.000
Outbound privacy leaks: 0
```

### Case 4: Unsupported Phone Format

The test used:

```text
(478) 555-0199
```

The current detector only supports the documented phone format:

```text
###-###-####
```

Observed result:

```text
TP: 0
FP: 0
FN: 1
Precision: N/A
Recall: 0.000
Outbound privacy leaks: 1
```

False negative:

```text
('PHONE', '(478) 555-0199', 28, 42)
```

### Overall Detection Results

```text
TP: 10
FP: 0
FN: 1
Precision: 1.000
Recall: 0.909
Outbound privacy leaks: 1
```

The single false negative and outbound privacy leak were caused by the deliberately tested unsupported phone-number format.

---

## 13. Privacy Boundary Evaluation

For supported detection formats, original protected values are removed from the outbound provider payload.

MASK values are replaced with placeholders such as:

```text
[[r1:NAME:1]]
```

The placeholder-to-original-value mapping remains local.

Across the supported labeled detection cases, there were zero outbound privacy leaks.

One outbound leak occurred in the deliberately unsupported phone-format case because the value was not recognized by the detector.

This shows that the privacy boundary depends on the documented detection coverage. A value that is not detected cannot be protected by the masker.

---

## 14. Prompt Comparison

Two prompt versions were evaluated using the same three synthetic masked resume cases.

The automated gateway tests used the deterministic offline mock provider.

The prompt experiment was performed separately with a real AI model using only masked synthetic input.

The comparison considered:

- task usefulness;
- required information;
- output format;
- correct placeholder preservation; and
- unsupported or invented information.

### Prompt Version 1

Prompt Version 1 asked for a short qualification summary focused on technical skills, relevant experience, education or training, and overall qualifications. It also instructed the model not to modify placeholders or invent qualifications.

#### Case 1

The response preserved `[[r201:NAME:1]]` and included the programming languages and team web-development project.

However, it added interpretive statements about foundational programming knowledge, teamwork skills, and suitability for entry-level software-development positions or internships.

Result:

**Useful, but contained minor unsupported interpretation.**

#### Case 2

The response preserved `[[r202:NAME:1]]` and included three years of Python development experience, AWS, MySQL, Git, and collaboration.

It also stated that the candidate demonstrated qualifications relevant to collaborative software-development roles.

Result:

**Useful, but contained a minor interpretive conclusion.**

#### Case 3

The response preserved `[[r203:NAME:1]]` and included the Computer Science degree, Java, C++, and missing professional development, certification, and cloud experience.

It also interpreted the education as relevant to entry-level software-development positions and stated that missing experience limited assessment of practical qualifications.

Result:

**Accurate overall, but contained minor unsupported interpretation.**

### Prompt Version 2

Prompt Version 2 required exactly these sections:

```text
Qualification Summary
Key Qualifications
Missing Information
```

It also explicitly required the model to use only supplied facts, avoid inference, preserve placeholders exactly, and never guess the original protected values.

#### Case 1

The response preserved `[[r201:NAME:1]]`, identified the Computer Science background, programming languages, web technologies, and team-project experience, and clearly separated missing information.

Result:

**Accurate, structured, and no unsupported qualifications were introduced.**

#### Case 2

The response preserved `[[r202:NAME:1]]` and accurately summarized the three years of Python development experience, AWS, MySQL, Git, and collaboration.

Result:

**Accurate, structured, and no unsupported conclusions were introduced.**

#### Case 3

The response preserved `[[r203:NAME:1]]` and accurately summarized the Computer Science degree and Java/C++ skills while keeping missing experience in the Missing Information section.

Result:

**Accurate, structured, and no unsupported qualifications were introduced.**

### Prompt Comparison Result

Prompt Version 2 performed better overall.

Both prompts preserved placeholders correctly and produced useful recruiter-oriented responses. Prompt Version 1 introduced minor interpretive conclusions in all three cases, while Prompt Version 2 remained more closely constrained to the supplied facts.

Prompt Version 2 was selected as the preferred prompt because it:

- preserved all privacy placeholders exactly;
- used only information supported by the masked input;
- reduced unsupported inference;
- produced a consistent recruiter-friendly format; and
- clearly separated known qualifications from missing information.

The prompt experiment also demonstrates that privacy protection and AI usefulness are separate concerns. The gateway controls what sensitive values may leave the local system, while prompt design affects output quality and factual discipline.

---

## 15. Current Failures and Limitations

The current system has the following documented limitations:

- Names must appear in the local synthetic name list.
- Physical addresses must appear in the local synthetic address list.
- Exact name and address matching is case-sensitive.
- Phone detection currently supports only `###-###-####`.
- `(478) 555-0199` was not detected in the labeled evaluation and produced one outbound privacy leak.
- The email pattern supports common formats but is not intended to validate every possible legal email format.
- The system is single-turn.
- The automated pipeline uses an offline mock provider rather than a live AI API.
- The mock provider does not perform real qualification analysis.
- PDF, DOCX, OCR, and graphical interfaces are not supported.
- Only synthetic data is used.
- Prompt Version 1 demonstrated that successful masking does not guarantee that AI output will avoid unsupported interpretation.

---

## 16. Current M3 Evaluation Conclusion

The current Milestone 3 implementation successfully demonstrates the required privacy-gateway behavior for the documented supported formats.

The automated test result is:

```text
22 tests executed
22 tests passed
0 tests failed
```

The quantitative detection result is:

```text
TP: 10
FP: 0
FN: 1
Precision: 1.000
Recall: 0.909
Outbound privacy leaks: 1
```

The single false negative and leak were caused by a deliberately tested unsupported phone-number format.

The prompt comparison showed that both prompt versions preserved privacy placeholders, but Prompt Version 2 produced more consistent, structured, and fact-constrained recruiter output.

The missing-placeholder and modified-placeholder response cases were both executed successfully. With those cases included, the M3 automated suite contains 22 passing tests and the planned M3 evaluation coverage is complete.
