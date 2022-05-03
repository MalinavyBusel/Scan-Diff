from concurrent.futures import ProcessPoolExecutor
from flask import Flask
from flask import request, render_template
from flask_bootstrap import Bootstrap
from os import path
from cv2 import imwrite

from templates.get_form import ImageForm
from logic.image_diff import create_image, process_diff
from logic.config import settings

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 16 - 1
app.config['SECRET_KEY'] = settings.SECRET_KEY

executor = ProcessPoolExecutor(max_workers=4)


@app.route('/', methods=('GET', 'POST'))
def main():
    form = ImageForm()

    if form.validate_on_submit():
        base_data = form.base_image.data
        compared_data = form.compared_image.data

        base = create_image(base_data)
        compared = create_image(compared_data)
        pool_process = executor.submit(process_diff, base, compared)
        res_1, res_2 = pool_process.result()

        path1 = path.join('static', base_data.filename)
        imwrite(path1, res_1)
        path2 = path.join('static', compared_data.filename)
        imwrite(path2, res_2)

        return render_template(
            "main_post.jinja2",
            form=form,
            img1=path1, img2=path2)

    return render_template(
        "main_get.jinja2",
        form=form)


if __name__ == "__main__":
    app.run(host=settings.HOST,
            port=settings.PORT,
            debug=settings.DEBUG)
