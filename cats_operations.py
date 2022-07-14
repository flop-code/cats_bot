from config import FTP_HOST
import ftplib
from io import BytesIO
from os import environ
from typing import Final


# Signs, that are not allowed in filenames.
SPECIAL_SIGNS: Final[tuple] = (
    "\\", "/", "|",
    "<", ">",
    "*", "?", "\"", ":"
)


def get_return_code(msg: str) -> int:
    # To get return code from message string.
    return int(msg[:3])


def get_connection_to_ftp_folder() -> ftplib.FTP:
    # Returns ftp client, connected to folder in FTP serv
    
    ftp: ftplib.FTP = ftplib.FTP(timeout=120)
    ftp.connect(FTP_HOST)
    ftp.login(environ["FTP_USERNAME"], environ["FTP_PASSWORD"])
    ftp.cwd("htdocs/")

    return ftp


def get_cat() -> BytesIO:
    # Load cat and description from FTP server and return them.

    ftp: ftplib.FTP = get_connection_to_ftp_folder()

    fnames: list = ftp.nlst()
    filename: str = fnames[-1]
    description: str = ".".join(filename.split(".")[:-1])
    with open("temp.jpg", "wb") as f:
       msg: str = ftp.retrbinary(f'RETR {filename}', f.write)
    if get_return_code(msg) != 226:
       print(f"FTP getting image error {msg}.")
       return
    
    with open("temp.jpg", "rb") as f:
        image: BytesIO = BytesIO(f.read())

    ftp.delete(filename)
    ftp.quit()

    return image, description


def get_description_and_save_cat(message, image: bytes) -> int:
    """ Get description from TG bot admin.
    returns special exit codes:
        0 - OK
        1 - Description contains signs, that are not allowed in filename.
        2 - Error while uploading file to FTP server.
    """

    ftp: ftplib.FTP = get_connection_to_ftp_folder()

    for sign in SPECIAL_SIGNS:
        if sign in message.text:
            return 1
    
    filename: str = message.text + ".png"
    msg: str = ftp.storbinary(f"STOR {filename}", BytesIO(image), blocksize=1024**2)
    ftp.quit()

    if get_return_code(msg) != 226:
        print(f"Error with code {msg}")
        return 2

    return 0
