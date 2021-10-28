# Copyright (c) 2020 SAS Company
"""
Module for working with system
"""
import datetime
import json
import os
import random
import string
import jwt

import requests

from m import md


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
        if __debug__:
            print(
                f"{System.app_sms_rest()}"
                f"&phones={a}"
                f"&mes={code} - {md.sms[b]}"
                f"&fmt=3"
            )

        res = requests.get(
            f"{System.app_sms_rest()}"
            f"&phones={a}"
            f"&mes={code} - {md.sms[b]}"
            f"&fmt=3"
        )
        if __debug__:
            print(f"sms result: {json.loads(res.content)}, {code}")
        return json.loads(res.content), code

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
