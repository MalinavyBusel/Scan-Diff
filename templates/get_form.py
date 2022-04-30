from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
from wtforms.validators import Length


class GetForm(FlaskForm):
    base_image = FileField(
        'Base Image',
        [
            FileRequired(),
            FileAllowed(['.jpg', '.png'],
                        message='Not a valid file extension.')
        ]
    )
    compared_image = FileField(
        'Compared Image',
        [
            FileRequired(),
            FileAllowed(['.jpg', '.png'],
                        message='Not a valid file extension.')
        ]
    )
    submit = SubmitField('Submit')
