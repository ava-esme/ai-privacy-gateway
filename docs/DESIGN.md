# DESIGN.md

## 1. Intended User
Recruiter or HR employee reviewing job applications.

## 2. AI-Assisted Task
Generate a qualification summary of a candidate's resume while
preventing personally identifiable information from being sent
to the external AI provider.

## 3. Motivation
Recruiters may want AI assistance summarizing qualifications,
but resumes contain personal information that does not need to
be exposed to the AI provider.

## 4. Sensitive Information Categories
- Person's name
- Email address
- Phone number
- Street address

## 5. Success Criteria
- Selected sensitive values are detected.
- Sensitive values are replaced before leaving the local system.
- Repeated values receive the same placeholder within a request.
- The AI output remains useful for resume qualification analysis.
- Unknown or invalid placeholders are not restored.

## 6. Non-Goals
- Hiring decisions
- Candidate ranking
- Background checks
- Sending real employee/applicant data to AI

## 7. M2 Scope
Milestone 2 will implement a complete and working 
privacy gateway. It will accept plain-text resumes,
but not PDFs or DOCXs.

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
- local program receives resume
- resume is scanned to detect any sensitive info
- sensitive info is replaced with placeholders
- placeholders are put into a local placholder map
- sanitized text is sent to external AI

----PRIVACY BOUNDARY----

- sanitized resume is summarized by AI
- AI provides summarized resume with same placeholders from local

----PRIVACY BOUNDARY----

- local system receives summarized, sanitized resume
- local system replaces placeholders with original information
- user recieves the summarized resume with the correct information restored

## 10. Component Responsibilities
### Input Component
Reads resume text.

### Detector
Finds supported sensitive information.

### Masker
Replaces detected values with placeholders.

### Placeholder Map
Stores placeholder → original value locally.

### Provider
Receives only masked text.

### Validator
Checks returned placeholders.

### Restorer
Restores only authorized placeholders.

## 11. Placeholder Format
Examples:
[[r1:NAME:1]]
[[r1:EMAIL:1]]
[[r1:PHONE:1]]
[[r1:ADDRESS:1]]

## 12. Initial Prompt
You are assisting a recruiter with analyzing a candidate's resume.

The resume has been sanitized to protect personally identifiable
information. Values such as [[r1:NAME:1]], [[r1:EMAIL:1]], [[r1:PHONE:1]], 
and [[r1:ADDRESS:1]] are placeholders.

Do not modify, invent, expand, or remove placeholders.

Analyze only the candidate's professional qualifications.

Provide:
1. Education
2. Relevant experience
3. Relevant technical skills
4. Qualifications matching the job requirements
5. Qualifications that are missing or unclear

Do not make a hiring decision.

RESUME:

{SANITIZED_RESUME}

## 13. Design Decisions
- The placholder map will be stored locally to prevent
any sensitive information from being sent to AI.
- It will begin with plain-text input to ensure the focus
remains on detection, masking, and restoration.