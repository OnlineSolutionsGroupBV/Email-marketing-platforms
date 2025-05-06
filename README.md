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
