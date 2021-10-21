import ftplib
import os
import logging

logger = logging.getLogger(__name__)


class FTPManager(object):
    def __init__(self):
        self.conn = None
        self.uri = None

    def connect(self, ftp_host, ftp_port, ftp_user, ftp_pass, ftp_path):
        self.uri = f"{ftp_host}:{ftp_port}/{ftp_path}"
        logger.info(f"connect to ftp server {self.uri}")
        try:
            self.conn = ftplib.FTP()
            self.conn.set_pasv(False)
            self.conn.connect(ftp_host, ftp_port)
            self.conn.login(ftp_user, ftp_pass)
            self.conn.cwd(ftp_path)
        except Exception as err:
            logger.error(f"ftp connection to {self.uri} failed: {err}")
            raise

    def disconnect(self):
        if self.conn:
            logger.info(f"disconnect from ftp server")
            self.conn.close()

    def send(self, from_path, to_path):
        try:
            with open(from_path, "rb") as file:
                self.conn.storbinary(f"STOR {to_path}", file)
                logger.info(f"[ftp] file sending to {self.uri} completed")
        except Exception as err:
            logger.error(
                f"[ftp] file sending from {from_path} to {to_path} failed: {err}"
            )
            raise

    def check_path(self, path):
        if not self.directory_exists(path):
            self.conn.mkd(path)

    def directory_exists(self, path):
        filelist = []
        self.conn.retrlines("LIST", filelist.append)
        for f in filelist:
            if f.split()[-1] == path and f.upper().startswith("D"):
                return True
        return False
