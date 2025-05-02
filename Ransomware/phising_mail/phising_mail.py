import smtplib
from email.message import EmailMessage
import getpass
import re

with open("egyptian_first_names.txt", "r") as f:
    EGYPTIAN_FIRST_NAMES = [line.strip() for line in f if line.strip()]


def extract_first_name(email):
    local_part = email.split("@")[0].lower()
    for name in EGYPTIAN_FIRST_NAMES:
        if local_part.startswith(name.lower()):
            return name
    return "Intern"


def send_bulk_email(
    addresses_file: str,
    message_file: str,
    smtp_server: str,
    smtp_port: int,
    username: str,
    password: str,
    subject: str,
):
    # Read recipient addresses
    with open(addresses_file, "r") as f:
        recipients = [line.strip() for line in f if line.strip()]

    # Read email body
    with open(message_file, "r") as f:
        body_template = f.read()

    # Connect and authenticate to the SMTP server
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Secure the connection
        server.login(username, password)

        # Send email to each recipient
        for recipient in recipients:
            first_name = extract_first_name(recipient)
            print(f"Sending email to {recipient} with first name {first_name}")

            # Personalize the greeting
            body = body_template.replace("Dear ,", f"Dear {first_name},")
            msg = EmailMessage()
            msg["From"] = username
            msg["To"] = recipient
            msg["Subject"] = subject
            msg.set_content(body)
            server.send_message(msg)
            print(f"Email sent to {recipient}")


if __name__ == "__main__":
    # Read username and password from my_mail.txt
    # Format: first line = username, second line = password
    with open("my_mail.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]
        username = lines[0]
        password = lines[1]

    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    subject = "Welcome to EFG Holding's 2025 Summer Internship Program"

    send_bulk_email(
        "mails_address.txt",
        "phising_mail.txt",
        smtp_server,
        smtp_port,
        username,
        password,
        subject,
    )
