from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from maillogger.models import EmailLog
import re
import codecs
import gzip

class Command(BaseCommand):
    help = 'Parses Postfix mail logs and saves delivery status'

    def handle(self, *args, **options):
        # ls /var/log/mail.*
        # /var/log/mail.err  /var/log/mail.log.1     /var/log/mail.log.3.gz  /var/log/mail.summ
        # /var/log/mail.log  /var/log/mail.log.2.gz  /var/log/mail.log.4.gz

        log_files = ["/var/log/mail.log.2.gz", "/var/log/mail.log.3.gz", "/var/log/mail.log.4.gz"]  # Add more if needed 
        # "/var/log/mail.log", "/var/log/mail.log.1"

        to_line_regex = re.compile(r'to=<([^>]+)>')
        from_line_regex = re.compile(r'from=<([^>]+)>')
        status_regex = re.compile(r'status=(\w+)(?: \((.*?)\))?')
        msg_id_regex = re.compile(r'message-id=<([^>]+)>')

        for log_path in log_files:
            try:

                if log_path.endswith('.gz'):
                    opener = lambda p: gzip.open(p, 'rb')
                else:
                    opener = lambda p: codecs.open(p, 'r', encoding='utf-8', errors='ignore')
                print("Starting: " + log_path)                
                with opener(log_path) as log_file:
                    for line in log_file:
                        if "status=" not in line or "to=<" not in line:
                            continue

                        recipient_match = to_line_regex.search(line)
                        sender_match = from_line_regex.search(line)
                        status_match = status_regex.search(line)
                        msg_id_match = msg_id_regex.search(line)

                        if recipient_match and status_match:
                            EmailLog.objects.create(
                                recipient=recipient_match.group(1),
                                sender=sender_match.group(1) if sender_match else None,
                                status=status_match.group(1).lower(),
                                reason=(status_match.group(2) or '').strip(),
                                message_id=msg_id_match.group(1) if msg_id_match else None
                            )
                self.stdout.write("Parsed: %s" % log_path)
            except IOError:
                self.stderr.write("Log file not found: %s" % log_path)

