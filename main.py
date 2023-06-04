import fetch_feeds
import send_email
import operator
import datetime
import pytz



def get_last_email_timestamp():
    """Retrieve the last email timestamp from a file or database."""
    try:
        with open('last_email_timestamp.txt', 'r') as file:
            timestamp = file.read().strip()
            return datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.UTC)
    except FileNotFoundError:
        # Return a default timestamp if the file is not found
        return datetime.datetime.min.replace(tzinfo=pytz.UTC)


def store_last_email_timestamp(timestamp):
    """Store the last email timestamp to a file or database."""
    with open('last_email_timestamp.txt', 'w') as file:
        file.write(timestamp.strftime('%Y-%m-%d %H:%M:%S'))


def filter_entries(entries, last_email_timestamp):
    """Filter entries based on the last email timestamp."""
    filtered_entries = []
    for entry in entries:
        published_date = entry.get('published')
        if published_date:
            entry_timestamp = datetime.datetime.strptime(published_date, '%a, %d %b %Y %H:%M:%S %z')
            if entry_timestamp > last_email_timestamp:
                filtered_entries.append(entry)
    return filtered_entries

def main():
    """Main function to orchestrate the operations."""
    journals = fetch_feeds.read_journals_from_csv('journals.csv')

    all_entries = []
    for journal_name, rss_url in journals.items():
        entries = fetch_feeds.get_feed_entries(rss_url)
        for entry in entries:
            entry['journal_name'] = journal_name  # Add journal name to each entry
        all_entries.extend(entries)

    # Sort the articles by journal name
    all_entries.sort(key=operator.itemgetter('journal_name'))

    # Get the last email timestamp from a file or database
    last_email_timestamp = get_last_email_timestamp()

    # Filter entries based on last email timestamp
    filtered_entries = filter_entries(all_entries, last_email_timestamp)

    # Format the email body
    email_body = send_email.format_email(filtered_entries)

    recipient_email = 'jhgearon@iu.edu'

    sender_email, sender_password = send_email.get_sender_credentials()

    send_email.send_email(email_body, sender_email, sender_password, recipient_email)

    # Store the timestamp of the current execution as the last email timestamp
    store_last_email_timestamp(datetime.datetime.now())



if __name__ == '__main__':
    main()
