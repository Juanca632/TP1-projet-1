from typing import List, Optional
from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel, Field
from uuid import UUID
import uuid
import sqlite3
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configuración de CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ruta de la base de datos SQLite
DB_NAME = "users.db"

# Modelo para la información del usuario
class UserRegister(BaseModel):
    user_id: UUID
    name: str
    lastname: str
    role: str

# Función para obtener los usuarios desde la base de datos
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Para acceder a los campos por nombre
    return conn

# Endpoint para obtener la lista de usuarios
@app.get(
    path="/users",
    status_code=status.HTTP_200_OK,
    summary="Show users",
    tags=["Users"]
)
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()

    return [{"user_id": row["user_id"], "name": row["name"], "lastname": row["lastname"], "role": row["role"]} for row in users]

# Endpoint para crear un nuevo usuario
@app.post(
    path="/create-user",
    response_model=UserRegister,
    status_code=status.HTTP_201_CREATED,
    summary="Create a user",
    tags=["Create"]
)
def create_user(user: UserRegister):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Generar un nuevo UUID si el user_id no es proporcionado
    user_id = str(uuid.uuid4())  # Genera un UUID único

    cursor.execute(
        "INSERT INTO users (user_id, name, lastname, role) VALUES (?, ?, ?, ?)",
        (user_id, user.name, user.lastname, user.role),
    )
    conn.commit()
    conn.close()

    return {**user.dict(), "user_id": user_id}

# Endpoint para actualizar un usuario (PUT)
@app.put(
    path="/update-user/{user_id}",
    response_model=UserRegister,
    status_code=status.HTTP_200_OK,
    summary="Update a user",
    tags=["Update"]
)
def update_user(user_id: UUID, user: UserRegister):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Buscar si el usuario existe
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (str(user_id),))
    existing_user = cursor.fetchone()

    if existing_user is None:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    # Actualizar usuario
    cursor.execute(
        "UPDATE users SET name = ?, lastname = ?, role = ? WHERE user_id = ?",
        (user.name, user.lastname, user.role, str(user_id)),
    )
    conn.commit()
    conn.close()

    return {**user.dict(), "user_id": str(user_id)}

# Endpoint para eliminar un usuario (DELETE)
@app.delete(
    path="/delete-user/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
    tags=["Delete"]
)
def delete_user(user_id: UUID):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Buscar si el usuario existe
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (str(user_id),))
    existing_user = cursor.fetchone()

    if existing_user is None:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    # Eliminar usuario
    cursor.execute("DELETE FROM users WHERE user_id = ?", (str(user_id),))
    conn.commit()
    conn.close()

    return {"detail": "User deleted"}

@app.get(
    path="/user/{user_id}",
    response_model=UserRegister,
    status_code=status.HTTP_200_OK,
    summary="Get a user by ID",
    tags=["Users"]
)
def get_user_by_id(user_id: UUID):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Buscar al usuario por su user_id
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (str(user_id),))
    user = cursor.fetchone()
    conn.close()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {"user_id": user["user_id"], "name": user["name"], "lastname": user["lastname"], "role": user["role"]}