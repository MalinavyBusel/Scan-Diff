from flask import Flask
from flask import request, render_template

from templates.get_form import GetForm
from logic.image_diff import create_image

app = Flask(__name__, template_folder="templates")
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 16 - 1
app.config['SECRET_KEY'] = 'SECRET_KEY'  # TODO в енв


@app.route('/', methods=('GET', 'POST'))  # TODO версия
def main():
    form = GetForm()

    if form.validate_on_submit():
        base = create_image(form.base_image.data)
        compared = create_image(form.compared_image.data)
        return render_template('result.html')

    return render_template(
        "main_get.jinja2",
        form=form)


if __name__ == "__main__":
    app.run()  # TODO add host and port to env
