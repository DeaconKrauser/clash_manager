# app/utils.py
import requests
from app import db
from app.models import War, WarAttack, Player, Clan
from config import Config
from datetime import datetime, timedelta, timezone  # Importe timedelta e timezone


def fetch_war_data():
    # ... (sua função fetch_war_data - sem alterações) ...
    """Busca os dados da guerra atual na API do Clash of Clans."""
    url = f"https://api.clashofclans.com/v1/clans/%23{Config.CLAN_TAG.replace('#', '')}/currentwar"
    headers = {"Authorization": f"Bearer {Config.API_KEY}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro ao buscar dados da API: {response.status_code} - {response.text}")
        return None

def fetch_clan_members():
     # ... (sua função fetch_clan_members - sem alterações) ...
    """Busca a lista de membros do clã."""
    url = f"https://api.clashofclans.com/v1/clans/%23{Config.CLAN_TAG.replace('#', '')}/members"
    headers = {"Authorization": f"Bearer {Config.API_KEY}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("items", [])
    else:
        print(f"Erro ao buscar membros do clã: {response.status_code} - {response.text}")
        return []

def fetch_clan_data():
    # ... (sua função fetch_clan_data - sem alterações) ...
    """Busca dados do clã."""
    url = f"https://api.clashofclans.com/v1/clans/%23{Config.CLAN_TAG.replace('#', '')}"
    headers = {"Authorization": f"Bearer {Config.API_KEY}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro ao buscar dados do clã: {response.status_code} - {response.text}")
        return None

def fetch_player_data(player_tag):
    # ... (sua função fetch_player_data - sem alterações)...
    """Busca dados de um jogador específico."""
    url = f"https://api.clashofclans.com/v1/players/%23{player_tag.replace('#', '')}"
    headers = {"Authorization": f"Bearer {Config.API_KEY}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro ao buscar dados do jogador: {response.status_code} - {response.text}")
        return None
def get_opponent_member_position(war_data, defender_tag):
     # ... (sua função  get_opponent_member_position - sem alterações)...
    opponent_clan = war_data.get("opponent", {})
    if not opponent_clan:
        return None

    for member in opponent_clan.get("members", []):
        if member["tag"] == defender_tag:
            return member["mapPosition"]
    return None

def save_war_to_db():
      # ... (sua função  save_war_to_db - sem alterações)...
    """Função principal para processar e salvar dados da guerra."""
    war_data = fetch_war_data()
    if not war_data:
        return

    if war_data.get("state") == "warEnded":
        war_id = f"{war_data.get('clan', {}).get('tag', 'clanTag')}-{war_data.get('preparationStartTime')}"

        # Verifica se a guerra já existe no banco de dados
        existing_war = War.query.get(war_id)
        if existing_war:
            print(f"Guerra {war_id} já existe no banco de dados.  Não inserindo novamente.")
            return

        # Salva informações da guerra
        clan_tag = war_data.get("clan", {}).get("tag")
        opponent_tag = war_data.get("opponent", {}).get("tag")
        preparation_start_time = war_data.get("preparationStartTime")
        start_time = war_data.get("startTime")
        end_time = war_data.get("endTime")
        team_size = war_data.get("teamSize")
        clan_stars = war_data.get("clan", {}).get("stars")
        opponent_stars = war_data.get("opponent", {}).get("stars")

        result = None
        if clan_stars is not None and opponent_stars is not None:
            if clan_stars > opponent_stars:
                result = "victory"
            elif clan_stars < opponent_stars:
                result = "defeat"
            else:
                result = "tie"
        # Salva a guerra
        war = War(
            war_id=war_id,
            clan_tag=clan_tag,
            opponent_tag=opponent_tag,
            preparation_start_time=preparation_start_time,
            start_time=start_time,
            end_time=end_time,
            team_size=team_size,
            result=result,
            clan_stars=clan_stars,
            opponent_stars=opponent_stars
        )
        db.session.add(war)

        # Salva os ataques da guerra
        clan_members = war_data.get("clan", {}).get("members", [])
        for member in clan_members:
            player_tag = member["tag"]
            player_pos = member["mapPosition"]
            if "attacks" in member:  # Verifica se o membro tem ataques
                for attack in member["attacks"]:
                    defender_tag = attack["defenderTag"]
                    defender_pos = get_opponent_member_position(war_data, defender_tag)
                    if defender_pos is not None:
                        war_attack = WarAttack(
                            war_id=war_id,
                            player_tag=player_tag,
                            defender_tag=defender_tag,
                            player_position=player_pos,
                            defender_position=defender_pos,
                            stars=attack["stars"],
                            destruction=attack["destructionPercentage"]
                        )
                        db.session.add(war_attack)
        db.session.commit()
        print(f"Dados da guerra {war_id} salvos com sucesso.")

def update_clan_members():
     # ... (sua função update_clan_members - sem alterações) ...
    """Atualiza a lista de membros do clã no banco de dados."""
    clan_data = fetch_clan_data()
    if not clan_data:
        return
    clan_tag = clan_data.get("tag")

    #Verifica se o clan existe, se não existir crie.
    clan = Clan.query.get(clan_tag)
    if not clan:
        clan = Clan(clan_tag=clan_tag, name=clan_data.get("name"), clan_level=clan_data.get("clanLevel"))
        db.session.add(clan)
        db.session.commit()
        print(f"Clã '{clan_data.get('name')}' adicionado ao banco de dados.")

    # 1. Obter membros atuais do clã da API
    current_members_api = {member['tag']: member for member in fetch_clan_members()}

    # 2. Obter membros atuais do clã do banco de dados
    current_members_db = {player.player_tag: player for player in Player.query.filter_by(clan_tag=clan_tag).all()}

    # 3. Adicionar novos membros
    for tag, member in current_members_api.items():
        if tag not in current_members_db:
            player = Player(player_tag=tag,
                            name=member['name'],
                            townhall_level=member.get('townHallLevel', 0), # Trata caso a informação não exista
                            exp_level=member.get('expLevel', 0), # Trata caso a informação não exista.
                            trophies=member.get('trophies', 0), # Trata caso a informação não exista.
                            best_trophies=member.get('bestTrophies', 0), # Trata caso a informação não exista.
                            war_stars=member.get('warStars', 0),  # Trata caso a informação não exista.
                            donations=member.get('donations', 0),
                            donations_received=member.get('donationsReceived', 0),
                            clan_tag = clan_tag)
            db.session.add(player)
            print(f"Novo membro adicionado: {member['name']} ({tag})")

    # 4. Remover membros que saíram (opcional - você pode querer manter um histórico)
    for tag, member in current_members_db.items():
        if tag not in current_members_api:
            db.session.delete(member)  # Ou, em vez de deletar, você pode adicionar uma coluna 'active'
            print(f"Membro removido: {member.name} ({tag})")

    db.session.commit()
    print("Lista de membros do clã atualizada.")

def update_player_data(player_tag):
    # ... (sua função update_player_data - sem alterações) ...
    """Atualiza os dados de um jogador específico no banco de dados."""
    player_data = fetch_player_data(player_tag)
    if not player_data:
        return

    player = Player.query.get(player_tag)
    if player:
        # Atualiza os dados existentes
        player.name = player_data['name']
        player.townhall_level = player_data['townHallLevel']
        player.exp_level = player_data['expLevel']
        player.trophies = player_data['trophies']
        player.best_trophies = player_data['bestTrophies']
        player.war_stars = player_data['warStars']
        player.donations = player_data.get('donations', 0)  # Trata caso a informação não exista
        player.donations_received = player_data.get('donationsReceived', 0)  # Trata caso a informação não exista
        #player.clan_tag = player_data.get('clan',{}).get('tag')  # Atualiza o clan tag, caso o jogador tenha mudado

        db.session.commit()
        print(f"Dados do jogador {player_data['name']} ({player_tag}) atualizados.")
    else:
        # Se o jogador não existir, você pode optar por criar um novo registro ou não
        print(f"Jogador {player_tag} não encontrado no banco de dados.")
        # Para criar um novo:
        # new_player = Player(...)
        # db.session.add(new_player)
        # db.session.commit()

def update_all_player_data():
     # ... (sua função update_all_player_data - sem alterações) ...
    """
    Função para atualizar os dados de todos jogadores do clã.
    """
    clan_members = fetch_clan_members()  # Busca a lista de membros do clã da API
    if clan_members:
        for member in clan_members:
            update_player_data(member['tag'])  # Atualiza os dados de cada membro

def format_war_id(war_id):
    """Formata o ID da guerra para exibição."""
    try:
        clan_tag, date_str = war_id.split('-')
        date_obj = datetime.strptime(date_str, "%Y%m%dT%H%M%S.%fZ")
        formatted_date = date_obj.strftime("%d/%m/%Y")
        return f"{clan_tag} - {formatted_date}"
    except ValueError:
        return war_id  # Retorna o ID original se houver erro na formatação

def format_date(date_str):
    """Formata a data e hora para o fuso horário de Brasília."""
    try:
        date_obj = datetime.strptime(date_str, "%Y%m%dT%H%M%S.%fZ")
        date_obj = date_obj.replace(tzinfo=timezone.utc)  # Define o fuso horário como UTC
        brasilia_tz = timezone(timedelta(hours=-3))  # Fuso horário de Brasília (UTC-3)
        date_obj_brasilia = date_obj.astimezone(brasilia_tz)  # Converte para Brasília
        return date_obj_brasilia.strftime("%d/%m/%Y %H:%M:%S")
    except ValueError:
        return date_str  # Retorna a string original se houver erro na formatação