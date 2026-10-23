# AI Privacy Gateway - Resume Qualification Analysis

## Project Overview

This project is a local AI privacy gateway designed to protect sensitive information in resume text before it is processed by an AI-style provider.

The intended user is a recruiter or Human Resources employee who wants assistance summarizing a candidate's qualifications without exposing selected personally identifiable information to the provider.

For Milestone 2, the system uses a deterministic offline mock provider rather than a live AI API.

The complete pipeline is:

`Input -> Detection -> Masking -> Offline Mock Provider -> Validation -> Restoration -> Output`

## Supported Sensitive Information

The Milestone 2 prototype supports four categories of sensitive information:

- Name
- Email address
- Phone number
- Physical address

Names and physical addresses are detected using exact matching against local synthetic term lists.

Email addresses and phone numbers are detected using structured regular-expression patterns.

## Placeholder Format

Sensitive values are replaced with request-specific placeholders using the format:

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

Repeated occurrences of the same sensitive value reuse the same placeholder within a request.

Different sensitive values within the same category receive different indexes.

## Privacy Boundary

The following remain local:

- Original resume text
- Detected sensitive values
- Placeholder mappings
- Validation logic
- Restoration logic

The provider receives only masked text.

The placeholder-to-original-value mapping is never sent to the provider.

## Requirements

- Python 3.13.17
- Command-line terminal
- Project files
- Synthetic data files

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
|-- masker.py
|-- mock_provider.py
|-- validator.py
|-- restorer.py
|-- pipeline.py
|-- main.py
|-- README.md
```

## Running the Program

From the project root, run:

```bash
python main.py
```

The program will prompt for a JSON request.

Enter the request on one line.

Example:

```json
{"request_id":"r1","text":"Jane Smith lives at 123 Example Street, Sampletown, GA 30000. Jane Smith has 3 years of Python experience. Contact Jane Smith at jane.smith@example.com or 478-555-1234."}
```

## Example Successful Output

```json
{
    "status": "ok",
    "request_id": "r1",
    "masked_text": "[[r1:NAME:1]] lives at [[r1:ADDRESS:1]]. [[r1:NAME:1]] has 3 years of Python experience. Contact [[r1:NAME:1]] at [[r1:EMAIL:1]] or [[r1:PHONE:1]].",
    "provider_response": "Qualification Summary:\n[[r1:NAME:1]] lives at [[r1:ADDRESS:1]]. [[r1:NAME:1]] has 3 years of Python experience. Contact [[r1:NAME:1]] at [[r1:EMAIL:1]] or [[r1:PHONE:1]].",
    "output": "Qualification Summary:\nJane Smith lives at 123 Example Street, Sampletown, GA 30000. Jane Smith has 3 years of Python experience. Contact Jane Smith at jane.smith@example.com or 478-555-1234."
}
```

## JSON Input Format

Each request must contain:

```json
{
  "request_id": "r1",
  "text": "resume text"
}
```

### `request_id`

The request ID must:

- Be a string
- Begin with lowercase `r`
- Be followed by a positive integer

Examples:

```text
r1
r2
r15
```

### `text`

The `text` field contains the plain-text synthetic resume information to process.

It must be:

- Present
- A string
- Non-empty

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

Controlled errors return:

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

## Controlled Error Codes

The current prototype supports:

- `INVALID_JSON`
- `INVALID_REQUEST`
- `RESERVED_PLACEHOLDER_IN_INPUT`
- `INVALID_PLACEHOLDER`
- `UNKNOWN_PLACEHOLDER`
- `PROVIDER_ERROR`

## Running the Automated Tests

From the project root, run:

```bash
python -m unittest discover -s tests -v
```

The current test suite contains 10 automated tests.

The tests cover:

- Normal input
- Repeated sensitive values
- No sensitive information
- Unknown placeholders
- Malformed placeholders
- Different entities within one request
- Reserved placeholder syntax
- Provider failure
- Invalid JSON
- Missing required fields

Current observed result:

```text
Ran 10 tests in 0.003s

OK
```

## Detection Methods

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

The current supported format is:

```text
###-###-####
```

Example:

```text
478-555-1234
```

## Offline Mock Provider

Milestone 2 uses a deterministic offline mock provider.

The mock provider allows the full privacy-gateway pipeline to be tested without:

- Internet access
- API keys
- Live AI services
- Real private data

The mock provider also supports test modes for:

- Unknown placeholders
- Malformed placeholders
- Provider failures

## Current Limitations

The Milestone 2 prototype does not support:

- PDF files
- DOCX files
- OCR
- Live AI APIs
- Graphical interfaces
- Multi-turn conversations
- Every possible name or physical address
- Every possible phone-number format
- MASK/REMOVE category policy
- Cross-request isolation testing
- Prompt comparison

Name and address detection currently depend on exact, case-sensitive matches in local synthetic term lists.

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

## Documentation

Additional project documentation is located in the `docs` folder.

### `docs/DESIGN.md`

Contains:

- Requirements
- Architecture
- Sensitive-information categories
- Placeholder format
- JSON I/O contract
- Language choice
- Design decisions

### `docs/EVALUATION.md`

Contains:

- Automated test cases
- Executed results
- End-to-end pipeline evidence
- Error handling
- Current limitations

### `docs/USER_GUIDE.md`

Contains:

- Detailed instructions for running the program
- Supported formats
- Example inputs and outputs
- Troubleshooting

### `docs/ASSISTANCE.md`

Records important AI, peer, library, and source assistance along with how that assistance was checked or verified.