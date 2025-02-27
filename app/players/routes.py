# app/players/routes.py
from flask import render_template, redirect, url_for, flash, request
from app.players import bp
from app.models import Player, Clan
from flask_login import login_required
from app import db
from app.utils import fetch_player_data
from app.players.forms import PlayerSearchForm  # Importe o formulário
from sqlalchemy import or_, and_ #Import para usar condições OR e AND.


@bp.route('/players', methods=['GET', 'POST'])  # Aceita GET e POST
@login_required
def players():
    form = PlayerSearchForm()
    clan_tag = db.session.query(Clan.clan_tag).scalar()

    if form.validate_on_submit():  # Se o formulário foi submetido
        # Construir a consulta dinamicamente
        query = Player.query.filter_by(clan_tag=clan_tag)

        if form.name.data:
            # Usar ilike para busca case-insensitive e com curingas
            query = query.filter(Player.name.ilike(f'%{form.name.data}%'))
        if form.tag.data:
            query = query.filter(Player.player_tag.ilike(f'%{form.tag.data}%'))  # Busca exata (case-insensitive)
        if form.min_townhall.data:
            query = query.filter(Player.townhall_level >= form.min_townhall.data)
        if form.max_townhall.data:
            query = query.filter(Player.townhall_level <= form.max_townhall.data)
        if form.min_trophies.data:
            query = query.filter(Player.trophies >= form.min_trophies.data)
        if form.max_trophies.data:
            query = query.filter(Player.trophies <= form.max_trophies.data)

        # Ordenação
        if form.sort_by.data == 'name':
            query = query.order_by(Player.name)
        elif form.sort_by.data == 'name_desc':
            query = query.order_by(Player.name.desc())
        elif form.sort_by.data == 'townhall_level':
            query = query.order_by(Player.townhall_level)
        elif form.sort_by.data == 'townhall_level_desc':
            query = query.order_by(Player.townhall_level.desc())
        elif form.sort_by.data == 'trophies':
            query = query.order_by(Player.trophies)
        elif form.sort_by.data == 'trophies_desc':
            query = query.order_by(Player.trophies.desc())

        players_data = query.all()  # Executa a consulta
        return render_template('players/players.html', title='Jogadores', players=players_data, form=form) # Passa o formulário

    # Se o formulário não foi submetido (primeira vez que a página é carregada)
    # ou se a validação falhar, mostra todos os jogadores.
    players_data = Player.query.filter_by(clan_tag=clan_tag).order_by(Player.name).all()
    return render_template('players/players.html', title='Jogadores', players=players_data, form=form) # Passa o formulário

@bp.route('/player/<player_tag>')
@login_required
def player(player_tag):
        #... (código da rota /player/<player_tag> - não mudou) ...
        player_data = Player.query.filter_by(player_tag=player_tag).first()
        if not player_data:
             # Busca da API
            player_api_data = fetch_player_data(player_tag)
            if player_api_data:
                # Cria um novo jogador com os dados da API
                player_data = Player(
                    player_tag=player_api_data['tag'],
                    name=player_api_data['name'],
                    townhall_level=player_api_data['townHallLevel'],
                    exp_level=player_api_data['expLevel'],
                    trophies=player_api_data['trophies'],
                    best_trophies=player_api_data['bestTrophies'],
                    war_stars=player_api_data['warStars'],
                    donations=player_api_data.get('donations', 0),
                    donations_received=player_api_data.get('donationsReceived', 0),
                    #clan_tag= player_api_data['clan']['tag'] #Verifica se o player esta em um clan.
                )
                # Adicione e commit as mudanças
                db.session.add(player_data)
                db.session.commit()
                flash(f"Jogador {player_data.name} adicionado com sucesso.", "success") #Mensagem de sucesso
            else:
                flash('Jogador não encontrado.', 'error')
                return redirect(url_for('players.players'))

        return render_template('players/player.html', title='Detalhes do Jogador', player=player_data)