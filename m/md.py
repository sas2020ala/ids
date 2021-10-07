import os

sms = {
    1: "- Ваш код подтверждения для службы 109",
    2: "- Ваш код подтверждения для терминал",
    3: "- Ваш код подтверждения для мобильного приложения школы",
    4: "- Ваш код подтверждения для мобильного приложения школы"
}

home = os.environ.get('HOME')
path = os.path.join(home, '.ods')
a_key = os.path.join(path, '.ask')
a_cache = os.path.join(path, ".cache")
a_db = os.path.join(path, ".db")
a_sms = os.path.join(path, ".sm")
a_jwt = os.path.join(path, ".key")


