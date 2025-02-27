# app/players/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import Optional, NumberRange

class PlayerSearchForm(FlaskForm):
    name = StringField('Nome', validators=[Optional()])
    tag = StringField('Tag', validators=[Optional()])
    min_townhall = IntegerField('CV Mínimo', validators=[Optional(), NumberRange(min=1)])
    max_townhall = IntegerField('CV Máximo', validators=[Optional(), NumberRange(min=1)])
    min_trophies = IntegerField('Troféus Mínimos', validators=[Optional()])
    max_trophies = IntegerField('Troféus Máximos', validators=[Optional()])
    sort_by = SelectField('Ordenar por', choices=[
        ('name', 'Nome (A-Z)'),
        ('name_desc', 'Nome (Z-A)'),
        ('townhall_level', 'CV (Crescente)'),
        ('townhall_level_desc', 'CV (Decrescente)'),
        ('trophies', 'Troféus (Crescente)'),
        ('trophies_desc', 'Troféus (Decrescente)'),
    ], default='name')
    submit = SubmitField('Buscar')