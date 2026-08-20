# Email-marketing-platforms
Email Marketing Platforms (HTTP2SMTP Services) 

**Email Marketing Platform** is a lightweight, open-source HTTP-to-SMTP email gateway, inspired by services like SendGrid or Mailgun, but designed to be simple, self-hosted, and easy to integrate.

It allows client applications to send transactional or marketing emails via a clean REST API (`POST /send-email/`), which then relays the messages through your own SMTP server. Built with Django (Python 2.7 compatible), this project is ideal for developers or small teams who need full control over their email infrastructure without relying on third-party providers.

---

## 🔧 Features

- Send emails via a simple JSON POST request  
- One recipient per message (ideal for tracking delivery status)  
- Supports `text/plain` and `text/html` bodies  
- Adds `List-Unsubscribe` header automatically  
- Stores status (`queued`, `sent`, `bounced`, etc.) and full SMTP/bounce logs  
- IP whitelisting for secure access  
- Easy to deploy on any VPS with Apache2 and mod_wsgi  

---

## 🎯 Use Cases

- Self-hosted transactional email delivery  
- API-driven email sending for SaaS products  
- Lightweight alternative to commercial SMTP APIs

## 📄 Webmailer – Self-Hosted HTTP-to-SMTP Email API

**Webmailer** is a lightweight, open-source Django-based HTTP-to-SMTP email microservice designed to offer a simple and flexible alternative to providers like SendGrid or Mailgun — but fully hostable on your own infrastructure.

It exposes a clean, minimal HTTP API endpoint that accepts email parameters via `POST` and dispatches messages using your own SMTP server, with full logging and delivery status tracking.

This project is part of the broader `Email-marketing-platforms` initiative, where we aim to build a suite of open and self-hostable tools for sending and managing email campaigns and transactional messaging — without vendor lock-in.

---

### 🔧 Features

* **Send emails via RESTful API** using `application/json`
* **Supports both plain text and HTML bodies**
* **Built-in List-Unsubscribe header generation**
* **One email per request** (ensures accurate delivery status per recipient)
* **Stores full message log and SMTP status** (`sent`, `failed`, etc.)
* **IP whitelisting for secure API access**
* **Easy to deploy with Apache + mod\_wsgi**
* **Python 2.7 and Django 1.8 compatible** (for legacy environments)

---

### 🔌 API Endpoint

```
POST /api/send-email/
```

### Webinterface en rootredirect

De root-URL `/` verwijst naar de externe publieke website die in de lokale
Django-settings is geconfigureerd:

```text
/ -> WEBMAILER_PUBLIC_SITE_URL
```

Voorbeeld in de niet-gecommitte `config/settings.py` van de webmailerserver:

```python
WEBMAILER_PUBLIC_SITE_URL = "https://www.example.com/"
```

Hierdoor gaan zowel bezoekers van het webmailer-subdomein als bezoekers die de
server via het IP-adres openen vanaf `/` naar de publieke website. De publieke
website kan bijvoorbeeld door Firebase Hosting worden bediend. De echte URL
staat alleen in de lokale settings en wordt niet hardcoded of in deze publieke
README opgeslagen.

De Django-admin blijft rechtstreeks bereikbaar voor beheerders die het pad
kennen:

```text
/admin/
```

`ALLOWED_HOSTS` moet zowel het webmailer-subdomein als het gebruikte server-IP
toestaan als beide HTTP Host-waarden door Django moeten worden geaccepteerd.
Het niet publiceren van `/admin/` is geen toegangsbeveiliging; gebruik een
sterk wachtwoord en beperk de admin waar mogelijk met firewall- of
Apache-regels.

De API-endpoints worden hierdoor niet beïnvloed. Bijvoorbeeld
`POST /api/send-email/` blijft rechtstreeks beschikbaar.

**Payload (JSON):**

```json
{
  "client_id": "your-app",
  "from_email": "noreply@example.com",
  "to_email": "user@example.net",
  "subject": "Welcome!",
  "text_body": "Hello user, welcome to our service.",
  "html_body": "<p>Hello <strong>user</strong>, welcome to our service.</p>",
  "unsubscribe_url": "https://example.com/unsubscribe?id=123",
  "unsubscribe_email": "contact@example.com",
  "one_click_unsubscribe_url": "https://example.com/unsubscribe/one-click?id=123"
}
```

**Response:**

```json
{
  "status": "sent",
  "id": 10123
}
```

---

### One-click unsubscribe headers

When `one_click_unsubscribe_url` is present, Webmailer adds RFC 8058 one-click headers:

```text
List-Unsubscribe-Post: List-Unsubscribe=One-Click
List-Unsubscribe: <mailto:contact@example.com>, <https://example.com/unsubscribe/one-click?id=123>
```

