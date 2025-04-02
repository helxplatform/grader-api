import string
import secrets
from passlib.context import CryptContext

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class PasswordHelper:
    @staticmethod
    def hash_password(password: str) -> str:
        return password_context.hash(password)
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return password_context.verify(password, hashed_password)
    
    # Generate a variable-length cryptographically secure password
    @staticmethod
    def generate_password(length: int) -> str:
        characters = string.ascii_letters + string.digits + '+/= '
        password = "".join(secrets.choice(characters) for i in range(length))
        return password