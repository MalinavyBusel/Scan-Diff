from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField, SelectField


class ImageForm(FlaskForm):
    base_image = FileField(
        'Base Image',
        validators=[
            FileRequired(),
            FileAllowed(['jpg', 'png', 'jpeg'],
                        'Not a valid file extension.')
        ]
    )
    compared_image = FileField(
        'Compared Image',
        validators=[
            FileRequired(),
            FileAllowed(['jpg', 'png', 'jpeg'],
                        'Not a valid file extension.')
        ]
    )
    language = SelectField(u'Document Language',
                           choices=[('eng', 'eng'), ('rus', 'rus')])
    submit = SubmitField('Submit')
