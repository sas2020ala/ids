import os

home = os.environ.get('HOME')
path = os.path.join(home, '.ods')
a_key = os.path.join(path, '.ask')
a_cache = os.path.join(path, ".cache")
a_db = os.path.join(path, ".db")
a_sms = os.path.join(path, ".sm")
a_jwt = os.path.join(path, ".key")
email = os.path.join(path, ".email")

E_MAIL_SERVER_NAME = "mail.decoritm.com"
E_MAIL_SERVER_PORT = 465
