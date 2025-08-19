# backend/main.py

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Optional
import json

from db_manager import initialize_db, db, Event
from auth_manager import AuthManager
from camera_stream import CameraThread
from pydantic import BaseModel

# Inicializar o banco de dados
initialize_db()

# Inicializar o gerenciador de autenticação
auth_manager = AuthManager()

# Configuração do FastAPI
app = FastAPI()

# Definição de schemas Pydantic (para validação de dados)
class UserLogin(BaseModel):
    username: str
    password: str

class EventResponse(BaseModel):
    id: int
    event_type: str
    camera_name: str
    timestamp: str
    image_path: Optional[str]
    video_path: Optional[str]

    class Config:
        orm_mode = True # Habilita o uso com modelos do Peewee

@app.on_event("startup")
async def startup():
    if db.is_closed():
        db.connect()

@app.on_event("shutdown")
async def shutdown():
    if not db.is_closed():
        db.close()

# ROTA DE AUTENTICAÇÃO
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth_manager.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Em uma implementação real, você geraria um token JWT aqui
    return {"access_token": user["username"], "token_type": "bearer"}

# ROTA PARA EVENTOS (RELATÓRIOS)
@app.get("/events", response_model=List[EventResponse])
def get_events():
    """Retorna uma lista de todos os eventos registrados."""
    return list(Event.select().order_by(Event.timestamp.desc()))

# A API precisa de mais rotas para gerenciar câmeras e rostos
# Vamos construir isso nas próximas etapas.