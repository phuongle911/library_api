from app.modules.user_service.repository import UsersDAO
from app.infrastructure.repositories.user_repository import UserRepository


class UserClient:
    async def get_user(self, db, user_id: int):
        """
        Future:
        GET /users/{id}
        """       
        return await UserRepository.get_by_id(db, user_id)