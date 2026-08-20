---
name: operate-webmailer-delivery
description: Deploy, configure, test, troubleshoot, and gradually warm up the Email-marketing-platforms Django HTTP-to-SMTP webmailer on its legacy Apache 2.2/Python 2.7 server or its newer Apache 2.4 server. Use for Apache/mod_wsgi virtual hosts, virtualenv selection, local settings, database migrations, the testmail command, IP allowlisting, SPF/DKIM/DMARC verification, sender-interface integration, bounce handling, and controlled sending-volume increases.
---

# Operate Webmailer Delivery

Operate this repository as a delivery service without mixing server-specific
configuration into Git.

## Read the relevant references

Before changing Apache or mod_wsgi, read
`docs/APACHE_MOD_WSGI_DEPLOYMENT.md` from the repository root.

Before sending a test or changing a daily limit, read
`docs/TESTING_AND_WARMUP.md` from the repository root.

Read `README.md` for the current API fields and local Django setting names.

## Classify the server first

Run read-only checks before proposing configuration:

```bash
pwd
apache2ctl -v
apache2ctl -M | grep wsgi
python --version
python -c "import django; print(django.get_version())"
pg_lsclusters 2>/dev/null || true
```

Treat these deployments separately:

- Legacy server: Apache 2.2, Python 2.7, shared `impexcompany2` virtualenv.
- New server: Apache 2.4 and its own verified Python environment.

Never paste Apache 2.4 `Require all granted` directives into Apache 2.2.
Never assume an activated shell virtualenv is used by Apache. Configure the
environment explicitly in `WSGIDaemonProcess` and keep its name identical to
`WSGIProcessGroup`.

## Preserve local configuration

Treat `config/settings.py` as server-local and uncommitted. Do not overwrite it
during pull, deployment, or troubleshooting. Never commit production domains,
IP allowlists, credentials, database passwords, DKIM keys, or live test
recipients.

Require these settings for the test command:

```text
WEBMAILER_TEST_API_URL
WEBMAILER_TEST_TO_EMAIL
WEBMAILER_TEST_UNSUBSCRIBE_URL
WEBMAILER_TEST_ONE_CLICK_UNSUBSCRIBE_URL
```

Use `DEFAULT_FROM_EMAIL` unless `WEBMAILER_TEST_FROM_EMAIL` is deliberately
set. Keep the caller's concrete trusted IP in `ALLOWED_SENDER_IPS`.

## Deploy safely

1. Inspect `git status` and preserve local settings.
2. Pull only committed application, docs, and skill changes.
3. Activate or invoke the exact server virtualenv.
4. Run `python manage.py check`.
5. Run committed migrations with `python manage.py migrate --noinput`.
6. Run `apache2ctl configtest`.
7. Restart or reload Apache only after `Syntax OK`.
8. Test locally with the intended Host header.
9. Read the site-specific Apache log and `/var/log/mail.log`.

Do not run `makemigrations` on a production server unless the task explicitly
concerns a reviewed model change and the repository truly lacks that migration.

## Test delivery in gates

Run the webmailer-local test first:

```bash
python manage.py testmail
```

Require JSON status `sent`; HTTP 200 alone is insufficient. Verify the stored
`EmailMessage`, Postfix queue result, received headers, SPF, DKIM, DMARC,
alignment, unsubscribe headers, content, links, and inbox placement.

Then test one owned recipient through the sender/impex interface. Run its
selection in dry-run mode first. Do not use imported contacts for preflight.

## Warm up conservatively

Treat approximately 100, 200, 500, and 1000 messages/day as phase ceilings,
not automatic consecutive-day targets. Hold or reduce a phase while observing
bounces, deferrals, complaints, unsubscribes, authentication, and reputation.
Use intermediate phases around 300-350 and 750 when signals remain stable.

Never bypass a configured daily limit during warmup. Never send suppressed,
unsubscribed, hard-bounced, blocked, spam-report, null-MX, or no-mail-DNS
records.

Stop or reduce immediately for authentication failure, broken unsubscribe,
wrong personalization, HTTP 200 with JSON `failed`, rising hard bounces,
provider deferrals, complaints, or disagreement between sender state,
webmailer state, and Postfix logs.

## Respect safety boundaries

- Do not send live mail unless the user explicitly authorizes it.
- Use only user-owned addresses for technical tests.
- Do not expose `/api/send-email/` publicly to compensate for an allowlist
  failure.
- Do not trust arbitrary `X-Forwarded-For`; only a trusted proxy may set it.
- Do not upgrade the legacy OS, Apache, PostgreSQL, Django, mod_wsgi, or shared
  virtualenv as an incidental fix.
- Do not restart Apache before a successful config test.

Report the exact server class, files changed, checks run, test recipient class
(never disclose the address), delivery result, and remaining blocker.
