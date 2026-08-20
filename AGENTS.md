# Agent instructions

## Project scope

This repository is the standalone Django HTTP-to-SMTP webmailer. It receives
email payloads, stores `EmailMessage` rows, sends through SMTP/Postfix, and
records delivery logs. Contact selection, campaign templates, and sending
limits may live in a separate sender/impex repository.

## Required skill

For deployment, Apache/mod_wsgi configuration, database initialization,
testmail execution, sender integration, deliverability verification, bounce
processing, or IP/domain warmup, read and follow:

```text
skills/operate-webmailer-delivery/SKILL.md
```

Also read the documentation selected by that skill before taking action.

For sender-dependent Postfix transports, multi-domain OpenDKIM
`KeyTable`/`SigningTable` work, DKIM DNS publication, or invalid-signature
diagnosis, also read and follow:

```text
skills/configure-multidomain-mail-auth/SKILL.md
```

Keep every example from that skill generic inside this public repository.
Store production routing matrices, domains, IP addresses, key paths, and DNS
values only in server-local configuration or private operational records.

## Compatibility and safety

- Preserve Python 2.7 and Django 1.8 compatibility unless an explicit upgrade
  project replaces the legacy runtime.
- Use Unix LF line endings.
- Keep `config/settings.py` local and uncommitted.
- Never commit secrets, database passwords, production hostnames/IPs, DKIM
  keys, live recipients, or production allowlists.
- Never hardcode deployment-specific URLs in reusable commands. Read them from
  Django settings.
- Distinguish Apache 2.2 (`Order`/`Allow`) from Apache 2.4 (`Require`).
- Keep `WSGIDaemonProcess` and `WSGIProcessGroup` names identical.
- Run `apache2ctl configtest` and require `Syntax OK` before restart/reload.
- Do not upgrade the legacy shared virtualenv, Apache, PostgreSQL, mod_wsgi, or
  OS as an incidental troubleshooting step.
- Do not send live email without explicit user authorization. Use owned test
  addresses for preflight.
- Treat HTTP 200 with JSON status `failed` as failed delivery.
- Keep `/api/send-email/` behind firewall and explicit IP allowlisting.
- Never bypass suppressions, unsubscribe state, hard-bounce state, complaint
  state, or warmup daily limits.

## Server layouts

Legacy server:

```text
Project: /home/eecho/impexcompany/autoverkopenshop/Email-marketing-platforms
Virtualenv: /home/eecho/.virtualenvs/impexcompany2
Apache: 2.2.22
```

New server:

```text
Project: /home/admin/Email-marketing-platforms
Apache: 2.4
Virtualenv: discover and verify locally; do not assume the legacy path
```
