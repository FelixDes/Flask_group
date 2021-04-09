import json

from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask_socketio import SocketIO, send
from werkzeug.security import check_password_hash

from Forms.user import RegisterForm, LoginForm
from data import db_session
from data.messages import Message
from data.users import User

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
login_manager = LoginManager()
login_manager.init_app(app)
app.config[
    'SECRET_KEY'] = "_ti{qxjXpNadwPPGaOh{zBawz^GBBpoIU|qpGpEVzgRzqhqeZ]hv_oeBhb|WBkmdRANtw}akIfMgOLm{r]ZnYiZcBFXZz{'"

socketio = SocketIO(app, cors_allowed_origins="*")

c_user = None

server_dict = {}


def parse_all(json_path):  # Ф-ция парсинга json-а
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
path_intro_image = "/static/assets/intro.jfif"


def server_start_data_read(path_sever_json):
    global server_dict
    with open(path_sever_json) as file:
        data = json.load(file)
    for key, value in data.items():
        server_dict.update({key: value})


def main(path_json_get="Res_json/str.json", path_sever_json_get="Res_json/server.json",
         path_intro_image_get="static/assets/intro.jfif"):
    global json_dict, path_json, path_sever_json, path_intro_image
    path_json = path_json_get
    path_sever_json = path_sever_json_get
    path_intro_image = path_intro_image_get
    json_dict = parse_all(path_json)
    db_session.global_init("db/main.db")
    server_start_data_read(path_sever_json)
    socketio.run(app, port=server_dict.get('port'))


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/")
def index():
    return render_template("common/main_page.html", title=inf_dict['title_main'],
                           interesting_information=inf_dict['text_about'],
                           information_list=inf_dict['text_about_our_work'],
                           logo_txt=inf_dict['logo_txt'], chat_btn_text=inf_dict['chat_btn_text'],
                           connection_list=inf_dict['how_to_contact_us'], how_to_find_us=inf_dict['how_to_find_us'],
                           footer_inf=inf_dict['footer'], intro_image=path_intro_image,
                           anonymous=str(current_user).split('>')[0] == '<User', c_user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('common/register_page.html', title=inf_dict['title_registration'], form=form,
                                   footer_inf=inf_dict['footer'], logo_txt=inf_dict['logo_txt'],
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('common/register_page.html', title=inf_dict['title_registration'],
                                   footer_inf=inf_dict['footer'],
                                   logo_txt=inf_dict['logo_txt'], chat_btn_text=inf_dict['chat_btn_text'], form=form,
                                   message="Такой пользователь уже есть")
        user = User(  # Создание нового пользователя
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')  # Переадресация на страницу входа
    return render_template('common/register_page.html', title=inf_dict['title_registration'],
                           logo_txt=inf_dict['logo_txt'],
                           footer_inf=inf_dict['footer'],
                           chat_btn_text=inf_dict['chat_btn_text'], form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.email.data and form.password.data:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if not user:
            return render_template('common/login_page.html', title=inf_dict['title_login'],
                                   logo_txt=inf_dict['logo_txt'], form=form,
                                   message="Такого пользователя не обнаружено")  # Если пользователь отсутствует в базе данных
        elif not check_password_hash(user.hashed_password, form.password.data):
            return render_template('common/login_page.html', logo_txt=inf_dict['logo_txt'],
                                   title=inf_dict['title_login'], form=form,
                                   message="Неверный пароль")
        else:
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
    return render_template('common/login_page.html', title=inf_dict['title_login'], logo_txt=inf_dict['logo_txt'],
                           form=form,
                           footer_inf=inf_dict['footer'], chat_btn_text=inf_dict['chat_btn_text'],
                           message='')


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    db_sess = db_session.create_session()
    messages = db_sess.query(Message).filter()
    messages_dict = {'messages': {i.id: {'name': i.user_name, 'text': i.text,
                                         'created_date': i.created_date.strftime("%H:%M:%S")} for i in messages}}
    # json_data = messages_dict
    # with open('Res_json/messages.json', 'w') as file:
    #     json.dump(json_data, file)
    # res_json = json.dumps(json_data)

    message_lst = [f"<strong>{i.user_name}:</strong> {i.text} <sub>{i.created_date.strftime('%H:%M:%S')}</sub>" for i in
                   messages]

    print(message_lst)

    try:
        username = str(current_user.name)
    except AttributeError:
        username = 'Anonymous'
    print(username)
    if not str(current_user).split('>')[0] == '<User':
        return redirect("/login")
    else:
        return render_template('common/chat_page.html', title=inf_dict['title_chat'], logo_txt=inf_dict['logo_txt'],
                               footer_inf=inf_dict['footer'],
                               username=username, anonymous=str(current_user).split('>')[0] == '<User',
                               c_user=current_user, message_lst=message_lst)


@socketio.on('message')
def handleMessage(data):
    db_sess = db_session.create_session()
    print(f"Message: {data}")
    send(data, broadcast=True)
    message = Message()
    message.text = data['msg']
    try:  # Предотвращение ошибок в случае анонимного пользователя
        message.is_from_admin = current_user.get_role()
        message.user_name = current_user.get_name()
    except AttributeError:
        message.is_from_admin = False
        message.user_name = 'Anonymous'
    db_sess.add(message)
    db_sess.commit()


@app.route('/administrate', methods=['GET', 'POST'])
def administrate():
    if current_user.get_role():
        db_sess = db_session.create_session()
        users = db_sess.query(User).filter()
        users_dict = []
        for i in users:
            users_dict.append(
                f"ID: {i.id}, NAME: {i.name}, EMAIL: {i.email}, DATE OF CREATION OF THIS ACCOUNT: {i.created_date.strftime('%H:%M:%S')}")
        return render_template('common/adm.html', title=inf_dict['title_administration'],
                               logo_txt=inf_dict['logo_txt'],
                               footer_inf=inf_dict['footer'], users_dict=users_dict,
                               anonymous=str(current_user).split('>')[0] == '<User', c_user=current_user,
                               users_lst=[(i.id, i.name, i.email, i.created_date.strftime('%H:%M:%S')) for i in users])


if __name__ == '__main__':
    main(path_json, path_sever_json)
