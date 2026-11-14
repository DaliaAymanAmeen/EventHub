# EventHub — QA Automation (US-114: Book tickets)

![Tests](https://github.com/DaliaAymanAmeen/eventhub-qa-automation/actions/workflows/tests.yml/badge.svg)

UI and API test automation for the EventHub ticket-booking flow, built with
**Playwright for Python** and **pytest**.

- **28 tests:** 25 pass, 3 are expected failures (`xfail`) that document real bugs
- **API-first:** 22 API tests cover the business rules; 6 UI tests cover the user journey
- **Self-contained:** each run creates its own test data and removes it afterwards

> **Language choice:** the brief allows "Playwright". I used Playwright's Python
> bindings for both UI and API testing — one tool, one language, one report.

---

## How to run

### CI

GitHub Actions runs the full suite on every push and pull request
([`.github/workflows/tests.yml`](.github/workflows/tests.yml)). The HTML report and
any failure traces are attached to each run as the `test-report` artifact.

### Locally
**Prerequisites:** Python 3.10+ and Git.

```bash
git clone https://github.com/DaliaAymanAmeen/eventhub-qa-automation.git
cd eventhub-qa-automation

python -m venv .venv
.venv\Scripts\activate            # Windows
# source .venv/bin/activate       # macOS / Linux

pip install -r requirements.txt
playwright install chromium

pytest
```

| Command | Runs |
|---|---|
| `pytest` | Everything (28 tests) |
| `pytest -m api` | API tests only |
| `pytest -m ui` | UI tests only |
| `pytest -m smoke` | Critical path only (2 tests) |

**Results:** an HTML report is written to `reports/report.html`.

### Credentials

The tests use a dedicated EventHub test account. Its credentials are committed in
`.env`, so the tests run straight after cloning. To use your own account, register at
https://eventhub.rahulshettyacademy.com/register and replace the values in `.env`.

> `.env` is committed only because the submission requires it. It holds credentials
> for a throwaway test account. In a real project they would live in CI secrets and
> `.env` would be gitignored.

---

## Story review (US-114)

### What's wrong
- **"As a visitor"** — booking requires login (the site redirects to `/login`, and
  bookings are private per account). The persona should be a registered user.
- **AC5 "the same works through the API"** — "the same" isn't testable. Which
  responses, validations and errors are expected?

### What's missing
- **Limits:** quantity must be 1–10 (API and UI enforce it; the story doesn't say).
- **Validation rules and messages** for name, email and phone.
- **Sold out / not enough seats:** what should the user see?
- **Booking reference format** (the docs say `EVT-XXXXXX`).
- **Pricing:** currency, rounding of decimal prices.
- **Past events:** can they be booked?

### What's unclear
- **AC4:** after cancelling, does the booking disappear or stay as "Cancelled"? The
  docs describe both a `cancelled` status and a permanent delete.
- **AC3:** sort order of My Bookings; are cancelled bookings shown?

### Questions for the Product Owner
1. Must the user be logged in to book? If so, can we update the persona?
2. Is the 1–10 ticket limit intended? What should the UI show at the limit?
3. What are the validation rules for name, email and phone, and what message should the user see for each?
4. Should cancelled bookings stay visible as "Cancelled", or be removed?
5. Can past events be booked? Should they be listed as "Upcoming"?
6. How should prices with cents be shown and rounded?
7. Is the booking reference format part of the requirement?
8. In what order should My Bookings list bookings (newest first, by event date)?


### App vs story / docs — findings

| # | Finding | Where | Severity |
|---|---|---|---|
| 1 | **UI rounds prices to whole dollars:** an event priced $99.99 shows as $100; 3 tickets show $300 while the backend stores $299.97 | UI | High |
| 2 | **Login reveals which emails exist:** wrong password → 400, unknown email → 404 (user enumeration) | API | Medium |
| 3 | **Booking ref format differs from docs:** `H-QCEQEM` instead of `EVT-XXXXXX` | API | Medium |
| 4 | **`price` / `totalPrice` returned as strings** (`"299.97"`); docs say numbers | API | Medium |
| 5 | **Cancel is a hard delete:** the `cancelled` status in the docs is never used | API / docs | Medium |
| 6 | **Past events listed as "Upcoming" and bookable** (all 3 demo events are dated before today) | UI | Medium |
| 7 | **API docs can't be used to test bookings or events:** every request from the docs page returns 401, even after signing in with "Authorize". The docs only mark `/auth/me` as needing a token, so the token isn't sent to the other endpoints | Docs | Medium |
| 8 | **Phone rules inconsistent:** UI says "10-digit phone" but accepts `+91-9876543210`; API allows digits, `+ - ( )` and spaces | UI / API | Low |

Findings 1, 3 and 4 are covered by `xfail(strict=True)` tests, so they appear in
every report and the suite flags them as soon as they're fixed.

---

## Architecture and key decisions

```
tests/            what to check (reads like the acceptance criteria)
  conftest.py     shared fixtures: auth, API clients, test data, cleanup
  api/            API tests, one file per topic
  ui/             UI tests + UI-only fixtures
pages/            page objects (locators + user actions)
api_clients/      one class per API resource (auth, events, bookings)
data/             test-data factories (unique, valid data)
config/           settings from environment variables
docs/             test plan
```

**1. Authorization is handled by the framework, not by tests.**
A session fixture logs in once through the API. API tests receive a client that
sends the token on every request. UI tests receive a browser page that is already
logged in: the token is injected into `localStorage` before the app loads, so no
test uses the login form.

**2. Each run owns its test data.**
The framework creates its own event through `POST /events`, with a known price
(deliberately decimal, $99.99) and seat count, and deletes it at the end. Tests
never depend on shared demo data. The decimal price is what exposed the UI
rounding bug.

**3. Cleanup is automatic and goes through the API.**
Bookings are created through "factory" fixtures that record what they create and
cancel it after each test, even when the test fails. UI tests register the
reference they see on screen; it is cancelled through the API afterwards.

**4. Layers keep changes in one place.**
API classes only send requests and return responses; page objects only find
elements and perform actions; tests decide what is correct. A changed endpoint or
selector is a one-line fix.

**5. Setup through the API, behaviour through the UI.**
A UI test only drives the browser for the behaviour it checks. The cancel test
(U3) creates its booking through the API, then cancels in the UI.

**6. Known bugs are tested, not hidden.**
Tests check the documented behaviour and are marked `xfail(strict=True)` with the
bug as the reason. The build stays green, the bug stays visible, and a fix turns
the test into a regression guard.

**7. Config from environment variables.**
URLs have defaults in `config/settings.py`; credentials come from `.env`

---

## Test choices

Full list with IDs: [`docs/test-plan.md`](docs/test-plan.md).

| Area | Tests | Why |
|---|---|---|
| Create booking (AC1, AC5) | API + UI | Core of the story |
| Total price (AC2) | API (1, 3, 10 tickets) + UI (whole and decimal price) | Boundaries and rounding |
| Booking appears (AC3) | API (by id, by ref, in list) + UI (My Bookings) | Every place a booking can be read |
| Cancel (AC4) | API + UI; seats restored | Removal checked in every view |
| Validation | API (quantity 0/11, bad name/email/phone, missing field, not enough seats, unknown event) + UI (empty form) | Business rules the story doesn't mention |
| Auth | No token, invalid token, token belongs to the configured user | The docs don't document auth |
| Known bugs | Ref format, price type, UI rounding | Documented as `xfail` |

**Why mostly API tests:** they are fast, stable and test the rules where they
live. UI tests cover the critical journey only (book → confirm → My Bookings →
cancel), so the suite stays quick and reliable.

**Out of scope:** event management, registration and login as features, the
"Clear all bookings" button — outside US-114.

---

## With more time

- **More negative scenarios**, for example:
  - booking with an expired token
  - wrong data types (quantity as text, decimal quantity like `2.5`)
  - very long or special-character names and emails
  - booking an event that was deleted, or cancelling the same booking twice
- **Robustness scenarios**, for example:
  - two bookings for the last available seats at the same time (only one should succeed)
  - booking an event that has just sold out
  - refreshing or double-clicking **Confirm Booking** (no duplicate bookings)
  - page reload during booking
- **User isolation test:** a second test account must not see or cancel another
  user's booking.
- **Cross-browser runs:** run the UI tests in Firefox and WebKit as well as Chromium
  (`pytest --browser firefox --browser webkit`).