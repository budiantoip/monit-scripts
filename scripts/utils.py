#!/usr/bin/python
from __future__ import print_function
import os
import smtplib
import logging
from subprocess import Popen, PIPE
import socket
import smtplib

# Import the email modules
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
handler = logging.FileHandler("/var/log/monit.log")
formatter = logging.Formatter("%(module)s.%(funcName)s: [%(levelname)s] %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)

# Create Gmail's App Password
# Once created fill in the email_password here
email_username = "user@gmail.com"
email_password = "12345"


def send_email(to_addr, from_addr, cc=None, bcc=None, subject=None, body=None):

    if not to_addr or not from_addr:
        log.error("error sending email, To or From values are null")
        return "error"

    # convert TO into list if string
    if type(to_addr) is not list:
        to_addr = to_addr.split()

    to_list = to_addr + [cc] + [bcc]
    to_list = [x for x in to_list if x]  # remove null emails

    msg = MIMEMultipart()
    msg["From"] = from_addr
    msg["Subject"] = subject
    msg["To"] = ",".join(to_addr)
    msg["Cc"] = cc
    msg["Bcc"] = bcc

    msg.attach(MIMEText(body, "html"))
    try:
        # Connect to the Gmail SMTP server and set SMTP to use TLS
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()  # Can be omitted
        server.starttls()
        server.ehlo()  # Can be omitted

        # Login to Gmail
        if email_username and email_password:
            server.login(email_username, email_password)
        else:
            log.error("SMTP authentication error: Username and Password required")
            return "error"

        # Send the email
        server.sendmail(from_addr, to_list, msg.as_string())
    except smtplib.SMTPAuthenticationError as e:
        log.error("Error authetnicating to SMTP server: %s, exiting.., %s" % (str(e)))
        return "error"
    except smtplib.SMTPException as e:
        log.error("Error sending email")
        log.error(str(e))
    except socket.timeout:
        log.error("SMTP login timeout")
        return "error"
    finally:
        server.quit()


def render_template(template, **kwargs):
    """renders a Jinja template into HTML"""
    # check if template exists
    if not os.path.exists(template):
        log.error("No template file present: %s" % template)
        return "error"

    import jinja2

    templateLoader = jinja2.FileSystemLoader(searchpath="/")
    templateEnv = jinja2.Environment(loader=templateLoader)
    templ = templateEnv.get_template(template)
    return templ.render(**kwargs)
