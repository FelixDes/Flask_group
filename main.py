from flask import Flask, render_template, redirect

from Forms.user import RegisterForm
from data import db_session
from data.users import User

app = Flask(__name__)
app.config[
    'SECRET_KEY'] = "_ti{qxjXpNadwPPGaOh{zBawz^GBBpoIU|qpGpEVzgRzqhqeZ]hv_oeBhb|WBkmdRANtw}akIfMgOLm{r]ZnYiZcBFXZz{'"


# def main():
#     db_session.global_init("db/main.db")


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
    # main()
    app.run(port=6655)
