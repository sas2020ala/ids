# Copyright (c) 2020 SAS Company
"""
Module for working with system
"""
import datetime
import json
import os
import random
import re
import smtplib
import string
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import jwt
import requests

from m import md
from m.md import E_MAIL_SERVER_NAME, E_MAIL_SERVER_PORT


class Logger:

    def __init__(self):
        pass

    @staticmethod
    def inform(msg):
        if __debug__:
            print(f"\033[96m Info: {msg}\033[00m")
        pass

    @staticmethod
    def notify(msg):
        if __debug__:
            print(f"\033[93m Warning: {msg}\033[00m")
        pass

    @staticmethod
    def error(msg):
        if __debug__:
            print(f"\033[91m Error->{msg}\033[00m")
        pass


class System:

    def __init__(self):
        pass

    @staticmethod
    def crash(msg=None):
        if __debug__ and msg:
            print(f"\033[91m Error->{msg}\033[00m")
        exit(1)

    @staticmethod
    def send_sms(a: str, b: int):
        code = System.generate_code()

        res = requests.get(
            f"{System.app_sms_rest()}"
            f"&phones={a}"
            f"&mes={code} {md.sms[b]}"
            f"&fmt=3"
        )
        if __debug__:
            print(f"sms result: {json.loads(res.content)}, {code}")
        return json.loads(res.content), code

    @staticmethod
    def send_by_email(user_email):
        e_mail, pw = System.app_email()
        code = System.generate_code()
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Link"
        msg['From'] = e_mail
        msg['To'] = user_email

        text = f"Hi!\nYOUR CODE: {code}\n   {code}"
        html = f"<html>\n" \
               f"<head></head>\n" \
               f"<body>\n" \
               f"<div>Hi!<br>\n" \
               f"<h3>Your code:</h3><br>\n" \
               f"<h2>{code}</h2>\n" \
               f"</div>\n" \
               f"</body>\n" \
               f"</html>\n"
        msg.attach(MIMEText(text, 'plain'))
        msg.attach(MIMEText(html, 'html'))

        try:
            with smtplib.SMTP_SSL(E_MAIL_SERVER_NAME, E_MAIL_SERVER_PORT) as smtp:
                smtp.login(e_mail, pw)
                smtp.send_message(msg)
        except Exception as e:
            Logger.error(f"System.send_by_email: {sys.exc_info()[-1].tb_lineno}: {e}")
            return None
        else:
            return code

    @staticmethod
    def check(upw: str, pwd: str, slt: str) -> bool:
        """The function checks whether the password typed by a user (hashed via the certain algorithm)
        with the hashed value of it in the database.

        Returns
        -------
        a boolean value"""

        if __debug__:
            print(f'  auth.check')

        return hmac.compare_digest(upw, generate(pwd, slt))

    @staticmethod
    def generate_code():
        """
        Генерирует смс-код подтверждения
        """

        # get microsecond in format 'xxxxxx'
        a = int(datetime.datetime.now().strftime("%f"))

        # get randomly one letter in uppercase and get its ascii code
        b = ord(random.choice(string.ascii_uppercase))

        # XOR 'a' and 'b'
        code = a ^ b

        # if length of code less than 6, increase the number of digits
        if len(str(code)) != 6:
            x = ''
            cn = 6 - len(str(code))
            for i in range(cn):
                x += str(random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9]))
            code = int((str(code) + str(x)))

        return code

    @staticmethod
    def valid_number(pn):
        """
        Қолданушының номері тексеріледі.
        Номер келесі форматта болу қажет "77771112233"

        :param pn: str
            phone number
        :return: True
        """
        pn.replace(" ", "")
        if pn.startswith("77") and pn.isdigit() and len(pn) == 11:
            return True

        return False

    @staticmethod
    def valid_email(email: str) -> bool:
        """
        The function checks if the email entered by a user is valid or not.
        Parameters
        ----------
        email

        Returns
        -------
        a boolean value"""

        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

        if re.fullmatch(regex, email):
            return True
        return False

    @staticmethod
    def jwt_token_for_mobile(un, phone):
        """
        JWT Token For Mobile
        Мобильді қосымшаға арнап jwt токен құрастырады.
        Токеннің өмір сүру уақыты шектелмеген.
        :param un: str
            user name
        :param phone: str
        :return: "jwt token"
        """
        k, _ = System.app_jwt_params()
        return jwt.encode(
            {
                "username": un,
                "phone": phone,
                "data": str(datetime.datetime.utcnow())
            },
            f"{k}{phone}",
            algorithm="HS256"
        )

    @staticmethod
    def app_secret_key():
        a_key = md.a_key
        if not os.path.exists(a_key):
            System.crash()

        with open(a_key, "r") as f:
            k = f.read(32)
            f.close()

        if not k:
            System.crash()

        return k

    @staticmethod
    def app_email():
        email = md.email
        if not os.path.exists(email):
            System.crash()

        with open(email, "r") as f:
            k: str = f.readline()
            f.close()

        if not k:
            System.crash()

        return k.strip("\n").split(" ")

    @staticmethod
    def app_sms_rest():
        a_sms = md.a_sms
        if not os.path.exists(a_sms):
            System.crash()

        with open(a_sms, "r") as f:
            d: str = f.read()  # [server, login, password]
            f.close()

        if not d:
            System.crash()

        return d.split("\n")[0]

    @staticmethod
    def app_jwt_params():
        a_jwt = md.a_jwt
        if not os.path.exists(a_jwt):
            System.crash()

        with open(a_jwt, "r") as f:
            k: str = f.readline()
            d: int = int(f.readline())
            f.close()

        if not d:
            System.crash()

        return k, d
