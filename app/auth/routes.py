# app/auth/routes.py
from flask import render_template, redirect, url_for, flash, request
from app.auth import bp
from app.auth.forms import LoginForm, CreateUserForm, ChangePasswordForm, ChangeUsernameForm, ChangeProfileForm
from app.models import User
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlparse #Caso a opção acima não funcione.
from app import db


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Usuário ou senha inválidos', 'danger')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)

    return render_template('auth/login.html', title='Login', form=form) #caminho do arquivo alterado

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/create_user', methods=['GET', 'POST'])
@login_required  # Requer login
def create_user():

    if not current_user.is_administrator():
        flash('Você não tem permissão para criar usuários.', 'danger')
        return redirect(url_for('main.index'))

    form = CreateUserForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, is_admin=form.is_admin.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Usuário {form.username.data} criado com sucesso!', 'success')
        return redirect(url_for('main.index'))  # Ou redirecione para onde for apropriado
    return render_template('auth/create_user.html', title='Criar Usuário', form=form) #caminho do arquivo alterado


@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Senha atual incorreta.', 'danger')
            return redirect(url_for('auth.change_password'))

        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash('Sua senha foi alterada.', 'success')
        return redirect(url_for('main.index'))  # Ou para o perfil do usuário

    return render_template('auth/change_password.html', title='Alterar Senha', form=form) #caminho do arquivo alterado


@bp.route('/change_username', methods=['GET', 'POST'])
@login_required
def change_username():
    form = ChangeUsernameForm()
    if form.validate_on_submit():
        #Verifica se o nome de usuário já existe
        existing_user = User.query.filter_by(username=form.new_username.data).first()
        if existing_user:
            flash('Nome já existe', 'danger')
            return redirect(url_for('auth.change_username'))

        current_user.username = form.new_username.data
        db.session.commit()
        flash('Seu nome de usuário foi alterado.', 'success')
        return redirect(url_for('main.index'))
    return render_template('auth/change_username.html', title='Alterar Nome de Usuário', form=form) #caminho do arquivo alterado

@bp.route('/change_profile', methods=['GET', 'POST'])
@login_required
def change_profile():
    form = ChangeProfileForm()
    if form.validate_on_submit():
        #Verifica se a senha atual está correta
        if not current_user.check_password(form.current_password.data):
            flash('Senha atual incorreta.', 'danger')
            return redirect(url_for('auth.change_profile'))

        #Verifica se o nome de usuario já existe.
        existing_user = User.query.filter_by(username=form.new_username.data).first()
        if existing_user and existing_user.id != current_user.id:
            flash('Nome de usuário já existe.', 'danger')
            return redirect(url_for('auth.change_profile'))

        #Atualiza nome
        current_user.username = form.new_username.data

        #Atualiza a senha, se fornecida
        if form.new_password.data:
            current_user.set_password(form.new_password.data)

        db.session.commit()
        flash('Seu perfil foi atualizado com sucesso.', 'success')
        return redirect(url_for('main.index'))

    return render_template('auth/change_profile.html', title='Alterar Perfil', form=form) #caminho do arquivo alterado



@bp.route('/set_theme/<theme>')
@login_required
def set_theme(theme):

    if current_user.set_theme(theme):
        db.session.commit()
        flash(f'Tema alterado para {theme}', 'success')
    else:
        flash('Tema inválido', 'danger')

    return redirect(request.referrer or url_for('main.index')) #retorna para pagina que estava