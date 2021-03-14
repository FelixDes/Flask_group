import json

from flask import Flask, render_template, redirect

from Forms.user import RegisterForm
from data import db_session
from data.users import User

# ДЛЯ КОНСТАНТ
path_json = "Res_json/str.json"

# Список текущих ключей json
# Если добавляешь что-то в json - дублируешь сюда
#
# logo_txt - текст логотипа - class header_logo
# title_main - название мейн страницы
# title_registration - название страницы регистрации
# title_login - название страницы логина
# text_about -
# text_about_our_work - список услуг - class services_list
# how_to_find_us - то, что будет перед картой - class потом добавлю
# how_to_contact_us - список контактов - class потом добавлю
# footer - то, что будет отображаться в футере сайта

app = Flask(__name__)
app.config[
    'SECRET_KEY'] = "_ti{qxjXpNadwPPGaOh{zBawz^GBBpoIU|qpGpEVzgRzqhqeZ]hv_oeBhb|WBkmdRANtw}akIfMgOLm{r]ZnYiZcBFXZz{'"

json_dict = {}


def parse_all(json_path):
    try:
        with open(json_path, "r") as file:
            json_dict = json.load(file)
        return json_dict
    except FileNotFoundError:
        print("Файл не существует")
        return "Файл не существует"
    except TypeError:
        print("Сегодня мы принимаем только строки")
        return "Сегодня мы принимаем только строки"
    except OSError:
        print("Что-то пошло не так")
        return "Что-то пошло не так"


def get_value(json_path, key):
    try:
        with open(json_path, "r") as file:
            json_dict = json.load(file)
        return json_dict.getValue(str(key))
    except FileNotFoundError:
        print("Файл не существует")
        return "Файл не существует"
    except TypeError:
        print("Сегодня мы принимаем только строки, и иногда int, но только как ключ")
        return "Сегодня мы принимаем только строки, и иногда int, но только как ключ"
    except OSError:
        print("Что-то пошло не так")
        return "Что-то пошло не так"


def main():
    global json_dict
    json_dict = parse_all(path_json)
    db_session.global_init("db/main.db")


@app.route("/")
def index():
    return render_template("common/main_page.html", interesting_information='текст ' * 150,
                           information_list=['что-то интересное'] * 5)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('common/register_page.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('common/register_page.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('common/register_page.html', title='Регистрация', form=form)


if __name__ == '__main__':
    main()
    app.run(port=6655)
