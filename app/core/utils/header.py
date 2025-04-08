from typing import Tuple
from email.message import EmailMessage

""" https://docs.python.org/3.11/library/cgi.html#cgi.parse_header """
def parse_content_disposition_header(header_value: str) -> Tuple[str, dict]:
    message = EmailMessage()
    message["Content-Disposition"] = header_value
    return message.get_content_disposition(), message["content-disposition"].params