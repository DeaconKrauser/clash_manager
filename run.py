# run.py
from app import create_app
from app.utils import save_war_to_db, update_clan_members, update_all_player_data
# Removido: import schedule, time, threading  (não vamos usar agendamento agora)
from flask import Flask
from config import Config #Import para usar variavel de ambiente.

app = create_app()

# Removido: def run_scheduled_tasks() e o bloco if __name__ == '__main__' original

if __name__ == '__main__':
    # Executa as funções de coleta de dados *imediatamente* (dentro de um contexto de aplicação)
    with app.app_context():
        save_war_to_db()
        update_clan_members()
        update_all_player_data()

    # Inicia a aplicação Flask
    app.run(debug=Config.DEBUG, host='0.0.0.0', use_reloader=False)