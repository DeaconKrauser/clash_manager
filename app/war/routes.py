# app/war/routes.py
from flask import render_template, redirect, url_for, flash, request
from app.war import bp
from app.models import War, WarAttack, Player, Clan
from app import db
from app.utils import fetch_war_data, fetch_clan_members, get_opponent_member_position, format_war_id, format_date  # Importe as funções
from flask_login import login_required
from sqlalchemy import desc, func, or_, and_  # Importe func, or_ e and_


@bp.route('/wars')
@login_required
def war_list():
    wars = War.query.order_by(desc(War.end_time)).all()
    # Passa as funções de formatação para o template
    return render_template('war/war_list.html', title='Guerras', wars=wars, format_war_id=format_war_id, format_date=format_date)


@bp.route('/war/<war_id>')
@login_required
def war_detail(war_id):
    war = War.query.get_or_404(war_id)
    attacks = war.attacks.order_by(WarAttack.player_position).all()
    # Passa as funções de formatação para o template
    return render_template('war/war_detail.html', title='Detalhes da Guerra', war=war, attacks=attacks, format_war_id=format_war_id, format_date=format_date)

@bp.route('/current_war')
@login_required
def current_war():
    #... (código da rota /current_war - sem alterações) ...
    war_data = fetch_war_data()
    if not war_data or war_data.get("state") not in ("inWar", "preparation"):
         flash("Não há guerra em andamento ou em preparação no momento.", "info")
         return redirect(url_for('main.index'))  # Ou outra página apropriada

    clan_members = {member['tag']: member for member in war_data.get('clan', {}).get('members', [])}
    opponent_members = {member['tag']: member for member in war_data.get('opponent', {}).get('members', [])}


    attacked = set()
    for member in clan_members.values():
        if 'attacks' in member:
            for attack in member['attacks']:
              attacked.add(attack['defenderTag'])

    not_attacked = [member for tag, member in clan_members.items() if tag not in attacked and 'attacks' not in member]

    return render_template('war/current_war.html', title="Guerra em Andamento",
                           clan_members=clan_members.values(),
                           opponent_members=opponent_members.values(),
                           not_attacked=not_attacked)


@bp.route('/war/<war_id>/stats')
@login_required
def war_stats(war_id):
    war = War.query.get_or_404(war_id)

    # 1. Jogadores que mais performaram (estrelas e destruição)
    top_performers = db.session.query(
        WarAttack.player_tag,
        func.sum(WarAttack.stars).label('total_stars'),
        func.avg(WarAttack.destruction).label('avg_destruction')
    ).filter(WarAttack.war_id == war_id).group_by(WarAttack.player_tag).order_by(desc('total_stars'), desc('avg_destruction')).limit(10).all()


    # 2. Contagem de estrelas (3, 2, 1, 0)
    star_counts = db.session.query(
        WarAttack.stars,
        func.count(WarAttack.stars).label('count')
    ).filter(WarAttack.war_id == war_id).group_by(WarAttack.stars).order_by(WarAttack.stars.desc()).all()


    # 3. Jogadores que atacaram fora do espelho (e não ganharam nenhuma estrela)
    off_mirror_attackers = db.session.query(
        WarAttack.player_tag
    ).filter(
        WarAttack.war_id == war_id,
        WarAttack.stars == 0,
        func.abs(WarAttack.player_position - WarAttack.defender_position) > 3  # Correção: usar func.abs()
    ).distinct().all()

    # Preparar dados para os gráficos (exemplo usando listas)
    performers_labels = [p.player_tag for p in top_performers]
    performers_stars = [p.total_stars for p in top_performers]
    performers_destruction = [p.avg_destruction for p in top_performers]

    stars_labels = [f"{s.stars} Estrelas" for s in star_counts]
    stars_values = [s.count for s in star_counts]

    # PASSE AS FUNÇÕES format_war_id e format_date AQUI:
    return render_template('war/war_stats.html', title='Estatísticas da Guerra', war=war,
                           top_performers=top_performers, star_counts=star_counts,
                           off_mirror_attackers=off_mirror_attackers,
                           performers_labels=performers_labels, performers_stars=performers_stars,
                           performers_destruction=performers_destruction,
                           stars_labels=stars_labels, stars_values=stars_values,
                           format_war_id=format_war_id, format_date=format_date)  # Adicionado!