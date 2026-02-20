You are building a platform that generates legal documents through a conversation with a user. You have access to a template of a legal document (for e.g Will ) , but this needs to be personalised for each client. You need to design a system that :-

Collects user information through a structured conversation

Generates a legal document based on:

structured user data

a legal template

AI-assisted drafting

Applies rule-based validation checks before document output [DO NOT ATTEMPT THIS , ASSUME THIS EXISTS ALREADY]

Allows the company to add new legal document types in the future without modifying core code

Prevents:

invention of facts

advice beyond scope

prompt injection or manipulation

Additional Requirements
The system must be modular.

New document types must be added via configuration (not rewriting logic).

Outputs must be reproducible.

The system must handle:

contradictions in user answers

vague inputs (“quite a lot of savings”)

user asking for advice

The company wants to add a second document type within 10 days after V1 without core refactoring.