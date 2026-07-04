import resend
from nutritrack.api.settings import get_settings
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

settings = get_settings()


def send_email(to: str, subject: str, html_body: str) -> None:
    resend.api_key = settings.resend_api_key
    params = {
        "from": settings.mail_from,
        "to": [to],
        "subject": subject,
        "html": html_body,
    }
    resend.Emails.send(params)


def render_html(summary_data: dict) -> str:
    template_dir = Path(__file__).parent.parent / "admin" / "templates"
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template("admin/weekly_report_email.html")
    return template.render(**summary_data)
