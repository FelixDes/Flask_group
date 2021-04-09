import argparse

from data import db_session
from data.users import User

parser = argparse.ArgumentParser()

parser.add_argument("--action", choices=["del", "adm", "low"],
                    help="Аргумент del удалит пользователя, аргумент adm даст пользователю статус администратора, аргумент low отнимет привелегию у пользователя")

parser.add_argument("--username", type=str)

args = parser.parse_args()

db_session.global_init("db/main.db")
db_sess = db_session.create_session()

if args.action == "del":
    try:
        user = db_sess.query(User).filter(User.name == args.username).first()
        db_sess.delete(user)
        db_sess.commit()
    except BaseException:
        print("Что-то пошло не так")


else:
    try:
        user = db_sess.query(User).filter(User.name == args.username).first()
        if args.action == "low":
            user.set_role(False)
        elif args.action == "adm":
            user.set_role(True)
        db_sess.add(user)
        db_sess.commit()
    except BaseException:
        print("Что-то пошло не так")
