import argparse
import os

import main

path_json = "Res_json/str.json"
path_sever_json = "Res_json/server.json"
parser = argparse.ArgumentParser()


def file_not_found(arg, path):
    print(
        "Файл: {path}, переданный в качестве аргумента: {arg} не существует, либо доступ к нему запрещён. Попробуйте "
        "пересоздать файл или поменять его директорию".format(
            arg=arg, path=path))


def create_boot_file():
    with open("boot.py", "w") as boot_file:
        boot_file.write("import main\nmain.main('{path_json}', '{path_sever_json}')".format(path_json=path_json,
                                                                                            path_sever_json=path_sever_json))


def run_main(path_json, path_sever_json, path_intro_image):
    main.main(path_json, path_sever_json, path_intro_image)


parser.add_argument("--json_path_rus",
                    help="Путь к файлу .json с русской версией. В нём находятся все текстовые фрагменты, используемые "
                         "приложением. ")
# parser.add_argument("--json_path_eng", default="", help="Путь к файлу .json с английской версией. В нём находятся
# все текстовые фрагменты, используемые приложением. " "Пример такого файла лежит в корне проекта.")
parser.add_argument("--json_path_server",
                    help="Путь к файлу .json с серверными настройками")
parser.add_argument("--path_intro_image",
                    help="Путь к файлу с интро (картинка jfif)")
parser.add_argument("--boot_file", default="yes", choices=["yes", "no"],
                    help="Создавать ли отдельный запускной файл?")
# parser.add_argument("--lang", default="rus", choices=["rus", "eng"])
args = parser.parse_args()

if not os.path.exists(args.json_path_rus):
    file_not_found("json_path_rus", args.json_path_rus)
if not os.path.exists(args.json_path_server):
    file_not_found("json_path_server", args.json_path_server)
if not os.path.exists(args.path_intro_image):
    file_not_found("path_intro_image", args.json_path_server)
if args.boot_file == "yes":
    create_boot_file()

path_json = args.json_path_rus
path_sever_json = args.json_path_server
path_intro_image = args.path_intro_image

run_main(path_json, path_sever_json, path_intro_image)
