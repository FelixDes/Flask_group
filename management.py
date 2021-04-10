import argparse

from data import db_session
from data.users import User

parser = argparse.ArgumentParser()

parser.add_argument("--action", choices=["del", "adm", "low", "ban", "unban"],
                    help="Аргумент del удалит пользователя, аргумент adm даст пользователю статус администратора, "
                         "аргумент low отнимет привелегию у пользователя, аргумент ban забанит пользователя, "
                         "арумент unban разбанит пользователя")

parser.add_argument("--username", type=str, help="Иня пользователя, над которым мы хотим произвести действие")

args = parser.parse_args()

db_session.global_init("db/main.db")
db_sess = db_session.create_session()

if args.action == "del":
    try:
        user = db_sess.query(User).filter(User.name == args.username).first()
        db_sess.delete(user)
        db_sess.commit()
        print("Успех")

    except BaseException:
        print("Что-то пошло не так")


elif args.action == "low" or args.action == "adm":
    try:
        user = db_sess.query(User).filter(User.name == args.username).first()

        if args.action == "low":
            user.set_role(False)
        elif args.action == "adm":
            user.set_role(True)

        db_sess.add(user)
        db_sess.commit()
        print("Успех")

    except BaseException:
        print("Что-то пошло не так")

elif args.action == "ban" or args.action == "unban":
    try:
        user = db_sess.query(User).filter(User.name == args.username).first()

        if args.action == "unban":
            user.set_banned(False)
        elif args.action == "ban":
            user.set_banned(True)

        db_sess.add(user)
        db_sess.commit()
        print("Успех")

    except BaseException:
        print("Что-то пошло не так")
