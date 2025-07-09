# app/schemas/token.py

from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    # Tambahkan field lain yang mungkin ada di payload token jika diperlukan
    user_id: Optional[int] = None
    is_superuser: Optional[bool] = None
    company_id: Optional[int] = None