from flask import Flask
from flask import request, render_template
from os import path

from templates.get_form import ImageForm
from logic.image_diff import create_image, process_diff, create_tempfile
from logic.config import settings

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 16 - 1
app.config['SECRET_KEY'] = settings['SECRET_KEY']


@app.route('/', methods=('GET', 'POST'))  # TODO версия
def main():
    form = ImageForm()

    if form.validate_on_submit():
        base_f = create_tempfile(form.base_image.data)
        compared_f = create_tempfile(form.compared_image.data)

        # base = create_image(base_f)
        # compared = create_image(compared_f)
        # result_pic = process_diff(base, compared)

        pic1 = path.join('static', 'scan1.PNG')
        pic2 = path.join('static', 'scan2.PNG')

        return render_template(
            "main_post.jinja2",
            form=form,
            img1=pic1, img2=pic2)

    return render_template(
        "main_get.jinja2",
        form=form)


if __name__ == "__main__":
    app.run(host=settings['HOST'],
            port=settings['PORT'])
