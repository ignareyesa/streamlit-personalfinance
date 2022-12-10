import smtplib

class EmailClient:
    """
    """
    def __init__(self, smtp_server, smtp_port, username, password, from_addr, from_name):
        """
        
        """

        # Dirección del servidor SMTP y puerto
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

        # Nombre de usuario y contraseña para iniciar sesión en el servidor
        username = username
        password = password

        # Establecer una conexión segura (TLS) con el servidor SMTP
        self.server = smtplib.SMTP(smtp_server, smtp_port)
        self.server.starttls()
        self.server.login(username, password)

        # Establecer quien escribe
        self.from_addr = from_addr
        self.from_name = from_name

    def _close_connection(self):
        self.server.quit()

    def send_email(self,to_addr,to_name,subject,body):
        
        msg = f"""From: {self.from_name} <{self.from_addr}>
        To: {to_name} <{to_addr}>
        Subject: {subject}
        
        {body}"""

        self.server.sendmail(self.from_addr, to_addr, msg.encode("utf-8"))
        self._close_connection()

