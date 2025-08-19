from peewee import *
import datetime
import os
import mysql.connector

# Configurações do banco de dados MySQL
db = MySQLDatabase(
    database='phoenix_vision_db',
    user='root',
    password='davi080401',  # <-- Corrigido: a senha agora é uma string
    host='localhost',
    port=3306,
)

class BaseModel(Model):
    class Meta:
        database = db

class Event(BaseModel):
    event_type = CharField()
    camera_name = CharField()
    timestamp = DateTimeField(default=datetime.datetime.now)
    image_path = CharField(null=True)
    video_path = CharField(null=True)

    class Meta:
        db_table = 'events'

def initialize_db():
    try:
        db.connect()
        db.create_tables([Event])
        print("Tabela 'events' criada com sucesso.")
    except OperationalError as e:
        print(f"ERRO: Falha ao conectar ou criar tabelas no MySQL. Verifique suas credenciais e a conexão. {e}")
    finally:
        if not db.is_closed():
            db.close()

if __name__ == '__main__':
    initialize_db()