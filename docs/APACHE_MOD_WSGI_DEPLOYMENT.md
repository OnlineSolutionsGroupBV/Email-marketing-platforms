# Apache and mod_wsgi deployment

This guide covers both supported deployment shapes for the Django webmailer.
Keep server-specific paths, hostnames, IP addresses, and secrets in local
configuration rather than Git.

## Identify the server before editing

```bash
apache2ctl -v
apache2ctl -M | grep wsgi
python --version
python -c "import django; print(django.get_version())"
```

An active virtualenv in the shell does not affect Apache. mod_wsgi runs in an
Apache process and must be pointed at the intended environment explicitly.

## Legacy server: Apache 2.2 and Python 2.7

Known legacy layout:

```text
Project: /home/eecho/impexcompany/autoverkopenshop/Email-marketing-platforms
Virtualenv: /home/eecho/.virtualenvs/impexcompany2
Apache: 2.2.22
```

Use `Order` and `Allow`, not the Apache 2.4 `Require` directive:

```apache
<VirtualHost SERVER_IP:80>
    ServerName MAILER_HOSTNAME

    DocumentRoot /home/eecho/impexcompany/autoverkopenshop/Email-marketing-platforms

    Alias /static/ /home/eecho/impexcompany/autoverkopenshop/Email-marketing-platforms/static/
    <Directory /home/eecho/impexcompany/autoverkopenshop/Email-marketing-platforms/static>
        Order allow,deny
        Allow from all
    </Directory>

    <Directory /home/eecho/impexcompany/autoverkopenshop/Email-marketing-platforms/config>
        <Files wsgi.py>
            Order allow,deny
            Allow from all
        </Files>
    </Directory>

    WSGIDaemonProcess webmailer \
        python-home=/home/eecho/.virtualenvs/impexcompany2 \
        python-path=/home/eecho/impexcompany/autoverkopenshop/Email-marketing-platforms
    WSGIProcessGroup webmailer

    WSGIScriptAlias / /home/eecho/impexcompany/autoverkopenshop/Email-marketing-platforms/config/wsgi.py

    ErrorLog /var/log/apache2/webmailer-error.log
    CustomLog /var/log/apache2/webmailer-access.log combined
</VirtualHost>
```

Replace `SERVER_IP` and `MAILER_HOSTNAME` locally. The
`WSGIDaemonProcess` and `WSGIProcessGroup` names must match exactly.

If this old mod_wsgi rejects `python-home`, first identify the exact mod_wsgi
and Python versions. Do not upgrade the shared runtime blindly. A compatible
legacy fallback is to include the verified virtualenv `site-packages` path in
`python-path`.

## New server: Apache 2.4

Known new-server project layout:

```text
/home/admin/Email-marketing-platforms
```

Use the actual virtualenv path created on that server:

```apache
<VirtualHost SERVER_IP:80>
    ServerName MAILER_HOSTNAME

    DocumentRoot /home/admin/Email-marketing-platforms

    Alias /static/ /home/admin/Email-marketing-platforms/static/
    <Directory /home/admin/Email-marketing-platforms/static>
        Require all granted
    </Directory>

    <Directory /home/admin/Email-marketing-platforms/config>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>

    WSGIDaemonProcess webmailer \
        python-home=/PATH/TO/VERIFIED/VIRTUALENV \
        python-path=/home/admin/Email-marketing-platforms
    WSGIProcessGroup webmailer

    WSGIScriptAlias / /home/admin/Email-marketing-platforms/config/wsgi.py

    ErrorLog ${APACHE_LOG_DIR}/webmailer-error.log
    CustomLog ${APACHE_LOG_DIR}/webmailer-access.log combined
</VirtualHost>
```

Do not copy the legacy Python 2 virtualenv path onto the new server. Confirm
that mod_wsgi and the selected environment use compatible Python major
versions.

## Local Django settings

`config/settings.py` is intentionally server-local. At minimum, configure:

```python
ALLOWED_HOSTS = ["mailer.example.com", "192.0.2.10"]
WEBMAILER_PUBLIC_SITE_URL = "https://www.example.com/"

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
```

The root path redirects to `WEBMAILER_PUBLIC_SITE_URL`. `/admin/` and the API
paths remain local to the webmailer.

## Database and static files

Use the exact environment that Apache will use:

```bash
cd /PATH/TO/Email-marketing-platforms
/PATH/TO/VIRTUALENV/bin/python manage.py check
/PATH/TO/VIRTUALENV/bin/python manage.py migrate --noinput
/PATH/TO/VIRTUALENV/bin/python manage.py collectstatic --noinput
```

Create a superuser only when admin access is required:

```bash
/PATH/TO/VIRTUALENV/bin/python manage.py createsuperuser
```

Do not run `makemigrations` during a routine deployment.

## Validate and activate

```bash
apache2ctl configtest
```

Proceed only after `Syntax OK`:

```bash
service apache2 restart
service apache2 status
```

Test the selected virtual host locally:

```bash
curl --include --header 'Host: MAILER_HOSTNAME' http://127.0.0.1/
```

Inspect both Apache and mail logs:

```bash
tail -n 100 /var/log/apache2/webmailer-error.log
tail -n 200 /var/log/mail.log
```

## Common failures

### Process group does not exist

Make the `WSGIDaemonProcess` and `WSGIProcessGroup` names identical.

### Wrong Django or missing module

The traceback path shows which environment Apache loaded. If it points into
the expected virtualenv, stop changing Apache and resolve the dependency or
legacy settings mismatch there.

For old Django versions, `django.middleware.security.SecurityMiddleware` may
not exist. Confirm the Django version before removing that middleware. Do not
upgrade a shared legacy virtualenv as an incidental fix.

### Static files return 403 or 404

Confirm the Apache version, access syntax, trailing Alias paths, filesystem
permissions, and that Apache's Alias target equals Django `STATIC_ROOT`.
