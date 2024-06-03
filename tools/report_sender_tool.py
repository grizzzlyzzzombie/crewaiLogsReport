import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from crewai_tools import BaseTool

smtp_server = "localhost"
smtp_port = 1025
sender_email = "aiisthebest@baza.eto"
receiver_email = "krasiviemail@gmail.com"


class SendEmailTool(BaseTool):
    name: str = "Email Sender"
    description: str = "Send report to email"

    def _run(self, message_body: str) -> str:
        print(f"\nkwargs: {message_body}\n")

        if not message_body:
            return "'message_body' must be provided."

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = "Report"
        msg.attach(MIMEText(message_body, 'plain'))

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.sendmail(sender_email, receiver_email, msg.as_string())
                return "Email sent successfully!"
        except Exception as e:
            return f"Failed to send email: {e}"
