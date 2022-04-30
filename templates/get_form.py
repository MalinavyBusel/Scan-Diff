from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField


class GetForm(FlaskForm):
    base_image = FileField(
        'Base Image',
        validators=[
            FileRequired(),
            FileAllowed(['jpg', 'png'],
                        'Not a valid file extension.')
        ]
    )
    compared_image = FileField(
        'Compared Image',
        validators=[
            FileRequired(),
            FileAllowed(['jpg', 'png'],
                        'Not a valid file extension.')
        ]
    )
    submit = SubmitField('Submit')
