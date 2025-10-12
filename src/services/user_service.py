from src.models.user import User, Department
from sqlalchemy.orm import Session
import bcrypt


class UserService:
    def create_user(
        self,
        db: Session,
        username: str,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        phone: str,
        department: Department,
    ) -> User:
        """Create a new user with hashed password.

        Args:
            db: Database session
            username: Unique username
            email: User email address
            password: Plain text password (will be hashed)
            first_name: User's first name
            last_name: User's last name
            phone: User's phone number
            department: User department (COMMERCIAL, GESTION, or SUPPORT)

        Returns:
            Created User object
        """
        # Hash the password using bcrypt
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            department=department,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash.

        Args:
            password: Plain text password to verify
            password_hash: Hashed password from database

        Returns:
            True if password matches, False otherwise
        """
        password_bytes = password.encode('utf-8')
        password_hash_bytes = password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, password_hash_bytes)
