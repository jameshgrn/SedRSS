# Sedimentary Geology RSS Feed Newsletter (SedRSS)

## Description

This repository contains code for fetching and processing RSS feeds from various journals in the field of sedimentary geology. The code retrieves the latest publications from the specified journals, filters them based on the last email timestamp, and sends an email newsletter with the selected articles.

## Files

- **journals.csv**: CSV file containing the list of journals and their corresponding RSS feed URLs.
- **output_file_gptloader.txt**: Placeholder file.
- **config.ini**: Configuration file containing email and OpenAI API credentials.
- **last_email_timestamp.txt**: Text file storing the timestamp of the last sent email.
- **main.py**: Main script that orchestrates the operations of fetching, filtering, and sending emails.
- **send_email.py**: Module containing functions for generating the email body, formatting the email, and sending the email using SMTP.
- **fetch_feeds.py**: Module containing functions for reading the journals from the CSV file and fetching the RSS feed entries.

## Instructions

To use the code in this repository, follow the steps below:

1. Update the `journals.csv` file with the desired list of journals and their corresponding RSS feed URLs.
2. Set up the email credentials in the `config.ini` file, including the sender's email address and password.
3. Set up the OpenAI API key in the `config.ini` file.
4. Run the `main.py` script to fetch the latest publications, filter them based on the last email timestamp, generate the email body, and send the email to the specified recipient.
5. The timestamp of the current execution will be stored in the `last_email_timestamp.txt` file, which will be used as the last email timestamp for subsequent executions.

Note: The `main.py` script includes two versions of the `main()` function. The `main()` function fetches all entries from the RSS feeds and filters them based on the last email timestamp. The `main_for_testing()` function selects one article from each journal for testing purposes. Choose the appropriate function based on your requirements.

## Dependencies

The code in this repository requires the following dependencies:

- Python 3.x
- Pandas
- Feedparser
- smtplib (standard library)
- email.mime.multipart (standard library)
- email.mime.text (standard library)

Install the dependencies using pip:

`pip install pandas feedparser`


## Contributing

Contributions to this repository are welcome. If you find any issues or have suggestions for improvement, please open an issue or submit a pull request.

## License

This repository is licensed under the [MIT License](LICENSE).



