import os
import secrets

SMS_LOGIN = "ab@slidtech.com"
SMS_PASS = "Qw123456!"

home = os.environ.get("HOME")
path = os.path.join(home, ".ods")
a_key = os.path.join(path, ".ask")
a_cache = os.path.join(path, ".cache")
a_db = os.path.join(path, ".db")
a_sms = os.path.join(path, ".sm")
a_jwt = os.path.join(path, ".key")

mode = 0o766

if not os.path.exists(path):
    os.mkdir(path, mode)

if not os.path.exists(a_key):
    with open(a_key, "w") as f:
        # f.write(secrets.token_urlsafe(32))
        print("Generate hash code for application...\n")
        f.write(f"{secrets.token_urlsafe(32)}")
        f.close()

if not os.path.exists(a_cache):
    with open(a_cache, "w") as f:
        f.write(input("Enter Redis connection, for example, localhost:6379:0\n"))
        f.close()

if not os.path.exists(a_db):
    with open(a_db, "w") as f:
        f.write(input("Enter DB connection, for example, host:port:db:user:password\n"))
        f.close()

if not os.path.exists(a_sms):
    with open(a_sms, "w") as f:
        # https://smsc.kz/sys/send.php?login=ab@slidtech.com&passwd=Qw123456!
        f.write(input("Enter data of the SMS server, for example, url with parameters\n"))
        f.close()

if not os.path.exists(a_jwt):
    with open(a_jwt, "w") as f:
        f.write(secrets.token_urlsafe(32))
        f.write("\n")
        f.write(input("Enter duration of validity for jwt(minute)\n"))
        f.close()
