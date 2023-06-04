import configparser
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
import os
from email.mime.text import MIMEText

import openai

# Set your OpenAI API key
config = configparser.ConfigParser()
config.read('config.ini')
openai.api_key = config.get('openai', 'api_key')

def generate_greeting(titles, journals):
    """
    Generate a personalized greeting message using GPT via OpenAI API.
    """
    # Combine the titles into a single string
    titles_text = ", ".join(titles)
    journals_text = ", ".join(journals)

    # Generate the prompt for GPT
    system_msg = f"You are the manager of SedRSS, an RSS service dedicated to providing the latest publications in " \
                 f"sedimentary geology to professional researchers and academics. Your task is to create a " \
                 f"personalized " \
                 f"greeting message for the email body, briefing the readers on the selected articles for this week's " \
                 f"" \
                 f"newsletter.\n" \
                 f"Here are the titles of the articles: {titles_text}\n" \
                 f"The articles are from the following journals: {journals_text}\n" \
                 f"Please choose 1-3 articles based on the quality of the title, prestige of the journal, " \
                 f"relevance to " \
                 f"sedimentary geology, and inclusion of an abstract. Generate short titles or use existing short " \
                 f"titles instead of the full title.\n" \
                 f"Construct a concise but friendly greeting message that summarizes the selected articles, " \
                 f"highlighting " \
                 f"their significance and why they were chosen. Your output must be NO MORE than 150 words. " \
                 f"Additionally, you will return the text in HTML/CSS formatting intended for an email. Be creative " \
                 f"while maintaining professionalism.\n" \
                 f"Here are some other rules to follow:\n" \
                 f"1. Always say Dear SedRSS X, where X is a fill in for community, family, subscribers, devotees, " \
                 f"etc.,.\n" \
                 f"2. Always include <p>-- SedRSS Management</p> at the end of the message\n" \
                 """3. Always use this formatting for the email body beginning:
                     <!DOCTYPE html>
                     <html>
                     <head>
                       <title>SedRSS Newsletter</title>
                       <style>
                         body {
                           font-family: Arial, sans-serif;
                           background-color: #f2f2f2;
                           margin: 0;
                           padding: 20px;
                         }

                         h1 {
                           color: #333;
                           font-size: 24px;
                           margin-bottom: 20px;
                         }

                         p {
                           color: #555;
                           font-size: 16px;
                           line-height: 1.5;
                           margin-bottom: 10px;
                         }

                         strong {
                           font-weight: bold;
                         }

                         em {
                           font-style: italic;
                         }
                       </style>
                     </head>
                     <body>
                       <p>Hey Sed Folks!</p>\n
                Here is an example of a greeting message, use it as a template.\n"""

    system_msg += """
                      <!DOCTYPE html>
                      <html>
                      <head>
                        <title>SedRSS Newsletter</title>
                        <style>
                          body {
                            font-family: Arial, sans-serif;
                            background-color: #f2f2f2;
                            margin: 0;
                            padding: 20px;
                          }

                          h1 {
                            color: #333;
                            font-size: 24px;
                            margin-bottom: 20px;
                          }

                          p {
                            color: #555;
                            font-size: 16px;
                            line-height: 1.5;
                            margin-bottom: 10px;
                          }

                          strong {
                            font-weight: bold;
                          }

                          em {
                            font-style: italic;
                          }
                        </style>
                      </head>
                      <body>
                        <p>Hey Sed Folks!</p>
                        <p>Welcome to this week's edition of the SedRSS newsletter. We've hand-picked a selection of 
                        articles that we think will be of particular interest to sedimentary geologists:</p>
                        <p><em><strong>Rift propagation unravelled:</strong></em> This short communication in the 
                        journal <em>Marine and Petroleum Geology</em> examines Cenozoic subsidence patterns in the 
                        South China Sea, using them to understand the eastward propagation of continental rifting.</p>
                        <p><em><strong>Aerosol forcing weakened:</strong></em> The relationship between aerosols and 
                        clouds is complex; this article in <em>Geophysical Research Letters</em> argues that biomass 
                        burning is increasing atmospheric variability, making the impact of aerosol forcing less 
                        clear.</p>
                        <p><em><strong>The taphonomic clock:</strong></em> This <em>Sedimentary Geology</em> article 
                        describes a new way to track the age of coral reef stratigraphy using sediment grain size as 
                        a clock.</p>
                        <p>We hope you find these articles as thought-provoking as we did. Happy reading!</p>
                        <p>-- SedRSS Management</p>
                      </body>
                      </html>
                    """

    # Create a dataset using GPT
    response = openai.ChatCompletion.create(model = "gpt-3.5-turbo",
                                            messages = [{"role": "system", "content": system_msg}], max_tokens = 2000)

    # Return the generated message
    return response["choices"][0]["message"]["content"]


def format_email(entries):
    """Format the entries into a string for the email body."""

    # Retrieve titles and journals for generating the greeting
    titles = [entry['title'] for entry in entries]
    journals = list(set(entry['journal_name'] for entry in entries))
    # Generate personalized greeting using the updated generate_greeting function
    greeting = generate_greeting(titles, journals)

    email_body = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                }}
                h1 {{
                    color: #333333;
                    font-size: 24px;
                    margin-bottom: 20px;
                    text-align: center;
                    text-transform: uppercase;
                    text-decoration: underline;
                    font-weight: bold;
                }}
                h2 {{
                    color: #333333;
                    font-size: 20px;
                    margin-bottom: 10px;
                }}
                h3 {{
                    color: #0000EE;
                    font-size: 18px;
                    margin-top: 15px;
                }}
                p {{
                    font-size: 16px;
                    margin-top: 5px;
                    margin-bottom: 10px;
                }}
                a {{
                    text-decoration: none;
                    color: #0000EE;
                }}
                .small-italic {{
                    font-size: 12px;
                    font-style: italic;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
        <h1>SedRSS Newsletter</h1>
        <p class="small-italic">Implemented and managed by Jake Gearon and GPT</p>
        <p>{greeting}</p>
    """

    current_journal = None

    for entry in entries:
        journal_name = entry.get('journal_name')

        # Add journal name if it has changed
        if journal_name != current_journal:
            current_journal = journal_name
            email_body += f"<h2>{journal_name}</h2>\n"

        title = entry.get('title')
        link = entry.get('link')
        email_body += f"<h3><a href='{link}'>{title}</a></h3>\n"

        if 'summary' in entry:
            email_body += f"<p>{entry['summary']}</p>\n"

    email_body += "</body></html>"

    return email_body





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
    sender_email = os.environ['EMAIL_USERNAME']
    sender_password = os.environ['EMAIL_PASSWORD']
    return sender_email, sender_password

