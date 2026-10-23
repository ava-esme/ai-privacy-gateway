# DESIGN.md

## 1. Intended User
Recruiter or HR employee reviewing job applications.

## 2. AI-Assisted Task
Generate a qualification summary of a candidate's resume while
preventing personally identifiable information from being sent
to the external AI provider.

For Milestone 2, the provider is a deterministic offline mock provider.
This allows the complete privacy-gateway pipeline to be tested without
sending any data to an external service.

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

The Milestone 2 prototype does not attempt to recognize every possible
phone-number format.

### Physical Address
Physical addresses will be detected using exact matching against a local
synthetic address term list.

Example:

`123 Example Street, Sampletown, GA 30000`

Placeholder:

`[[r1:ADDRESS:1]]`

The Milestone 2 prototype will only detect physical addresses that appear
in the local synthetic term list. It will not attempt to recognize every
possible address format.

## 5. Success Criteria
- Supported sensitive values are detected.
- Sensitive values are replaced locally before they reach the provider.
- The placeholder-to-original-value mapping remains local.
- Repeated sensitive values receive the same placeholder within one request.
- Different sensitive values within the same category receive different placeholders.
- The mock provider receives only masked text.
- The provider response is validated before restoration occurs.
- Unknown or malformed reserved placeholders produce controlled errors.
- Valid placeholders are restored locally.
- The final output remains useful for resume qualification analysis.
- The M1 acceptance cases are implemented as automated tests.

## 6. Non-Goals
The following are not required for Milestone 2:

- Hiring decisions
- Candidate ranking
- Background checks
- Sending real employee/applicant data to AI
- Detecting every possible representation of sensitive information
- PDF or DOCX parsing
- OCR
- A graphical user interface
- A live AI API
- Multi-turn conversations
- MASK/REMOVE category policy
- Cross-request isolation testing
- Prompt comparison


## 7. M2 Scope
Milestone 2 implements one complete and working privacy-gateway request:

`Input -> Detection -> Masking -> Offline Mock Provider -> Validation -> Restoration -> Output`

The prototype accepts plain-text resume content through a JSON request.

The Milestone 2 implementation includes:

- NAME, EMAIL, PHONE, and ADDRESS categories
- Exact matching using local synthetic term lists
- Structured regular-expression matching
- Local masking
- Request-local placeholder mappings
- A deterministic offline mock provider
- Provider-response validation
- Local restoration
- Repeated-value handling
- Different-entity handling within one request
- Controlled errors for invalid reserved placeholders
- Automated acceptance tests
- JSON input and output


## 8. Programming Language Choice
### Selected Language: Python
Python will be used to complete this project because the 
program deals primarily with text processing, sensitive-information 
detection and AI integration, all of which are strong in Python. 

### Alternative: TypeScript
Compare at least two relevant differences:
- Python has a larger NLP and machine learning ecosystem than TypeScript.
- TypeScript has stronger static typing and the ability to use the same
language for front-end and back-end, but the text-processing abilities
and machine learning ecosystem of Python are more relevant to this project.

## 9. Architecture / Data Flow
### Local / Trusted System
1. The local program receives a JSON request containing a request ID and
   plain-text resume content.
2. The input is checked for valid JSON fields and reserved placeholder syntax.
3. The detector finds supported names, email addresses, phone numbers, and
   physical addresses.
4. The masker replaces each detected value with a request-specific placeholder.
5. The original values and placeholders are stored in a request-local map.
6. Only the masked text is passed to the offline mock provider.

`---- PROVIDER BOUNDARY ----`

### Offline Mock Provider
7. The deterministic offline mock provider receives the masked resume text.
8. The mock provider returns a predictable response that may contain the same
   placeholders it received.

`---- PROVIDER BOUNDARY ----`

### Local / Trusted System
9. The validator checks all reserved placeholders in the provider response.
10. If validation fails, the system returns a controlled error and does not
    restore values.
11. If validation succeeds, the restorer replaces valid placeholders with
    their original values.
12. The program returns a JSON result containing the masked text, provider
    response, and final restored output.

The placeholder mapping never crosses the provider boundary.

## 10. Component Responsibilities
### Input Component
Reads and validates the JSON request.

The input must contain:

- `request_id`
- `text`

### Detector
Finds supported sensitive information.

Detection methods for Milestone 2:

- NAME: exact matching from a local synthetic name list
- ADDRESS: exact matching from a local synthetic address list
- EMAIL: regular-expression pattern
- PHONE: regular-expression pattern

