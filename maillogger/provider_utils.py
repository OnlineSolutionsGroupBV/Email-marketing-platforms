import subprocess


DOMAIN_PROVIDER_MAP = {
    'gmail.com': 'google',
    'googlemail.com': 'google',
    'outlook.com': 'microsoft',
    'outlook.be': 'microsoft',
    'outlook.nl': 'microsoft',
    'hotmail.com': 'microsoft',
    'hotmail.be': 'microsoft',
    'hotmail.nl': 'microsoft',
    'hotmail.co.uk': 'microsoft',
    'live.com': 'microsoft',
    'live.be': 'microsoft',
    'live.nl': 'microsoft',
    'windowslive.com': 'microsoft',
    'msn.com': 'microsoft',
    'yahoo.com': 'yahoo',
    'yahoo.be': 'yahoo',
    'yahoo.nl': 'yahoo',
    'ymail.com': 'yahoo',
    'rocketmail.com': 'yahoo',
    'aol.com': 'yahoo',
    'skynet.be': 'proximus_skynet',
    'proximus.be': 'proximus_skynet',
    'telenet.be': 'telenet',
    'pandora.be': 'telenet',
    'icloud.com': 'icloud',
    'me.com': 'icloud',
    'mac.com': 'icloud',
    'proton.me': 'proton',
    'protonmail.com': 'proton',
}

MX_PROVIDER_PATTERNS = (
    ('business_google', ('aspmx.l.google.com', 'googlemail.com', 'google.com')),
    ('business_microsoft', ('mail.protection.outlook.com', 'outlook.com')),
    ('business_yahoo', ('yahoodns.net', 'yahoo.com')),
    ('business_proton', ('protonmail.ch', 'protonmail.com')),
)


def get_email_domain(email):
    if not email or '@' not in email:
        return None
    return email.rsplit('@', 1)[1].lower().strip()


def lookup_mx_hosts(domain):
    if not domain:
        return []
    try:
        output = subprocess.check_output(['dig', '+short', 'MX', domain], stderr=subprocess.STDOUT)
    except Exception:
        return []
    if not isinstance(output, str):
        output = output.decode('utf-8', 'ignore')
    hosts = []
    for line in output.splitlines():
        parts = line.strip().rstrip('.').split()
        if len(parts) == 1:
            hosts.append(parts[0].lower())
        elif len(parts) >= 2:
            hosts.append(parts[1].lower())
    return hosts


def detect_provider_from_mx_hosts(mx_hosts):
    for mx_host in mx_hosts:
        host = mx_host.lower().rstrip('.')
        for provider, patterns in MX_PROVIDER_PATTERNS:
            for pattern in patterns:
                if pattern in host:
                    return provider
    if mx_hosts:
        return 'business_other'
    return 'unknown'


def detect_provider(email, use_mx=False):
    domain = get_email_domain(email)
    provider = DOMAIN_PROVIDER_MAP.get(domain)
    if provider:
        return provider, domain, None
    mx_hosts = lookup_mx_hosts(domain) if use_mx else []
    if use_mx:
        return detect_provider_from_mx_hosts(mx_hosts), domain, mx_hosts[0] if mx_hosts else None
    return 'unknown', domain, None
