# Test Plan: Book tickets for an event

## API tests

| ID  | Test | AC | Priority |
|-----|------|----|----------|
| A1  | Create booking → 201, status `confirmed`, booking ref returned, customer fields echoed back | AC1, AC5 | Smoke |
| A2  | `totalPrice` = event price × quantity (quantity 1, 3, 10; decimal price) | AC2 | High |
| A3  | Created booking can be found by id, by reference and in the bookings list | AC3 | High |
| A4  | Cancel booking → 200; booking then returns 404 and is gone from the list | AC4 | High |
| A5  | Available seats drop by the quantity booked and are restored on cancel | AC5 | High |
| A6  | Quantity outside 1–10 (0, 11) → 400 validation error | — | Medium |
| A7  | Invalid customer data → 400 naming the bad field (name < 2 chars, bad email, phone < 10 chars, letters in phone, missing field) | — | Medium |
| A8  | More tickets than seats left → 400 | — | Medium |
| A9  | Booking for a non-existent event → 404 | — | Medium |
| A10 | No token / invalid token → 401 | — | High |
| A11 | Cancel a non-existent booking → 404 | AC4 | Low |
| A12 | Booking ref matches documented format `EVT-XXXXXX` — **xfail, known bug** | AC1 | Bug |
| A13 | `totalPrice` returned as a number, as documented — **xfail, known bug** | AC2 | Bug |
| A14 | Framework check: the session token belongs to the configured account (`GET /auth/me`) | — | Medium |

## UI tests

| ID | Test | AC | Priority |
|----|------|----|----------|
| U1 | Book tickets on the event page → confirmation shows booking ref, customer, ticket count, and total = price × quantity | AC1, AC2 | Smoke |
| U2 | Booking made in the UI appears in My Bookings with the same reference | AC3 | High |
| U3 | Cancel a booking from My Bookings (booking created via API) → booking disappears | AC4 | High |
| U4 | Submitting the form empty shows a validation message for each field | — | Medium |
| U5 | Confirmation total = price × quantity: whole price passes; decimal price **xfail, known bug** (UI rounds to whole dollars) | AC2 | Bug |
