# app/models.py
from app import db, login  # Importe 'login' aqui
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import secrets

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(255))
    is_admin = db.Column(db.Boolean, default=False)  # Novo: define se é administrador
    theme = db.Column(db.String(10), default='light')  # Novo: armazena o tema ('light' ou 'dark')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

    def is_administrator(self):  #Função para verificar.
        return self.is_admin

    def set_theme(self, theme): #função para alterar o tema.
        if theme in ['light','dark']:
            self.theme = theme
            return True
        return False

    def get_theme(self): #Função para retornar o tema.
        return self.theme

# Adicione a função user_loader *aqui*, dentro do models.py
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# class User(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(64), unique=True, index=True)
#     password_hash = db.Column(db.String(128))

#     def set_password(self, password):
#         self.password_hash = generate_password_hash(password)

#     def check_password(self, password):
#         return check_password_hash(self.password_hash, password)

#     def __repr__(self):
#         return f'<User {self.username}>'

class War(db.Model):
    # ... (seu modelo War, sem alterações) ...
    war_id = db.Column(db.Text, primary_key=True)
    clan_tag = db.Column(db.Text)
    opponent_tag = db.Column(db.Text)
    preparation_start_time = db.Column(db.Text)
    start_time = db.Column(db.Text)
    end_time = db.Column(db.Text)
    team_size = db.Column(db.Integer)
    result = db.Column(db.Text)
    clan_stars = db.Column(db.Integer)
    opponent_stars = db.Column(db.Integer)
    attacks = db.relationship('WarAttack', backref='war', lazy='dynamic') #adicionado para simplificar

    def __repr__(self):
        return f'<War {self.war_id}>'

class WarAttack(db.Model):
     # ... (seu modelo WarAtack, sem alterações) ...
    id = db.Column(db.Integer, primary_key=True)
    war_id = db.Column(db.Text, db.ForeignKey('war.war_id'))
    player_tag = db.Column(db.Text)
    defender_tag = db.Column(db.Text)
    player_position = db.Column(db.Integer)
    defender_position = db.Column(db.Integer)
    stars = db.Column(db.Integer)
    destruction = db.Column(db.Integer)
    __table_args__ = (
        db.UniqueConstraint('war_id', 'player_tag', 'defender_tag', name='unique_attack'),
    )
    def __repr__(self):
        return f'<WarAttack {self.player_tag} -> {self.defender_tag}>'

class Player(db.Model):
     # ... (seu modelo Player, sem alterações) ...
    player_tag = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text)
    townhall_level = db.Column(db.Integer)
    exp_level = db.Column(db.Integer)
    trophies = db.Column(db.Integer)
    best_trophies = db.Column(db.Integer)
    war_stars = db.Column(db.Integer) #Total de estrelas em guerras.
    donations = db.Column(db.Integer) # Doações na temporada
    donations_received = db.Column(db.Integer) # Recebidos na temporada
    clan_tag = db.Column(db.Text, db.ForeignKey('clan.clan_tag')) #referencia a tabela clan
    def __repr__(self):
        return f'<Player {self.name}>'

class Clan(db.Model):
     # ... (seu modelo Clan, sem alterações) ...
    clan_tag = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text)
    clan_level = db.Column(db.Integer)
    members_data = db.relationship('Player', backref='clan', lazy='dynamic')

    def __repr__(self):
        return f'<Clan {self.name}>'
    
@login.user_loader
def load_user(id):
    return User.query.get(int(id))