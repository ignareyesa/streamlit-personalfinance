import smtplib


class EmailClient:
    """
    A class for sending emails using an SMTP server.
    """

    def __init__(
        self, smtp_server, smtp_port, username, password, from_addr, from_name
    ):
        """
        Creates a new instance of the `EmailClient` class.

        Args:
            smtp_server (str): The address of the SMTP server to be used for sending emails.
            smtp_port (int): The port number for the SMTP server.
            username (str): The username to be used for logging into the SMTP server.
            password (str): The password to be used for logging into the SMTP server.
            from_addr (str): The email address that the email will be sent from.
            from_name (str): The name of the sender that will appear in the email.
        """

        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.from_addr = from_addr
        self.from_name = from_name
        self.username = username
        self.password = password

        # Init connection
        self.server = smtplib.SMTP(smtp_server, smtp_port)
        self.server.starttls()
        self.server.login(username, password)

    def _close_connection(self):
        """
        Helper method to close the connection to the SMTP server.
        """
        self.server.quit()

    def send_email(self, to_addr, to_name, subject, body):
        """
        Sends an email using the provided arguments.

        Args:
            to_addr (str): The email address that the email will be sent to.
            to_name (str): The name of the recipient that will appear in the email.
            subject (str): The subject of the email.
            body (str): The body of the email.
        """

        msg = f"""From: {self.from_name} <{self.from_addr}>
        To: {to_name} <{to_addr}>
        Subject: {subject}
        
        {body}"""
        print(msg)

        self.server.sendmail(self.from_addr, to_addr, msg.encode("utf-8"))
        self._close_connection()
