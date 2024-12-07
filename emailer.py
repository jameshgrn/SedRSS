import configparser

config = configparser.ConfigParser()
config.read('config.ini')

def send_email(email_body, sender_email, sender_password, recipient_email):
    """Send an email with the list of new articles."""
    msg = MIMEMultipart('alternative')
    msg['From'] = sender_email
    msg['To'] = recipient_email

    # Create subject line with date and description
    current_date = datetime.date.today().strftime("%m-%d-%Y")
    subject_line = f"SedRSS: New Articles from around the Field ({current_date})"
    msg['Subject'] = subject_line

    # Attach the HTML version
    html_part = MIMEText(email_body, 'html')
    msg.attach(html_part)

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()

    server.login(sender_email, sender_password)
    server.send_message(msg)
    server.quit()
    print("Email sent!")


def get_sender_credentials():
    """Retrieve sender credentials from secrets."""
    sender_email = config["email"]["SENDER_EMAIL"]
    sender_password = config["email"]["SENDER_PASSWORD"]
    return sender_email, sender_password