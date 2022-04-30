from flask import Flask
from flask import request, render_template


@app.route('/', methods=['GET', 'POST'])
def main():
    # handle the POST request
    if request.method == 'POST':

        pass

    # otherwise handle the GET request
    pass


if __name__ == "__main__":
    app.run()  # TODO add host and port to env
