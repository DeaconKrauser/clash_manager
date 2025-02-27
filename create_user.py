# create_user.py
from app import create_app, db
from app.models import User
import getpass
import sys

app = create_app()

def create_user(username, password):
    with app.app_context():  # Cria um contexto de aplicação
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f"Usuário '{username}' criado com sucesso!")

if __name__ == '__main__':
    if len(sys.argv) > 1: #Verifica se foi passado um nome por parametro.
        username = sys.argv[1]
    else:
        username = input("Digite o nome de usuário: ")
    password = getpass.getpass("Digite a senha: ")  # Usa getpass para ocultar a senha
    create_user(username, password)