### Masker
Replaces detected values with request-specific placeholders.

If the same sensitive value appears multiple times in one request, the masker
reuses the same placeholder.

Different values within the same category receive different indexes.

### Placeholder Map
Stores placeholder-to-original-value mappings locally for the current request.

Example:

`[[r1:NAME:1]] -> Jane Smith`

`[[r1:EMAIL:1]] -> jane.smith@example.com`

`[[r1:PHONE:1]] -> 478-555-1234`

`[[r1:ADDRESS:1]] -> 123 Example Street, Sampletown, GA 30000`

The mapping is not included in the provider request or returned as part of the
normal JSON output.

### Offline Mock Provider
Receives only masked text and returns a deterministic response.

The mock provider is used instead of a live AI API so the pipeline can be
tested offline and reproduced consistently.

### Validator
Checks reserved placeholders in the mock provider response before restoration.

A returned placeholder must:

1. use the valid reserved placeholder format; and
2. have been issued for the current request.

Malformed or unknown placeholders produce controlled errors.

### Restorer
Restores only valid placeholders after validation succeeds.

If validation fails, restoration does not occur.

## 11. Placeholder Format
The Milestone 2 placeholder format is:

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

Supported Milestone 2 categories are:

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

## 12. Initial Prompt
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
- Contains the synthetic plain-text resume content to process

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

### M2 Error Codes

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

#### `PROVIDER_ERROR`
The offline mock provider failed unexpectedly.

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

## 14. Request-Local State

Each request creates its own placeholder mapping.

For example:

`[[r1:NAME:1]] -> Jane Smith`

`[[r1:ADDRESS:1]] -> 123 Example Street, Sampletown, GA 30000`

The mapping exists locally for the current request and is used during
restoration after the provider response has been validated.

Cross-request isolation is not part of the required Milestone 2 scope and will
be handled in a later milestone.

## 15. Offline Mock Provider Design

Milestone 2 uses a deterministic offline mock provider instead of a live AI
service.

The mock provider's purpose is to simulate the provider step while keeping the
prototype reproducible and completely offline.

The same masked input should produce the same mock response every time.

The mock provider preserves valid placeholders so that response validation and
local restoration can be tested.

## 16. Initial Prompt

The initial prompt remains:

You are assisting a recruiter with analyzing a candidate's resume.

The resume has been sanitized to protect personally identifiable
information. Values such as `[[r1:NAME:1]]`, `[[r1:EMAIL:1]]`,
`[[r1:PHONE:1]]`, and `[[r1:ADDRESS:1]]` are placeholders.

Do not modify, invent, expand, or remove placeholders.

Analyze only the candidate's professional qualifications.

Provide:

1. Education
2. Relevant experience
3. Relevant technical skills
4. Qualifications matching the job requirements
5. Qualifications that are missing or unclear

Do not make a hiring decision.
Do not invent qualifications that are not present in the resume.

RESUME:

`{SANITIZED_RESUME}`

For Milestone 2, the offline mock provider does not perform real AI analysis.
The prompt documents the intended provider behavior and can be used by a later
provider implementation.

## 17. Design Decisions

- The placeholder map is stored locally so original sensitive values are not
  sent to the provider.
- The system begins with plain-text resume input so the project remains focused
  on detection, masking, validation, and restoration.
- Names and physical addresses use exact matching against local synthetic term
  lists so their detection behavior is deterministic and easy to test.
- Email addresses and phone numbers use documented structured patterns.
- Request IDs are included in placeholders so placeholders can be associated
  with the request that created them.
- Repeated sensitive values reuse an existing placeholder instead of creating a
  new one.
- Different values within the same category receive separate indexes.
- The provider is a deterministic offline mock for Milestone 2.
- Provider responses are validated before any local restoration occurs.
- JSON is used for program input and output so requests and results have a
  consistent, testable structure.
- Reserved `[[...]]` syntax in original input produces a controlled error.

## 18. Changes From Milestone 1

Milestone 1 defined the intended user, task, privacy boundary, placeholder
format, and initial design.

Milestone 2 refines that design into a working prototype by:

- defining NAME, EMAIL, PHONE, and ADDRESS as the implemented M2 categories;
- specifying exact term-list detection for names and physical addresses;
- specifying structured patterns for email addresses and phone numbers;
- defining the JSON input/output contract;
- replacing the planned external provider with a deterministic offline mock;
- defining repeated-value and different-entity behavior;
- defining response-validation behavior and controlled placeholder errors; and
- connecting the individual components into one complete request pipeline.
