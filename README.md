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

**Payload (JSON):**

```json
{
  "client_id": "your-app",
  "from_email": "noreply@example.com",
  "to_email": "user@example.net",
  "subject": "Welcome!",
  "text_body": "Hello user, welcome to our service.",
  "html_body": "<p>Hello <strong>user</strong>, welcome to our service.</p>",
  "unsubscribe_url": "https://example.com/unsubscribe?id=123"
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

  

