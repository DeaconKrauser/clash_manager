# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Carrega variáveis de ambiente do arquivo .env

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'uma-chave-secreta-muito-forte'  # Chave secreta para Flask (segurança)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://user:password@host:port/database'  # URL do banco de dados
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    API_KEY = os.environ.get("API_KEY")
    CLAN_TAG = os.environ.get("CLAN_TAG")
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true' #habilita debug