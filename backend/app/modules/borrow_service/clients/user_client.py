from app.modules.user_service.repository import UsersDAO


class UserClient:
    async def get_user(self, db, user_id: int):
        return await UsersDAO.get_by_id(db, user_id)