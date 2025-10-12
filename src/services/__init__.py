"""Services package for Epic Events CRM."""

from .user_service import UserService

# Create singleton instances
user_service = UserService()
