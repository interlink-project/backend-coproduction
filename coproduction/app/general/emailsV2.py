from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import make_msgid
import smtplib
import ssl
from jinja2 import Template
from app.config import settings
from pathlib import Path
import logging


def send_emailV2(email_to, type, environment):

    assert settings.EMAILS_ENABLED, "no provided configuration for email variables"
    
    environment["server"] = settings.SERVER_NAME
    if type == 'add_member_team':
        subject = 'Interlink: You have been added to a new team'
        environment["team_url"] = 'https://{server}/dashboard/organizations/{org_id}/{team_id}'.format(
            server=settings.SERVER_NAME,
            org_id=environment['org_id'],
            team_id=environment['team_id'])
        environment["link"] = 'https://{server}/dashboard/organizations/{org_id}/{team_id}'.format(
            server=settings.SERVER_NAME,
            org_id=environment['org_id'],
            team_id=environment['team_id'])
    elif type == 'add_admin_coprod':
        subject = 'Interlink: You have been added to a new coproduction process'
        environment["link"] = 'https://{server}/dashboard/coproductionprocesses/{id}/overview'.format(
            server=settings.SERVER_NAME,
            id=environment['coprod_id'])
    elif type == 'user_apply_team':
        subject = 'Interlink: A new user has applied to join your team'
        environment["link"] = 'https://{server}/dashboard/organizations/{org_id}/{team_id}?user={user_email}'.format(
            server=settings.SERVER_NAME,
            org_id=environment['org_id'],
            team_id=environment['team_id'],
            user_email=environment['user_email'])
    elif type == 'apply_to_be_contributor':
        subject = 'Interlink: A user has applied to be a contributor'
        environment["link"] = 'https://{server}/dashboard/coproductionprocesses/{id}/team'.format(
            server=settings.SERVER_NAME,
            id=environment['coprod_id'])
        #Print to see what is in the environment
        environment["coprod_id"] = str(environment.get("coprod_id", ""))


    # SMTP settings
    smtp_server = settings.SMTP_HOST
    smtp_port = settings.SMTP_PORT
    smtp_user = settings.SMTP_USER
    smtp_password = settings.SMTP_PASSWORD
    smtp_sender = (settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL)

    # Load HTML template
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / f"{type}.html") as f:
        template_str = f.read()
    
    # Create a Jinja2 template and render
    template = Template(template_str)
    html_content = template.render(environment)

    # Load plain text template and render
    try:
        with open(Path(settings.EMAIL_TEMPLATES_DIR) / f"{type}.txt") as f:
            template_text_str = f.read()
        template_text = Template(template_text_str)
        plain_text_content = template_text.render(environment)
    except FileNotFoundError:
        plain_text_content = "This email does not have a plain text version."

    # Prepare the multipart email (plain text + HTML)
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_sender
    msg["To"] = email_to
    msg["Message-ID"] = make_msgid(domain=settings.SERVER_NAME)

    part1 = MIMEText(plain_text_content, "plain")
    part2 = MIMEText(html_content, "html")

    # The email client will try to render the last part first
    msg.attach(part1)
    msg.attach(part2)

    # Create a secure SSL context
    context = ssl.create_default_context()

    # Try to send the email
    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
    except Exception as e:
        logging.error(f"Failed to send the email. Error: {e}")
