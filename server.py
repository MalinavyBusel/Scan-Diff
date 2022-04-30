import tempfile

from flask import Flask
from flask import request, render_template

from templates.get_form import GetForm


app = Flask(__name__, template_folder="templates")
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png']
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 16 - 1


@app.route('/', methods=['GET', 'POST'])  # TODO версия
def main():
    form = GetForm()

    if form.validate_on_submit():
        pass
        base = request.files['base_image']
        compared = request.files['compared_image']
        return render_template('some_template')

    return render_template(
        "main_get.jinja2",
        form=form,
        template="form-template")


if __name__ == "__main__":
    app.run()  # TODO add host and port to env
