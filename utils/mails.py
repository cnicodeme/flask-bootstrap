# -*- coding:utf-8 -*-

# @see http://mynthon.net/howto/-/python/python%20-%20logging.SMTPHandler-how-to-use-gmail-smtp-server.txt

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# @see http://stackoverflow.com/questions/8616617/how-to-make-smtphandler-not-block

class TlsSMTPHandler(logging.handlers.SMTPHandler):
    def emit(self, record):
        """
        Emit a record.

        Format the record and send it to the specified addressees.
        """
        try:
            port = self.mailport
            if not port:
                port = smtplib.SMTP_PORT

            smtp = smtplib.SMTP(self.mailhost, port)

            message = MIMEMultipart('alternative')
            message['Subject'] = self.subject
            message['From'] = self.fromaddr
            text = MIMEText(self.format(record), 'text')
            message.attach(text)

            if self.username:
                smtp.ehlo()     # for tls add this line
                smtp.starttls() # for tls add this line
                smtp.ehlo()     # for tls add this line
                smtp.login(self.username, self.password)

            smtp.sendmail(message['From'], self.toaddrs, message.as_string())
            smtp.quit()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)
