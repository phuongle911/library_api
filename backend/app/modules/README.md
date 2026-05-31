# Modular Service Boundaries

This project is currently a modulaar monolith.

The goal is to keep service boundaries clear before splitting into real microservices.

## User Service

Owns:

- users
- authentication
- refresh tokens
- roles / permissions

Other services should not directly modify user data

## Book Service

Owns:

- books
- categories
- inventory / available copies

Other services should not directly modify book data except through Book Service logic/client.

## Borrow Service

Owns:

- borrow records
- borrow rules
- return rules
- idempotency for borrow actions

Borrow Service communicates with User Service and Book Service through clients.

## Rule

Each service owns itss data and business rules.

Current communication is internal Python calls.

Future communication can beecome HTTP or async events without changing borrow business logic.