import sqlite3

# Conexión a la base de datos (se crea si no existe)
conn = sqlite3.connect('users.db')

# Crear un cursor
cursor = conn.cursor()

# Crear tabla de usuarios
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    name TEXT,
    lastname TEXT,
    role TEXT
)
''')

# Cerrar la conexión
conn.commit()
conn.close()

print("Base de datos y tabla de usuarios creadas exitosamente.")
