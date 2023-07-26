
import logging
from pathlib import Path
from typing import Any, Dict
import threading
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader, select_autoescape
from email.utils import make_msgid, formatdate, formataddr


from app.models import Team
from app.config import settings

semaphore = threading.Semaphore(4)

def thread_send_email(message, email_to, settings):
    with semaphore:
        mail = smtplib.SMTP('mail.interlink-project.eu', 587)
        mail.ehlo()
        mail.starttls()
        mail.login(settings.EMAILS_FROM_EMAIL, settings.SMTP_PASSWORD)
        mail_from = formataddr((settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL))
        response = mail.sendmail(mail_from, email_to, message.as_string())
        mail.quit()
        logging.info(f"send email result: {response}")


def new_message(from_mail, to, subject, body_text, body_html):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = formataddr((settings.EMAILS_FROM_NAME, from_mail))
    msg['To'] = to
    msg['Message-ID'] = make_msgid(domain='interlink-project.eu')
    msg['Date'] = formatdate(timeval=None, localtime=False, usegmt=False)
    
    part1 = MIMEText(body_text, 'plain')
    part2 = MIMEText(body_html, 'html')
    
    msg.attach(part1)
    msg.attach(part2)
    return msg


def send_email(
    email_to: str,
    type: str = "",
    environment: Dict[str, Any] = {},
) -> None:
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
        environment["link"] = 'https://{server}/dashboard/coproductionprocesses/{id}/team?tab=Requests'.format(
            server=settings.SERVER_NAME,
            id=environment['coprod_id'])
        environment["coprod_id"] = str(environment.get("coprod_id", ""))
    
    elif type == 'ask_team_contribution':
        subject = environment['subject']

    elif type == 'points_awarded':
        subject = 'Interlink: You have been awarded new points'
        environment["link"] = 'https://{server}/dashboard/coproductionprocesses/{coprod_id}/{treeitem_id}/guide'.format(
            server=settings.SERVER_NAME,
            coprod_id=environment['coproduction_process_id'],
            treeitem_id=environment['task_id'])
         environment["coprod_link"] ='https://{server}/dashboard/coproductionprocesses/{coprod_id}/guide'.format(
            server=settings.SERVER_NAME,
            coprod_id=environment['coproduction_process_id'])


    # Load HTML template
    env = Environment(
        loader=FileSystemLoader(settings.EMAIL_TEMPLATES_DIR),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template(type + '.html')
    
    message = new_message(
        from_mail=settings.EMAILS_FROM_EMAIL,
        to=email_to,
        subject=subject,
        body_text="",
        body_html=template.render(**environment),
    )

        
    t = threading.Thread(target=thread_send_email,args=(message, email_to, settings))
    t.start()


def send_team_email(
    team: Team,
    type: str = "",
    environment: Dict[str, Any] = {},
) -> None:
    assert settings.EMAILS_ENABLED, "no provided configuration for email variables"
    
    environment["server"] = settings.SERVER_NAME
    if type == 'add_team_coprod':
        subject = 'Interlink: Your team has been added to a coproduction process'
        environment["team_url"] = 'https://{server}/dashboard/organizations/{org_id}/{team_id}'.format(
            server=settings.SERVER_NAME,
            org_id=environment['org_id'],
            team_id=environment['team_id'])
        environment["link"] = 'https://{server}/dashboard/coproductionprocesses/{id}/overview'.format(
            server=settings.SERVER_NAME,
            id=environment['coprod_id'])

    elif type == 'add_member_team':
        subject = 'Interlink: You have been added to a new team'
        environment["team_url"] = 'https://{server}/dashboard/organizations/{org_id}/{team_id}'.format(
            server=settings.SERVER_NAME,
            org_id=environment['org_id'],
            team_id=environment['team_id'])
        environment["link"] = 'https://{server}/dashboard/organizations/{org_id}/{team_id}'.format(
            server=settings.SERVER_NAME,
            org_id=environment['org_id'],
            team_id=environment['team_id'])

    elif type == 'add_team_treeitem':
        subject = 'Interlink: New permissions on a coproduction item'
        environment["team_url"] = 'https://{server}/dashboard/organizations/{org_id}/{team_id}'.format(
            server=settings.SERVER_NAME,
            org_id=environment['org_id'],
            team_id=environment['team_id'])
        environment["coprod_url"] = 'https://{server}/dashboard/coproductionprocesses/{coprod_id}'.format(
            server=settings.SERVER_NAME,
            coprod_id=environment['coprod_id'])
        environment["link"] = 'https://{server}/dashboard/coproductionprocesses/{coprod_id}/{treeitem_id}/guide'.format(
            server=settings.SERVER_NAME,
            coprod_id=environment['coprod_id'],
            treeitem_id=environment['treeitem_id'])
    elif type == 'ask_team_contribution':
        subject = environment['subject']

    for user in team.users:
        env = Environment(
            loader=FileSystemLoader(settings.EMAIL_TEMPLATES_DIR),
            autoescape=select_autoescape(['html', 'xml'])
        )
        template = env.get_template(type + '.html')
        
        message = new_message(
            from_mail=settings.EMAILS_FROM_EMAIL,
            to=user.email,
            subject=subject,
            body_text="",
            body_html=template.render(**environment),
        )
        t = threading.Thread(target=thread_send_email, args=(message, user.email, settings))
        t.start()

def send_test_email(email_to: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Test email"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "added_to_process.html") as f:
        template_str = f.read()
