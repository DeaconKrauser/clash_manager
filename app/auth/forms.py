# app/auth/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from app.models import User  # Importe o modelo User


class LoginForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember_me = BooleanField('Lembrar de mim')
    submit = SubmitField('Entrar')


class CreateUserForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        'Confirmar Senha', validators=[DataRequired(), EqualTo('password')]
    )
    is_admin = BooleanField('Administrador?')  # Campo para definir se é admin
    submit = SubmitField('Criar Usuário')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Nome de usuário já existe. Escolha outro.')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Senha Atual', validators=[DataRequired()])
    new_password = PasswordField('Nova Senha', validators=[DataRequired(), Length(min=6)])
    confirm_new_password = PasswordField(
        'Confirmar Nova Senha', validators=[DataRequired(), EqualTo('new_password')]
    )
    submit = SubmitField('Alterar Senha')

class ChangeUsernameForm(FlaskForm): #Adicionado
    new_username = StringField('Novo Nome de Usuário', validators=[DataRequired(), Length(min=4, max=20)])
    submit = SubmitField('Alterar Nome')

    def validate_username(self, username): #Adicionado
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Nome de usuário já existe. Escolha outro.')

class ChangeProfileForm(FlaskForm): #Adicionado para simplificar
    new_username = StringField('Novo Nome de Usuário', validators=[DataRequired(), Length(min=4, max=20)])
    current_password = PasswordField('Senha Atual', validators=[DataRequired()])
    new_password = PasswordField('Nova Senha', validators=[Length(min=6)])  # Opcional
    confirm_new_password = PasswordField('Confirmar Nova Senha', validators=[EqualTo('new_password')])
    submit = SubmitField('Alterar Perfil')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Nome de usuário já existe. Escolha outro.')