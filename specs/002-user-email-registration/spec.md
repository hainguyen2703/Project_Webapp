# Feature Specification: User Email Registration

**Feature Branch**: `002-user-email-registration`  
**Created**: 2026-05-05  
**Status**: Draft  
**Input**: User description: "Add feature: allow user to create account by mail"

## Clarifications

### Session 2026-05-14 (continued)
- Q: Should the system accept all RFC 5321-compliant email addresses, or restrict registration to Gmail addresses only? → A: Accept only Gmail addresses (`@gmail.com`).
- Q: What happens to a pending account that is never verified (user never clicks the link and never resends)? → A: Delete pending unverified accounts after 1 day.
- Q: Is there a maximum number of verification email resend attempts per registration? → A: Maximum 3 resend attempts per registration; after that, the user must re-register.
- Q: Should the registration flow include explicit security event logging requirements? → A: No logging requirement in this spec; defer to a future observability feature.
- Q: Should the registration form include a privacy/data-consent mechanism? → A: Add a mandatory consent checkbox (e.g., "I agree to the Privacy Policy") that must be ticked before submission is accepted.

### Session 2026-05-14 (session 2)
- Q: Where should the resend attempt counter (max 3) be tracked in the data model? → A: Add `resend_count` (integer, 0–3) to the Verification Token entity.
- Q: How is active account data retention and deletion handled? → A: Out of scope for this feature; active account deletion (including right-to-erasure) will be addressed in a future account management feature.
- Q: Should the Privacy Policy link in the consent checkbox be encoded as a Functional Requirement? → A: Yes — the consent checkbox label MUST include a visible hyperlink to the Privacy Policy page.

### Session 2026-05-14 (session 3)
- Q: What UI state is shown after the registration form is successfully submitted? → A: Show a dedicated "Check your email" confirmation page with a resend link (subject to FR-008 cooldown and attempt cap).
- Q: Should the spec explicitly require secure password hashing rather than leaving it as an implied data-model detail? → A: Yes — add an FR mandating one-way cryptographic hashing; plaintext storage is prohibited.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Register a new account with email (Priority: P1)

A visitor to the paper discovery website wants to create a personal account using their email address so they can access personalised features in the future.

**Why this priority**: This is the foundational capability — all personalised features depend on an account existing. Without registration, no downstream user value is possible.

**Independent Test**: A new visitor can navigate to the registration page, submit a valid email and password, receive a confirmation email, verify their address, and then be recognised as a registered user on the site.

**Acceptance Scenarios**:

1. **Given** a visitor is on the registration page, **When** they enter a valid email address and a conforming password and submit the form, **Then** the system creates a pending account and sends a verification email to the provided address.
2. **Given** a verification email has been sent, **When** the visitor clicks the verification link within 24 hours, **Then** their account is activated and they are directed to a confirmation screen.
3. **Given** a visitor submits the registration form with an email that already has an account, **When** the form is submitted, **Then** the system informs them the email is already registered and offers a "sign in" path without revealing whether a password exists.
4. **Given** a visitor successfully submits the registration form, **When** the system creates the pending account and dispatches the verification email, **Then** the user is navigated to a dedicated "Check your email" confirmation page that shows their masked email address and a resend link.

---

### User Story 2 - Receive and act on the verification email (Priority: P2)

A user who just registered wants to confirm their email address so their account becomes active and trusted.

**Why this priority**: Email verification protects the platform from spam accounts and ensures the contact address is reachable for future communications.

**Independent Test**: After registration, check that an email arrives promptly, that the link in the email activates the account when clicked, and that re-clicking an already-used link is handled gracefully.

**Acceptance Scenarios**:

1. **Given** a user has registered successfully, **When** they open the verification email and click the link, **Then** their account status changes to active and they see a success confirmation.
2. **Given** a user clicks an expired verification link (older than 24 hours), **When** the link is followed, **Then** the system displays an expiry message and offers the option to resend a fresh verification email.
3. **Given** a user has already verified their email and attempts to use the same verification link again, **When** the link is followed, **Then** the system responds with a friendly message indicating the account is already verified.

---

### User Story 3 - Receive meaningful feedback on invalid input (Priority: P3)

A user filling in the registration form wants clear, immediate guidance when their input does not meet the requirements, so they can correct and resubmit without restarting.

**Why this priority**: Clear validation messages reduce abandonment and support tickets, improving the overall registration completion rate.

**Independent Test**: Submit the registration form with various combinations of bad input (missing fields, malformed email, weak password) and verify that each scenario produces a descriptive, field-level error message.

**Acceptance Scenarios**:

1. **Given** a visitor leaves the email field blank and submits, **When** the form is validated, **Then** an error message appears next to the email field indicating it is required.
2. **Given** a visitor enters a malformed email address (e.g., missing the `@` symbol), **When** the form is submitted, **Then** a field-level error explains the email format is invalid.
3. **Given** a visitor enters a password that is shorter than the minimum length, **When** the form is submitted, **Then** the password field shows the minimum length requirement and the form is not submitted.
4. **Given** a visitor does not check the consent checkbox and submits the form, **When** the form is validated, **Then** the consent checkbox shows an error message indicating agreement is required and the form is not submitted.