`unsubscribe_url` can still point to a human unsubscribe page shown in the message body.

### Configuratievariabelen

Deze public repo bevat geen `settings.py` met productiegegevens. Maak op elke server een lokale settings file of gebruik environment variables. Commit nooit echte secrets, API keys, database wachtwoorden of domeinspecifieke productieconfiguratie.

Minimale Django/webmailer configuratie:

```python
import os

SECRET_KEY = "change-me-local-secret"
DEBUG = False
ALLOWED_HOSTS = ["mailer.example.com", "192.0.2.10"]
WEBMAILER_PUBLIC_SITE_URL = "https://www.example.com/"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "email_marketing",
        "USER": "email_marketing",
        "PASSWORD": "change-me",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

EMAIL_HOST = "localhost"
EMAIL_PORT = 25
DEFAULT_FROM_EMAIL = "noreply@example.com"
SERVER_EMAIL = DEFAULT_FROM_EMAIL
WEBMAILER_CONTENT_TRANSFER_ENCODING = "quoted-printable"

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
```

`STATIC_URL` is het URL-prefix dat Django voor static bestanden gebruikt.
`STATIC_ROOT` is de lokale directory waarin `collectstatic` de bestanden
verzamelt. Apache moet met `Alias /static/` exact naar deze directory wijzen.
Deze waarden horen in de lokale, niet-gecommitte `config/settings.py`; de
README bewaart alleen het configuratievoorbeeld en geen actieve serverwaarde.

`WEBMAILER_CONTENT_TRANSFER_ENCODING` controls MIME body encoding for text/plain and text/html parts before SMTP handoff.
Recommended value is `"quoted-printable"` for UTF-8 mail because it keeps message bodies readable while avoiding unstable `8bit` transport bodies that can break DKIM body hash validation if a downstream server rewrites or wraps content.
Use `"base64"` if you prefer maximum transport stability over readable raw source, or `"none"` to keep Django's default behavior.

Contact status synchronisatie naar een externe Contact database:

```python
CONTACT_STATUS_UPDATE_ENABLED = True
CONTACT_STATUS_UPDATE_URL = "https://contact.example.com/contact/api/email-status/"
CONTACT_PROVIDER_UPDATE_KEY = "change-me-long-random-key"
CONTACT_STATUS_UPDATE_TIMEOUT = 10
```

Externe status ingest API voor scripts of andere mailservers:

```python
EMAIL_LOG_INGEST_KEY = "change-me-long-random-key"
```

Aanbevolen productie-aanpak:

- bewaar secrets in environment variables of een niet-gecommitte lokale settings file;
- zet `DEBUG = False`;
- beperk `ALLOWED_HOSTS`;
- gebruik aparte keys voor `CONTACT_PROVIDER_UPDATE_KEY` en `EMAIL_LOG_INGEST_KEY`;
- roteer keys direct als ze ooit in git, logs of chat terechtkomen;
- houd mailserverconfiguratie zoals DKIM private keys buiten deze repo.

### Contact status notification

`maillogger` can notify an external contact system after parsing Postfix logs.

Settings:

```python
CONTACT_STATUS_UPDATE_ENABLED = True
CONTACT_STATUS_UPDATE_URL = "https://contact.example.com/contact/api/email-status/"
CONTACT_PROVIDER_UPDATE_KEY = "change-me"
CONTACT_STATUS_UPDATE_TIMEOUT = 10
```

Parse logs, classify recipient providers by domain/MX, and notify the external contact endpoint:

```bash
python manage.py parse_maillogs --mx --notify-contact
```

External parsers can also POST delivery status into maillogger:

```python
EMAIL_LOG_INGEST_KEY = "change-me"
```

```bash
curl -X POST https://mailer.example.com/api/email-log/ \
  -H "X-Email-Log-Key: change-me" \
  -d "email=user@example.com" \
  -d "status=bounced" \
  -d "reason=User unknown" \
  -d "bounce_type=hard" \
  -d "notify_contact=true"
```

---

### 🛠 Use Cases

* Self-hosted email delivery for CRM or SaaS applications
* Replacement for SendGrid/Mailgun when using your own SMTP
* Email relay API for internal apps or staging environments
* Educational or test setup for building reliable SMTP-based delivery

---

### 📁 Structure

This is one of several tools being developed under `Email-marketing-platforms`. Future components may include:

* Bounce handler / webhook parser
* Template & contact manager
* Admin dashboard for delivery logs
* Cron-based campaign batch sender
* Mail merge and personalization tools

Each tool can be linked from this central repository, or optionally bundled together depending on integration needs.

