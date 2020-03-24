import os
import email
import imaplib


class Gmail:
    def __init__(self, username: str = None, password: str = None, target: str = 'INBOX',
                 subject: str = None, since: str = None, unread: bool = False):

        self.username = username or os.getenv("GMAIL_USER")
        self.password = password or os.getenv("GMAIL_PASS")

        assert self.username
        assert self.password

        self.imap_host = 'imap.gmail.com'
        self.imap_port = '993'
        self.folder = target

        if since:
            self.search_terms = f'SINCE "{since}" SUBJECT "{subject}"'
        else:
            self.search_terms = f'SUBJECT "{subject}"'
        if unread:
            self.search_terms += " UNSEEN"
        self.server = imaplib.IMAP4_SSL(self.imap_host, self.imap_port)

        self.message_ids = None

    def __call__(self):

        self._login()
        self.search()
        self.retrieve_message(self.message_ids[0])

    def _login(self):
        self.server.login(self.username, self.password)
        self.server.select(self.folder)

    def search(self):
        message_ids = self.server.search(None, self.search_terms)
        self.message_ids = message_ids[1][0].split()
        print(f"Got {len(self.message_ids)} messages")

    def retrieve_message(self, message_id):
        typ, data = self.server.fetch(message_id, '(RFC822)')
        for rp in data:
            if isinstance(rp, tuple):
                msg = email.message_from_string(rp[1].decode('UTF-8'))
                subject = msg["subject"]
                body = msg.get_payload()
                print(subject)
                print(body)


if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser()
    parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter
    parser.add_argument("--user", help="Gmail username", default=None)
    parser.add_argument("--password",
                        help="Gmail password. This may require an app password (https://support.google.com/mail/answer/185833?hl=en-GB)",
                        default=None)
    parser.add_argument("--target", help="Which folder (called labels in Gmail) to target",
                        default="INBOX")
    parser.add_argument("--subject", help="A substring-sensitive subject to search for new messages",
                        default="HELLO WORLD")
    parser.add_argument("--since", help="Search only after this date. Required format is dd-mmm-yyyy e.g. 25-Dec-2018",
                        default=None)
    parser.add_argument("--unread", help="Include only unread messages", type=bool, default=False)
    args = parser.parse_args()

    g = Gmail(args.user, args.password, args.target, args.subject, args.since, args.unread)()

