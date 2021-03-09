from flask import Flask, render_template

from data import db_session
from data.users import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

# def main():
#     db_session.global_init("db/main.db")


@app.route("/")
def index():
    return render_template("common/main_page.html")


if __name__ == '__main__':
    #main()
    app.run(port=6655)
