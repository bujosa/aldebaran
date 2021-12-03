from flask_wtf.form import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.simple import PasswordField
from wtforms.validators import DataRequired

class FormMeli(FlaskForm):
    secret = PasswordField("Secret", validators=[DataRequired()])
    days = StringField("Days", validators=[DataRequired()])
    submit = SubmitField('Submit')