# ai-privacy-gateway

## Project Overview

This project is a local AI privacy gateway designed for resume analysis.

The intended user is a recruiter or Human Resources employee who wants to use
AI to summarize a candidate's qualifications without sending selected
personally identifiable information to the external AI provider.

The gateway will eventually:

1. Read resume text.
2. Detect supported sensitive information.
3. Replace sensitive values with placeholders.
4. Send only masked data to an AI or offline mock provider.
5. Validate placeholders in the provider response.
6. Restore authorized values locally.
7. Return the final output to the user.

The project uses synthetic data only.

## Current Milestone

### Milestone 1 - Requirements and Design

The complete privacy gateway is not implemented yet.

The current milestone includes:

- User and task definition
- Sensitive-data categories
- Success criteria and non-goals
- Programming-language comparison
- System architecture and privacy boundary
- Placeholder design
- Initial AI prompt
- Planned acceptance tests
- Basic Python Tech Spike

## Intended User

The intended user is a recruiter or HR employee reviewing job applications.

## AI-Assisted Task

The AI-assisted task is to generate a qualification summary from a candidate's
resume.

The summary may include:

- Education
- Professional experience
- Technical skills
- Relevant qualifications
- Missing or unclear qualifications

The system is not intended to make hiring decisions or rank candidates.

## Sensitive Information

The initial design focuses on:

- Candidate name
- Email address
- Phone number
- Physical Address

Example placeholders:

[[r1:NAME:1]]
[[r1:EMAIL:1]]
[[r1:PHONE:1]]
[[r1:ADDRESS:1]]

## Programming Language

The project will be implemented in Python.

Python was selected because the system relies heavily on text processing,
regular expressions, and AI-related tooling.

TypeScript was considered as an alternative.

## Requirements

- Python 3.14.7

Check the installed version with:

python --version

## Project Structure

Example:

AI-Privacy-Gateway/
|
|-- README.md
|-- tech_spike.py
|
|-- docs/
|   |-- DESIGN.md
|   |-- EVALUATION.md
|   |-- ASSISTANCE.md
|   |-- USER_GUIDE.md
|
|-- tests/
|
|-- src/


## Running the M1 Tech Spike

From the project directory, run:

python tech_spike.py

The program reads one line of text and prints it back to the user.

## Example

Command:

python tech_spike.py

Input:

Candidate has 3 years of Python experience.

Output:

Received text: Candidate has 3 years of Python experience.

## Planned M2 Pipeline

The next milestone will implement:

Input
  ->
Detection
  ->
Masking
  ->
Offline Mock Provider
  ->
Response Validation
  ->
Local Restoration
  ->
Final Output


## Documentation

Additional project documentation is located in the `docs` directory.

- `docs/DESIGN.md`
  - Requirements, language choice, architecture, prompt, state, and design
    decisions.

- `docs/EVALUATION.md`
  - Planned and executed test cases, results, failures, and limitations.

- `docs/ASSISTANCE.md`
  - Important AI, peer, library, or source assistance and how it was verified.

- `docs/USER_GUIDE.md`
  - Instructions for running the program, supported formats, warnings, and
    troubleshooting.

## Privacy and Data Policy

Only synthetic data should be used during development and testing.

Do not include:
- Real applicant records
- Real employee information
- API keys
- Passwords
- Live credentials
- Other private information

## Current Limitations

At Milestone 1:

- Sensitive-data detection is not implemented.
- Masking is not implemented.
- Response validation is not implemented.
- Restoration is not implemented.
- The provider is not implemented.
- PDF, DOCX, OCR, and graphical interfaces are not supported.
