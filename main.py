import json

from flask import Flask, render_template, redirect
from flask_login import LoginManager
from flask_socketio import SocketIO, send
from werkzeug.security import check_password_hash

# ДЛЯ КОНСТАНТ
path_json = "Res_json/str.json"
path_sever_json = "Res_json/server.json"

# Список текущих ключей json
# Если добавляем что-то в json - дублируем сюда
#
# logo_txt - текст логотипа - class header_logo
# title_main - название мейн страницы
# title_registration - название страницы регистрации
# title_login - название страницы логина
# text_about - о нас - about
# text_about_our_work - список услуг - class services_list
# how_to_find_us - то, что будет перед картой - class потом добавлю
# chat_btn_text - текст для кнопки чата - bottom_chat_button
# how_to_contact_us - список контактов - class потом добавлю
# footer - то, что будет отображаться в футере сайта

app = Flask(__name__)
app.config[
    'SECRET_KEY'] = "_ti{qxjXpNadwPPGaOh{zBawz^GBBpoIU|qpGpEVzgRzqhqeZ]hv_oeBhb|WBkmdRANtw}akIfMgOLm{r]ZnYiZcBFXZz{'"

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

c_user = None

server_dict = {}

from Forms.user import RegisterForm, LoginForm
from data import db_session
from data.messages import Message
from data.users import User


def parse_all(json_path):
    try:
        with open(json_path, "r", encoding='utf-8') as file:
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
        with open(json_path, "r", encoding='utf-8') as file:
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


inf_dict = parse_all(path_json)


def server_start_data_read(path_sever_json):
    global server_dict
    with open(path_sever_json) as file:
        data = json.load(file)
    for key, value in data.items():
        server_dict.update({key: value})


def main(path_json_get="Res_json/str.json", path_sever_json_get="Res_json/server.json"):
    global json_dict, path_json, path_sever_json
    path_json = path_json_get
    path_sever_json = path_sever_json_get
    json_dict = parse_all(path_json)
    db_session.global_init("db/main.db")
    server_start_data_read(path_sever_json)
    socketio.run(app, port=server_dict.get('port'))
    #app.run(port=server_dict.get('port'))


@app.route("/")
def index():
    return render_template("common/main_page.html", interesting_information=inf_dict['text_about'],
                           information_list=inf_dict['text_about_our_work'],
                           logo_txt=inf_dict['logo_txt'], chat_btn_text=inf_dict['chat_btn_text'],
                           connection_list=inf_dict['how_to_contact_us'], how_to_find_us=inf_dict['how_to_find_us'],
                           footer_inf=inf_dict['footer'])


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('common/register_page.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('common/register_page.html', title='Регистрация',
                                   footer_inf=inf_dict['footer'],
                                   logo_txt=inf_dict['logo_txt'], chat_btn_text=inf_dict['chat_btn_text'], form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('common/register_page.html', title='Регистрация', footer_inf=inf_dict['footer'],
                           logo_txt=inf_dict['logo_txt'], chat_btn_text=inf_dict['chat_btn_text'], form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    global c_user  # Это очень криво сделанный текущий пользователь; Teamlead: ладно
    form = LoginForm()
    if form.email.data and form.password.data:  # Костыль
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if not user:
            return render_template('common/login_page.html', title='Вход', form=form,
                                   message="Такого пользователя не обнаружено")
        elif not check_password_hash(user.hashed_password, form.password.data):
            return render_template('common/login_page.html', title='Вход', form=form,
                                   message="Неверный пароль")
        else:
            c_user = user
            print(type(c_user), c_user)
            return redirect('/')
    return render_template('common/login_page.html', title='Вход', logo_txt=inf_dict['logo_txt'], form=form,
                           footer_inf=inf_dict['footer'], chat_btn_text=inf_dict['chat_btn_text'],
                           message='')


@app.route('/chat', methods=['GET', 'POST'])
def chat(reboot_arg=False, res_json=""):
    if reboot_arg:
        return res_json
    username = None
    if c_user is None:
        return redirect("/login")
    else:
        return render_template('common/chat_page.html', username=username)


@socketio.on('message')
def handleMessage(data):
    db_sess = db_session.create_session()
    print(f"Message: {data}")
    send(data, broadcast=True)
    message = Message(text=data['msg'])
    print(message)
    db_sess.add(message)
    db_sess.commit()

    messages = db_sess.query(Message).filter(Message.user == c_user)
    # print(messages)
    # res_dct = messages.to_dict()
    # res_json = json.dumps(res_dct)
    # print(res_json)
    # #chat(reboot_arg=True, res_json=res_json)


if __name__ == '__main__':
    main(path_json, path_sever_json)
