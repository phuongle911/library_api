from app.modules.user_service.repository import UsersDAO
from app.infrastructure.repositories.user_repository import UserRepository
from app.modules.borrow_service.contracts.user_contract import UserContract


class UserClient:
    async def get_user(self, db, user_id: int) -> UserContract | None:
        user = await UsersDAO.get_by_id(db, user_id)

        if not user:
            return None
        return UserContract(
            id=user.id,
            email=user.email,
            is_active=True,
         )
