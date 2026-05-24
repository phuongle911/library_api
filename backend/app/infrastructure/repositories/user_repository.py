from app.DAO.users_dao import UsersDAO

class UserRepository:

    @staticmethod
    async def get_by_id(db, user_id: int):
        return await UsersDAO.get_by_id(db, user_id)
