# Delivery testing and gradual warmup

Use gates. First prove the webmailer itself, then prove the sender integration,
then increase real volume only while delivery signals remain stable.

## 1. Configure the local test command

Add server-specific values to the uncommitted `config/settings.py`:

```python
ALLOWED_SENDER_IPS = ["127.0.0.1", "TRUSTED_SENDER_SERVER_IP"]

WEBMAILER_TEST_API_URL = "http://mailer.example.com/api/send-email/"
WEBMAILER_TEST_FROM_EMAIL = "sender@example.com"
WEBMAILER_TEST_TO_EMAIL = "owned-test-address@example.net"
WEBMAILER_TEST_UNSUBSCRIBE_EMAIL = "contact@example.com"
WEBMAILER_TEST_UNSUBSCRIBE_URL = "https://www.example.com/unsubscribe/test"
WEBMAILER_TEST_ONE_CLICK_UNSUBSCRIBE_URL = "https://www.example.com/unsubscribe/one-click/test"
WEBMAILER_TEST_SUBJECT = "UTF-8 DKIM test via webmailer"
WEBMAILER_TEST_TIMEOUT = 30
```

Use only an address controlled by the operator or a fresh address issued by a
mail-analysis service. Do not commit the real values.

## 2. Run the direct HTTP-to-SMTP test

Run with the same environment as Apache:

```bash
cd /PATH/TO/Email-marketing-platforms
/PATH/TO/VIRTUALENV/bin/python manage.py testmail
```

The command performs this complete path:

```text
testmail
  -> POST /api/send-email/
  -> ALLOWED_SENDER_IPS check
  -> EmailForm validation
  -> EmailMessage database row
  -> Django SMTP
  -> Postfix
  -> recipient mailbox
```

The endpoint currently has no API key. It is protected by the existing
firewall and `ALLOWED_SENDER_IPS`. Never widen the firewall or allowlist merely
to make a test pass. Only a trusted reverse proxy may supply
`X-Forwarded-For`.

Success requires both HTTP 200 and JSON status `sent`. The command raises
`CommandError` for a connection error, non-JSON response, non-200 response, or
any other JSON status.

## 3. Verify the received message

Inspect the stored `EmailMessage`, `/var/log/mail.log`, and the received raw
headers. Require:

- SPF pass;
- DKIM pass;
- DMARC pass and alignment with the visible From domain;
- matching forward and reverse DNS for the sending IP;
- a valid Message-ID and Date;
- expected From, content, encoding, and links;
- working visible unsubscribe link;
- expected `List-Unsubscribe` and `List-Unsubscribe-Post` headers;
- expected inbox placement across owned Gmail, Microsoft, and other relevant
  provider test accounts.

The current API does not yet apply `reply_to_email`. If a separate Reply-To is
required, implement and test it before production.

Stop here for any authentication failure, unexpected identity or link, broken
unsubscribe, or JSON status `failed`.

## 4. Test the sender integration

From the impex/sender application, select a dedicated test source containing
only owned addresses. Run the sender command in dry-run mode first, then send
exactly one message. Confirm that sender state, webmailer state, Postfix state,
and the received message all refer to the same delivery.

Do not start with imported campaign recipients.

## 5. Warm up in controlled phases

Treat these values as phase ceilings, not mandatory consecutive-day targets:

| Phase | Daily ceiling | Gate |
|---|---:|---|
| A | about 100 | Best and most recently engaged eligible recipients only |
| B | about 200 | Advance only after stable observation of phase A |
| C | about 500 | Prefer an intermediate 300-350 phase |
| D | about 1000 | Prefer an intermediate 750 phase |

Hold each level for at least one complete observation period. Send at a
consistent rate rather than one burst. Never bypass the daily counter during
warmup.

Exclude unsubscribed, suppressed, hard-bounced, blocked, spam-report, null-MX,
no-mail-DNS, empty, and invalid addresses before every phase.

## 6. Monitor and stop conditions

After every run, review accepted, deferred, soft bounce, hard bounce, rejected,
complaint, unsubscribe, and webmailer-failed counts by recipient provider.

Stop, reduce, or hold volume for:

- SPF, DKIM, or DMARC failure;
- rising hard bounces or provider deferrals;
- any complaint in a very small test cohort;
- broken unsubscribe processing;
- incorrect personalization or recipient selection;
- reputation or blocklist warnings;
- disagreement between sender, webmailer, and Postfix state.

Google recommends keeping Postmaster Tools spam rate below 0.10% and avoiding
0.30% or higher. At small warmup volumes, investigate a single complaint
immediately rather than waiting for a percentage threshold.

## 7. Record the decision

For each day, record the configured ceiling, actual sent count, provider mix,
bounces, SMTP codes, complaints, unsubscribes, authentication, reputation
signals, and the decision to pause, hold, reduce, or advance.

Official references:

- [Google Email sender guidelines](https://support.google.com/mail/answer/81126?hl=en)
- [Google Postmaster Tools setup](https://support.google.com/mail/answer/9981691?hl=en)
