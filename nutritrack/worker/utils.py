import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from nutritrack.api.settings import get_settings
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

settings = get_settings()


def send_email(to: str, subject: str, html_body: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.mail_from
    msg["To"] = to
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(settings.mail_username, settings.mail_password)
        server.sendmail(settings.mail_from, to, msg.as_string())


def render_html(summary_data: dict) -> str:
    template_dir = Path(__file__).parent.parent / "admin" / "templates"
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template("admin/weekly_report_email.html")
    html_body = template.render(**summary_data)
    return html_body