---

### Edge Cases

- What happens when the verification email is not delivered (e.g., mail server rejection)? The user can request a resend after a short waiting period.
- What happens if the same email is used for two concurrent registrations? Only the first confirmed registration is retained; subsequent duplicates are rejected with an appropriate message.
- How does the system handle email addresses with uncommon but valid formats (e.g., `user+tag@domain.co`)? Only `@gmail.com` addresses are accepted; all other domains are rejected at the validation step with a descriptive error message.
- What happens when a user tries to register but their email domain is temporarily unreachable? Registration proceeds; only the verification step fails gracefully.
- What happens when a user exhausts all 3 resend attempts before verifying? The pending account is left to be purged after 24 hours; the user is informed they must re-register with the same address once it becomes available again.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a registration form collecting at least an email address and a password.
- **FR-002**: The system MUST only accept email addresses with the domain `@gmail.com`; submissions using any other domain MUST be rejected with a clear field-level error indicating that only Gmail addresses are supported.
- **FR-003**: The system MUST enforce a minimum password length of 8 characters and require at least one letter and one digit.
- **FR-004**: The system MUST reject registration attempts where the email address is already associated with an existing account, without disclosing whether a password exists for that account.
- **FR-005**: The system MUST send a verification email to the provided address immediately after a successful registration submission.
- **FR-006**: The system MUST activate the user account only after the user clicks the verification link in the email.
- **FR-007**: Verification links MUST expire 24 hours after they are issued.
- **FR-008**: The system MUST allow a user with a pending (unverified) account to request a new verification email, subject to a resend cooldown of at least 60 seconds and a maximum of 3 resend attempts per registration; once the limit is exhausted, the user must re-register.
- **FR-009**: The system MUST display field-level validation messages for invalid or missing inputs without clearing already-entered valid data.
- **FR-010**: The system MUST NOT reveal account existence through error messages or response timing differences.
- **FR-011**: The system MUST automatically delete pending (unverified) accounts that have not been verified within 24 hours of registration; the associated email address MUST become available for re-registration once purged.
- **FR-012**: The registration form MUST include a mandatory consent checkbox confirming agreement to the Privacy Policy; the form MUST NOT submit unless the checkbox is checked, and the system MUST record the consent timestamp alongside the account.
- **FR-013**: The consent checkbox label MUST include a visible hyperlink to the Privacy Policy page; the link MUST open the policy without navigating the user away from the registration form (e.g., opens in a new tab).
- **FR-014**: Upon successful form submission, the system MUST navigate the user to a dedicated "Check your email" confirmation page that displays their masked email address and a resend verification email link; the resend link MUST respect the FR-008 cooldown and attempt cap.
- **FR-015**: The system MUST store user passwords using a one-way cryptographic hash; storing passwords in plaintext or using reversible encryption is prohibited.

### Key Entities

- **User Account**: Represents a registered user. Key attributes: unique identifier, email address, hashed password, account status (pending / active), registration timestamp, verification timestamp, consent timestamp. Pending accounts are purged 24 hours after creation if not verified.
- **Verification Token**: A single-use token linked to a user account. Key attributes: token value, associated account, expiry timestamp, used flag, resend_count (integer, 0–3; tracks how many resend requests have been issued for this token).
- **Email Notification**: An outbound message sent to a user. Key attributes: recipient address, message type (verification), sent timestamp, delivery status (best-effort).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new visitor can complete the full registration and email verification flow in under 3 minutes under normal conditions.
- **SC-002**: 90% of users who begin the registration form successfully submit it on their first attempt (no abandonment due to unclear errors).
- **SC-003**: Verification emails are received by the user within 2 minutes of registration submission in at least 95% of cases during acceptance testing.
- **SC-004**: 100% of registration attempts with duplicate email addresses are rejected without disclosing account existence.
- **SC-005**: All invalid input scenarios (blank fields, malformed email, non-Gmail domain, weak password, unchecked consent checkbox) produce visible, field-specific error messages without full page reload or data loss.

## Assumptions

- Users have access to the email inbox corresponding to the address they register with.
- The platform already has an email sending capability or can integrate one; no specific provider is assumed.
- Account registration is limited to the email-and-password method in this feature; social login (OAuth2, SSO) is out of scope.
- Post-verification, users are not automatically signed in; a separate sign-in flow is assumed to exist or will be specified separately.
- Password recovery / "forgot password" is out of scope for this feature.
- The website is desktop-targeted (consistent with the existing Paper Discovery site scope).
- Rate limiting or CAPTCHA to prevent automated registrations is a security hardening concern and may be addressed in a separate feature; this spec assumes a reasonably trusted user population for v1.
- A Privacy Policy document is assumed to exist (or will be created separately); FR-013 requires the registration form to link to it.
- Security event logging (registration attempts, verification outcomes, resend requests) is out of scope for this feature and will be addressed in a dedicated observability feature.
- Active account deletion, data retention periods for verified accounts, and right-to-erasure are out of scope for this feature and will be addressed in a future account management feature.
