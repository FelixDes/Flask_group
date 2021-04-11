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

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config[
    'SECRET_KEY'] = "_ti{qxjXpNadwPPGaOh{zBawz^GBBpoIU|qpGpEVzgRzqhqeZ]hv_oeBhb|WBkmdRANtw}akIfMgOLm{r]ZnYiZcBFXZz{'"

socketio = SocketIO(app, cors_allowed_origins="*")

server_dict = {}


def parse_all(json_path):  # Ф-ция парсинга json-а
    try:
        with open(json_path, "r", encoding='utf-8') as file:
            json_dict = json.load(file)
        return json_dict

    except BaseException:
        print("Файл не существует")
        return "Файл не существует"


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
    try:
        is_admin = current_user.is_admin
    except AttributeError:
        is_admin = False
    return render_template("common/main_page.html", title=inf_dict['title_main'],
                           interesting_information=inf_dict['text_about'],
                           information_list=inf_dict['text_about_our_work'],
                           logo_txt=inf_dict['logo_txt'], chat_btn_text=inf_dict['chat_btn_text'],
                           connection_list=inf_dict['how_to_contact_us'], how_to_find_us=inf_dict['how_to_find_us'],
                           footer_inf=inf_dict['footer'], intro_image=path_intro_image,
                           anonymous=str(current_user).split('>')[0] == '<User',
                           c_user=current_user, admin=is_admin)


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
            # Если пользователь отсутствует в базе данных
            return render_template('common/login_page.html', title=inf_dict['title_login'],
                                   logo_txt=inf_dict['logo_txt'], form=form,
                                   message="Такого пользователя не обнаружено")

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

    message_lst = [(f"<strong>{i.user_name.capitalize() + '<sup>admin</sup>' if db_sess.query(User).filter(User.name == i.user_name).first().is_admin else i.user_name.capitalize()}:</strong> " \
                   f"{i.text} <sub>{i.created_date.strftime('%H:%M')}</sub>", i.id) for i in
                   messages]

    print(message_lst)

    try:
        username = str(current_user.name)
        is_admin = current_user.is_admin
    except AttributeError:
        username = 'Anonymous'
        is_admin = False
    print(username)

    if not str(current_user).split('>')[0] == '<User':
        return redirect("/login")

    else:
        return render_template('common/chat_page.html', title=inf_dict['title_chat'], logo_txt=inf_dict['logo_txt'],
                               footer_inf=inf_dict['footer'],
                               username=username, anonymous=str(current_user).split('>')[0] == '<User',
                               c_user=current_user, message_lst=message_lst, admin=is_admin)


@socketio.on('message')
def handleMessage(data):
    db_sess = db_session.create_session()

    try:
        if data['role'] == 'ban':
            user = db_sess.query(User).filter(User.id == data['id']).first()
            if user.banned:
                user.banned = 0
            else:
                user.banned = 1
        elif data['role'] == 'del_mes':
            if db_sess.query(Message).filter(Message.id == int(data['id'])).first():
                db_sess.query(Message).filter(Message.id == int(data['id'])).delete()
            else:
                del_mes_inf = 'Сообщения с данным ID не найдено'
        db_sess.commit()

    except KeyError:
        if str(current_user).split('>')[0] == '<User' or not current_user.banned:
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
                               users_lst=[(i.id, i.name, i.email, i.created_date.strftime('%d.%m.%y %H:%M:%S'),
                                           'YES' if i.banned else 'NO') for i in users], admin=current_user.is_admin)


if __name__ == '__main__':
    main(path_json, path_sever_json, path_intro_image)
