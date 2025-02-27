# app/main/routes.py
from flask import render_template, redirect, url_for, flash
from app.main import bp
from flask_login import login_required
from app.models import Clan, Player, War  # Importe os modelos
from sqlalchemy import func, desc
from app.utils import format_war_id, format_date
from app import db

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    # Obtém informações do clã (assumindo que você só tem um clã)
    clan = Clan.query.first()
    #Correção: Obtem o clan_tag
    clan_tag = db.session.query(Clan.clan_tag).scalar()
    if not clan:
        flash("Nenhum clã encontrado. Configure o clã na sua aplicação.", "warning")
        # Considere redirecionar para uma página de configuração do clã
        return render_template('index.html', title='Página Inicial')

    # Obtém os membros do clã
    members = Player.query.filter_by(clan_tag=clan_tag).order_by(Player.name).all()

    # Obtém a última guerra (para exibir detalhes)
    last_war = War.query.order_by(desc(War.end_time)).first()

    # Jogador que mais doou
    top_donator = Player.query.filter_by(clan_tag=clan_tag).order_by(desc(Player.donations)).first()

    # Jogador que menos doou
    least_donator = Player.query.filter_by(clan_tag=clan_tag).order_by(Player.donations).first()

    # Jogador que mais recebeu doações
    top_receiver = Player.query.filter_by(clan_tag=clan_tag).order_by(desc(Player.donations_received)).first()

    # Jogador que menos recebeu doações
    least_receiver = Player.query.filter_by(clan_tag=clan_tag).order_by(Player.donations_received).first()

    return render_template('index.html', title='Página Inicial', clan=clan,
                           members=members, last_war=last_war,
                           top_donator=top_donator, least_donator=least_donator,
                           top_receiver=top_receiver, least_receiver=least_receiver,
                           format_date=format_date, format_war_id=format_war_id) #Passa as funções para formatação