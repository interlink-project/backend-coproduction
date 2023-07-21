# Import modules
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader, select_autoescape
from email.utils import make_msgid, formatdate

def send_template_email(template, to, subj, **kwargs):
    """Sends an email using a template."""
    env = Environment(
        loader=FileSystemLoader('../../email-templates/build/'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template(template)
    send_email(to, subj, template.render(**kwargs))

def send_email(to, subj, body):
    # me == my email address
    # you == recipient's email address
    me = 'admin@interlink-project.eu'
    you = 'ruben.sanchez@deusto.es'
    password = 's&g-e4EgKl_3/?lP'

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Testing"
    msg['From'] = me
    msg['To'] = you

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText("You have been added to a new team! https://dev.interlink-project.eu", 'plain')
    part2 = MIMEText(body, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)
    msg['Message-ID'] = make_msgid(domain='interlink-project.eu')
    msg['Date'] = formatdate(timeval=None, localtime=False, usegmt=False)

    # Send the message via local SMTP server.
    mail = smtplib.SMTP('mail.interlink-project.eu', 587)

    mail.ehlo()

    mail.starttls()

    mail.login(me, password)
    mail.sendmail(me, you, msg.as_string())
    mail.quit()
    
        
if __name__ == "__main__":
    send_template_email('add_member_team.html','a','b')