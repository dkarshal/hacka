from datetime import datetime
from enum import Enum
from typing import List, Optional
from fastapi_users import fastapi_users
from pydantic import BaseModel, Field

from fastapi import Depends, FastAPI, Request, status, HTTPException
import httpx, openai 
from auth.auth import auth_backend
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from auth.db import User
from auth.manager import get_user_manager

from auth.schemas import UserCreate, UserRead
import g4f
from g4f.Provider import (
    Bing,
)

#users=[
 #   {"id": 1, "role": "admin", "name": "q"},
 #   {"id": 2, "role": "investor", "name": "w"},
 #   {"id": 3, "role": "trader", "name": "e"},
 #   {"id": 4, "role": "trader", "name": "r", "degree": [
#        {"id": 1, "created_at": "2020-01-01T00:00:00", "type_degree": "expert"}
#        ]
#    },
#]

#class DegreeType(Enum):
#    newbie="newbie"
#    expert="expert"

#class Degree(BaseModel):
#    id: int
#    created_at: datetime
#    type_degree: DegreeType

#class User(BaseModel):
  #  id: int
  #  role: str
  #  name: str
  #  degree: Optional[List[Degree]] = []

#@app.get('/users/{user_id}', response_model=List[User])
#def get_user_by_id(user_id: int):
#    return [user for user in users if user.get("id")==user_id]
#
#ftrades=[
#    {"id": 1, "user_id": 1, "currency": "BTC", "side": "buy", "price": 123, "amount": 2.12},
#    {"id": 2, "user_id": 2, "currency": "BTC", "side": "sell", "price": 125, "amount": 2.12},
 #   {"id": 3, "user_id": 1, "currency": "BTC", "side": "buy", "price": 122, "amount": 2.12},
 #   {"id": 4, "user_id": 3, "currency": "BTC", "side": "sell", "price": 121, "amount": 2.12},
  #  {"id": 5, "user_id": 3, "currency": "BTC", "side": "sell", "price": 125, "amount": 2.12},
#    {"id": 6, "user_id": 3, "currency": "BTC", "side": "buy", "price": 124, "amount": 2.12},
#    {"id": 7, "user_id": 2, "currency": "BTC", "side": "sell", "price": 127, "amount": 2.12},
#    {"id": 8, "user_id": 1, "currency": "BTC", "side": "sell", "price": 129, "amount": 2.12},
#    {"id": 9, "user_id": 1, "currency": "BTC", "side": "sell", "price": 120, "amount": 2.12},
#]
#
#@app.get('/trades')
#def get_trades_by_limit(limit: int, offset: int):
#    return ftrades[offset:][:limit]

#users2=[
#    {"id": 1, "role": "admin", "name": "q"},
#    {"id": 2, "role": "investor", "name": "w"},
#    {"id": 3, "role": "trader", "name": "e"}
#]

#@app.post('/users/{user_id}')
#def change_uname(user_id: int, new_name: str):
#    current_user = list(filter(lambda user: user.get('id')==user_id, users2))[0]
#    current_user['name'] = new_name
#    return {"message": f"username with user id {user_id} has changed uname", "data": current_user}
    ##users2[user_id]["name"] = new_name
    ##return {"message": f"username with user id {user_id} has changed uname", "data": users2[user_id]}

#class Trade(BaseModel):
    #id: int
    #user_id: int
    #currency: str = Field(max_length=3)
   # side: str
  #  price: float = Field(ge=0)
 #   amount: float

#@app.post('/trades')
#def add_trades(trades: List[Trade]):
#    ftrades.extend(trades)
#    return {"data": ftrades}
fastapi_users = fastapi_users.FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

app = FastAPI()

@app.get('/')
def hi():
    return 'in development...' 

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

current_user = fastapi_users.current_user()

@app.get("/protected-route")
def protected_route(user: User = Depends(current_user)):
    return f"Hello, {user.email}"

@app.get("/unprotected-route")
def unprotected_route():
    return f"Hello, anon"

@app.get("/askgpt")
def ask_gpt(prompt: str)->str:
    response = g4f.ChatCompletion.create(
    model="gpt-3.5-turbo",
    provider=g4f.Provider.Bing,
    messages=[{"role": "user", "content": prompt}],
    )
    return response