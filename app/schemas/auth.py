from pydantic import BaseModel


class UserPayload(BaseModel):
    id: str
    nome: str
    usuario: str
    is_admin: bool
    pode_abastecer: bool


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserPayload | None = None


class LoginRequest(BaseModel):
    username: str
    password: str
