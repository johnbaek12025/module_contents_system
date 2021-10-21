import logging
import smtplib  # Simple Mail Transfer Protocol, 메일을 보내는데 사용되는 프로토콜
from email.mime.multipart import MIMEMultipart  # 복잡한 메세지를 작성, 이메일에 이미지를 첨부 가능

logger = logging.getLogger(__name__)


class SMTPManager(object):

    def __init__(self, **kwargs):
        self.host = kwargs.get('smtp_host')
        self.port = kwargs.get('smtp_port')
        self.sender = kwargs.get('sender')
        self.sender_pass = kwargs.get('sender_pass')
        self.recipient = kwargs.get('recipient')

    def send_email(self, subject):
        server = None
        try:
            server = smtplib.SMTP(self.host)
            server.starttls()  # TLS 인 경우는 starttls()를 실행하여 TLS Encryption을 시작
            server.login(self.sender, self.sender_pass)

            body = MIMEMultipart()
            body['subject'] = subject
            body['From'] = self.sender
            body['To'] = ",".join(self.recipient)

            server.sendmail(from_addr=self.sender, to_addrs=self.recipient, msg=body.as_string())
        except Exception as err:
            logger.error(f"sending mail to {self.host}/{self.port} failed: {err}")
        finally:
            if server:
                server.quit()   #SMTP 연결을 끊고 종료