---

### 📦 Planned Extensions

* Token-based API auth
* Rate limiting per IP
* Multiple SMTP relay backends
* Stats dashboard (success, bounce, open rate)
* DKIM/SPF validation helper


For comprehensive installation instructions, configuration details, and various use cases, please visit the full guide:

👉 Email Marketing Platforms – Self-Hosted 
https://www.webdeveloper.today/2025/05/email-marketing-platforms-self-hosted.html

# 📬 maillogger

A simple Django app for parsing Postfix mail logs and storing email delivery statuses for analytics, reporting, and automated unsubscribe workflows.

---

## ✅ Features

- Parses `/var/log/mail.log` and rotated `.gz` files
- Stores each email delivery event:
  - Sender and recipient
  - Delivery status (`sent`, `bounced`, etc.)
  - Bounce reason (e.g. "user unknown", "mailbox full")
  - Bounce type (`hard`, `soft`, or null)
- Bounce classification can be automatic or manual
- Ready for filtering, analytics, or unsubscribe automation

---

## 📦 Installation

1. Add the app to your Django project:

   ```bash
   python manage.py startapp maillogger
   ```

2. Add it to your `INSTALLED_APPS` in `settings.py`:

   ```python
   INSTALLED_APPS = [
       ...
       'maillogger',
   ]
   ```

3. Apply migrations:

   ```bash
   python manage.py makemigrations maillogger
   python manage.py migrate
   ```

---

## 🛠 Management Commands

### 🔹 `parse_maillogs`

Parses mail logs (including `.gz` files) and stores delivery events in the `EmailLog` model.

```bash
python manage.py parse_maillogs
```

> ✅ Supports automatic decoding and fallback for compressed logs.

---

### 🔹 `classify_bounces`

Classifies previously parsed bounce records into `hard` or `soft` types based on the bounce reason.

```bash
python manage.py classify_bounces
```

> Recommended to run after `parse_maillogs` if you want to separate bounce classification logic.

---

### 🔹 Postfix log feedback naar Contact API

Gebruik deze volgorde op de mail/webmailer server om Postfix logs naar de
centrale Contact status API te sturen:

```bash
python manage.py parse_maillogs --mx
python manage.py classify_bounces
python manage.py notify_bounced_contacts --status bounced --bounce-type hard --limit 100 --dry-run
python manage.py notify_bounced_contacts --status bounced --bounce-type hard --limit 100
```

Als URL/key niet in lokale settings of environment staan:

```bash
python manage.py notify_bounced_contacts \
  --url https://CONTACT-SERVER/contact/api/email-status/ \
  --key CONTACT_PROVIDER_UPDATE_KEY \
  --status bounced \
  --bounce-type hard \
  --limit 100
```

Huidige hard-bounce classificatie dekt al:

- `user_unknown`: user unknown, mailbox not found, no such user, recipient unknown
- `mailbox_full_quota`: mailbox full, over quota, quota exceeded, out of storage
- domain hard failures: Host not found, name service error, no such domain
- Microsoft hosted tenant zonder mailbox-subscription:
  `Mail received as unauthenticated ... hosted tenant which has no mail-enabled subscriptions`
- terugkerende Postfix connect failures op SMTP poort 25:
  `connect to ...:25: Connection timed out` en `connect to ...:25: Connection refused`

Algemene technische/reputatieproblemen zoals DNS soft error, message expired en
5.7 policy/reputation blocks worden niet blind hard bounce gemaakt.

---

## 🧠 Model: `EmailLog`

| Field         | Description                          |
|---------------|--------------------------------------|
| `recipient`   | Email address receiving the message  |
| `sender`      | Email address sending the message    |
| `status`      | Email status (`sent`, `bounced`, etc.) |
| `reason`      | Text reason from the mail log        |
| `bounce_type` | `hard`, `soft`, or `null`            |
| `message_id`  | Mail message ID                      |
| `logged_at`   | When the log was saved               |

---

## 🔍 Example Usage

Filter for all hard bounces:

```python
EmailLog.objects.filter(status='bounced', bounce_type='hard')
```

---

## 📈 Coming Soon

- Unsubscribe automation via API
- Bounce analytics dashboard
- Domain-based performance stats

---

## ⚠️ Python & Django Compatibility

- ✅ Compatible with **Python 2.7**
- ✅ Designed for **Django 1.11 LTS**

  


## 💬 Support

For questions, bug reports, or feature requests, please open an issue on GitHub.

For commercial support or custom integration, contact us at: 
https://www.webdeveloper.today/p/about-web-developer-today.html 

Blog post
https://www.webdeveloper.today/2025/05/new-open-source-django-app-maillogger.html 
  
