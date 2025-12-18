from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.database import get_db
from app.core.dependencies import get_current_user

user_router = APIRouter()

# @user_router.post("/users/", response_model=UserResponse)   
# async def create_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):
#    result = await db.execute(select(User).where(User.email == payload.email))
#    existing_user = result.scalar_one_or_none()
#    if existing_user:
#       raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already use") 
#    user = User(**payload.model_dump())
#    db.add(user)
#    await db.commit()
#    await db.refresh(user)
#    return user

@user_router.get("/users/", response_model=list[UserResponse])
async def list_users(
   name: str | None = None, 
   email: str | None = None, 
   sort_by: str | None = None,
   db: AsyncSession = Depends(get_db),
   current_user: User = Depends(get_current_user)
   ):
   
   query = select(User)

   #Apply fliter name if provided
   if name:
      query = query.where(User.name.ilike(f"%{name}%"))

   #Apply filter email if provided
   if email:
      query = query.where(User.email.ilike(f"%{email}%"))

   #Apply sort_by 
   if sort_by == "name":
      query = query.order_by(User.name)
   elif sort_by == "email":
      query = query.order_by(User.email)
   elif sort_by == "oldest":
      query = query.order_by(User.id.asc())
   elif sort_by == "newest":
      query = query.order_by(User.id.desc())

   
   result = await db.execute(query)
   users = result.scalars().all()
   if not users:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user found")
   return users


# @user_router.get("/users/{user_id}", response_model=UserResponse)
# async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
#    result = await db.execution(select(User).where(User.id == user_id))
#    users = result.scalars().first()
#    if not users:
#       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
#    return users

@user_router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
   user_id: int,
   db: AsyncSession = Depends(get_db),
   current_user: User = Depends(get_current_user),
   ):
   user = await db.get(User, user_id)
   if not user:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
   return user

@user_router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, payload: UserUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
   user = await db.get(User, user_id)
   if not user:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
   if user_id != current_user.id:
      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this user")
   for key, value in payload.model_dump().items():
      setattr(user, key, value)
      db.add(user)
      await db.commit()
      await db.refresh(user)
      return user
   
@user_router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
   user = await db.get(User, user_id)
   if not user:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
   if user_id != current_user.id:
      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this user")
   await db.delete(user)
   await db.commit()
   return {"message": "User deleted"}

