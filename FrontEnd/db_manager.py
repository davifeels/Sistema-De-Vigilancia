from peewee import *
import datetime
import os
import mysql.connector
from mysql.connector.errors import OperationalError 

# Configurações do banco de dados MySQL (exatamente como o seu)
db = MySQLDatabase(
    database='phoenix_vision_db',
    user='root',
    password='davi080401',  # <-- Sua senha
    host='localhost',
    port=3306,
)

# --- MODELO BASE ---
class BaseModel(Model):
    class Meta:
        database = db

# --- TABELA DE EVENTOS (LOGS) - JÁ EXISTIA ---
class Event(BaseModel):
    event_type = CharField()
    camera_name = CharField()
    timestamp = DateTimeField(default=datetime.datetime.now)
    image_path = CharField(null=True)
    video_path = CharField(null=True)

    class Meta:
        db_table = 'events'

# --- (NOVO) TABELA DE PESSOAS (PERFIS) ---
class Pessoa(BaseModel):
    nome = CharField(unique=True) # Nome da pessoa (ex: "Davi Anderson")
    origem = CharField(null=True) # (ex: "Distrito Federal", "Minas Gerais")
    foto_path = CharField(null=True) # Caminho para a foto de perfil (ex: "rostos_conhecidos/Davi.png")

    class Meta:
        db_table = 'pessoas'

# --- (NOVO) TABELA DE BIOMETRIA (ROSTOS) ---
class Biometria(BaseModel):
    pessoa = ForeignKeyField(Pessoa, backref='biometrias', on_delete='CASCADE')
    # Usamos BlobField para armazenar os bytes puros do encoding facial
    # (É muito mais eficiente que guardar um texto gigante)
    encoding = BlobField() 

    class Meta:
        db_table = 'biometrias'

# --- (NOVO) TABELA DE REGISTROS (BASE CIVIL/CRIMINAL) ---
class Registro(BaseModel):
    pessoa = ForeignKeyField(Pessoa, backref='registros', on_delete='CASCADE')
    tipo_base = CharField() # (ex: "Civil", "Criminal", "Alerta")
    descricao = TextField() # (ex: "Mandado de prisão em aberto", "Pessoa desaparecida")
    data_registro = DateTimeField(default=datetime.datetime.now)

    class Meta:
        db_table = 'registros'


# --- FUNÇÃO DE INICIALIZAÇÃO ATUALIZADA ---
def initialize_db():
    try:
        db.connect(reuse_if_open=True)
        # ATUALIZADO: Manda o Peewee criar TODAS as tabelas
        db.create_tables([Event, Pessoa, Biometria, Registro])
        print("Tabelas (events, pessoas, biometrias, registros) verificadas/criadas com sucesso.")
    except OperationalError as e:
        print(f"ERRO: Falha ao conectar ou criar tabelas no MySQL. Verifique suas credenciais e a conexão. {e}")
    finally:
        if not db.is_closed():
            db.close()

if __name__ == '__main__':
    initialize_db()