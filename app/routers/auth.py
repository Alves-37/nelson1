from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.db.session import AsyncSessionLocal
from app.db.models import User
from app.schemas.auth import Token, UserPayload
from app.core.security import create_access_token, verify_password

router = APIRouter()

async def get_db_session():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/auth/login", response_model=Token, tags=["Auth"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db_session)):
    """Authenticate user and return a JWT access token."""
    # Case-insensitive username lookup to align with client behavior
    result = await db.execute(
        select(User).where(func.lower(User.usuario) == func.lower(func.cast(form_data.username, User.usuario.type)))
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Bloquear usuários inativos
    if not user.ativo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")

    # Permitir login online apenas para administradores
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not allowed to access online system")

    access_token = create_access_token(data={"sub": user.usuario, "user_id": str(user.id)})
    user_payload = UserPayload(
        id=str(user.id),
        nome=user.nome,
        usuario=user.usuario,
        is_admin=user.is_admin,
        pode_abastecer=user.pode_abastecer,
    )
    return {"access_token": access_token, "token_type": "bearer", "user": user_payload}
