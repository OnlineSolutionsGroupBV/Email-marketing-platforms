---
name: configure-multidomain-mail-auth
description: Configure, verify, or troubleshoot a shared Postfix and OpenDKIM installation that sends multiple From domains through domain-specific source IPs, HELO names, private keys, and DKIM DNS records. Use for sender-dependent transports, KeyTable/SigningTable migrations, invalid DKIM signatures, DNS key publication, signer restarts, SPF/PTR alignment, or safely adding another sending domain.
---

# Configure multi-domain mail authentication

Keep all examples generic. Never commit production domains, IP addresses,
private keys, public-key values, credentials, recipient addresses, or internal
hostnames to this public repository.

## Establish the routing matrix

For every sending domain, record locally outside Git:

```text
From domain
envelope-sender domain
Postfix transport name
outbound source IP
HELO hostname
PTR hostname
DKIM selector
private-key path
DNS provider
```

Require forward DNS and PTR agreement for each HELO. Do not assume the HTTP
webmailer hostname is suitable as SMTP HELO until PTR confirms it.

## Inspect before changing

1. Read `postconf -n`, `postconf -M`, `master.cf`, and active transport maps.
2. Inspect the OpenDKIM process command and non-comment configuration.
3. Identify whether the signer uses single-domain `Domain/Selector/KeyFile`
   settings or `KeyTable`/`SigningTable`.
4. Back up each affected config and key directory with a dated name.
5. Never display or commit private-key contents.

## Route Postfix by envelope sender

On a shared instance, keep global `smtp_bind_address` empty. Create one custom
smtp service per sending identity in `master.cf`:

```text
<TRANSPORT> unix - - n - - smtp
  -o syslog_name=postfix/<TRANSPORT>
  -o smtp_helo_name=<HELO_HOSTNAME>
  -o smtp_bind_address=<OUTBOUND_IP>
```

Select it using `sender_dependent_default_transport_maps`. Match the envelope
sender, not only the visible From header. Test each rule with `postmap -q` and
run `postfix check` before reload.

## Map each From domain to its own DKIM key

Do not use `Domain *` with one `KeyFile` for unrelated domains. Configure:

```text
KeyTable     refile:<KEY_TABLE_PATH>
SigningTable refile:<SIGNING_TABLE_PATH>
```

Pattern:

```text
# KeyTable
<SELECTOR>._domainkey.<DOMAIN_A> <DOMAIN_A>:<SELECTOR>:<DOMAIN_A_PRIVATE_KEY_PATH>
<SELECTOR>._domainkey.<DOMAIN_B> <DOMAIN_B>:<SELECTOR>:<DOMAIN_B_PRIVATE_KEY_PATH>

# SigningTable
*@<DOMAIN_A> <SELECTOR>._domainkey.<DOMAIN_A>
*@<DOMAIN_B> <SELECTOR>._domainkey.<DOMAIN_B>
```

Use `refile:` for wildcard SigningTable entries. Preserve the working milter
socket and trusted-host configuration. Grant the signer read access to private
keys while keeping them inaccessible to other users.

## Publish and verify DNS

Generate a separate RSA key pair per domain. Publish only the generated public
TXT value at:

```text
<SELECTOR>._domainkey.<DOMAIN>
```

Never publish or copy the private key. DNS interfaces usually need a relative
host such as `<SELECTOR>._domainkey`; avoid appending the zone twice. Long TXT
records may be returned as multiple quoted strings and are concatenated by DNS
clients.

Verify the exact private-key/DNS pair:

```bash
opendkim-testkey -d <DOMAIN> -s <SELECTOR> -k <PRIVATE_KEY_PATH> -vvv
```

Require `key OK`. A `key not secure` notice commonly means DNSSEC was not
validated; it does not by itself mean DKIM failure.

## Restart the signer and test runtime selection

Parsing configuration and publishing DNS do not update a running signer.
After successful config and key checks, restart OpenDKIM using the host's init
system, verify the new process, check Postfix, and reload Postfix.

Send one owned-recipient test per domain. Inspect raw headers and require:

```text
expected public source IP
expected HELO/PTR
d=<FROM_DOMAIN>
s=<SELECTOR>
dkim=pass
spf=pass
dmarc=pass
```

Test an existing domain first and again after adding a new domain. Stop and
rollback if it regresses.

## Diagnose invalid signatures

If DNS lookup succeeds but DKIM fails:

1. Compare the signature size with the expected RSA key size.
2. Confirm old single-key settings are inactive.
3. Confirm KeyTable and SigningTable paths used by the running daemon.
4. Confirm the daemon was restarted after configuration changes.
5. Confirm DNS matches the exact private key with `opendkim-testkey -k`.
6. Only then investigate message body/header modification after signing.

The common failure pattern is publishing a new domain's public key while the
running signer still uses an old domain's private key. Restarting OpenDKIM is a
required activation step, not an optional cleanup step.
