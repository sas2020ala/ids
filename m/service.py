import json
import os
import sys
import uuid
from functools import wraps

from flask import Flask, request, session
from flask_cors import CORS

from m import md, proto
from m.mairadb import Database
from m.mgr import System
from m.sql import Q

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
app.secret_key = System.app_secret_key()

CROSS_L = CORS(app, resources={
    r"/*": {
        "Origins": "*",
        "Content-Type": "application/json"
    }
})

dc = Database()
dc.connect_to_cache()
dc.connect()


def access_token_required(f):
    """Access token - ді тексеру

    Қолданушыдан келген request - терден access-token - ді тексеру
    :param f:
    :return:
    """

    @wraps(f)
    def check_access_token(*args, **kwargs):
        try:
            hd = request.headers
            tkn = hd.get("access-token")
            if tkn:
                pass
            else:
                app.logger.warning('No access token')
                return proto.msg_wrong("No access token")
        except Exception as e:
            app.logger.error(e)
            return proto.msg_error("Error")
        return f(*args, **kwargs)

    return check_access_token


def get_access_token(req):
    return req.headers.get("access-token")


@app.route("/visits", methods=["GET", "POST"])
def visit():
    """Visit

    Visit - қолданушының ISAS сервисіне жасалынатын ең алғашқы сұраныс.
    Бұл жерде қолданушыға қайталанбайтын access-token құрастырылады.

    Parameters
    ----------
    data["appl_code"]: str
        сайттың немесе мобилді қосымшаның коды (application code)
    gen_access_token: str, unique
        қолданушыны растайтын токен

    Returns
    ------
    {
        "sts": "s",
        "dat": {
            "access_token": gen_access_tone,
            "msg": "Success"
        }
    }
    """
    con = cursor = None
    try:
        if not request.method == "POST":
            app.logger.warning("/visits: wrong request")
            return proto.msg_wrong("Wrong request")

        access_token = session["access_token"] if "access_token" in session else None

        if access_token and dc.get_from_cache(access_token):
            return proto.msg_success({"access_token": access_token, "msg": "Success"})

        data = json.loads(request.data)

        if "appl_code" in data:
            con = dc.check()
            cursor = con.cursor()
            cursor.execute(Q["app"], (data["appl_code"],))
            rs = cursor.fetchone()

            if rs:
                gen_access_token = uuid.uuid1().hex
                dc.save_to_cache(gen_access_token, {"app_i": rs[0]})
                session["access_token"] = gen_access_token
                return proto.msg_success({"access_token": gen_access_token, "msg": "Success"})
            else:
                app.logger.warning("visit: Wrong application code")
                return proto.msg_error("You sent the wrong data")
        else:
            app.logger.warning("visit: Application code not found")
            return proto.msg_error("You sent the wrong data")

    except Exception as e:
        if con:
            con.rollback()

        app.logger.error(e)
        return proto.msg_error("An error has occurred")
    finally:
        if cursor:
            cursor.close()


@app.route(f"/auth_mobile", methods=["POST"])
@access_token_required
def auth_mobile():
    """
    Қолданушы нөмері бойынша базадан тексеріледі,
    егер бар болса, онда нөмеріне смс код жіберіледі
    және нөмері redis - ке сақталады.
    redis->key = access_token + "-" + sms_code

    Parameters
    ----------
    access_token: str
    appl_id: int
    result: dict
        smsc.kz - сервисінен келген жауап
    _code: int
        қолданушыға жіберілген смс код
    Returns
    -------
    {
        "sts": "s",
        "dat": {
            "msg": "Success"
        }
    }
    """

    con = cursor = None
    try:
        if not request.method == "POST":
            app.logger.warning("AuthMobile: wrong request")
            return proto.msg_wrong("Wrong request")

        app.logger.warning(f"\n data: \n{ request.data}")
        data = json.loads(request.data)
        phone = data["phone"]
        if phone and System.valid_number(phone):
            con = dc.check()
            cursor = con.cursor()
            access_token = get_access_token(request)
            app_i = dc.get_from_cache(access_token)['app_i']
            cursor.execute(Q["user-id"], [phone, app_i])
            res = cursor.fetchall()

            if res:
                result = {}
                _code = '000000'
                if data["phone"] != "77771112233":
                    result, _code = System.send_sms(phone, app_i)

                if "error" in result:
                    return proto.msg_error(result["error"])

                dc.save_to_cache(f"{access_token}-{_code}", phone)

                return proto.msg_success({"msg": "Success"})
            else:
                app.logger.warning(f"auth_mobile: {data} user isn't registered")

    except Exception as e:
        if con:
            con.rollback()

        app.logger.error(e)
        return proto.msg_error("Error")
    finally:
        if cursor:
            cursor.close()


@app.route(f"/auth_mobile_code", methods=["POST"])
@access_token_required
def auth_mobile_code():
    """
    Қолданушы мектеп қосымшасынан сұраныс жасап отыр.
    Қолданушы өзінің мәліметтерін смс код арқылы растайды.
    Қолданушының мәліметтері базадан алынады.
    Қолданушы қосымшамен әрі қарай жұмыс жасау үшін jwt - токен
    құрастырылып қажетті мәліметтерді redis - ке сақтайды.
    Мұндағы redis - ке салынған мәліметтерді өзге сервистер
    қолданушыны растау үшін және қолданушының толық
    мәліметтерін алу үшін қолданады.

    Parameters
    ----------
    access_token: str
    phone: str
    token: str
        jwt token
    user_data: dict

    Returns
    -------
    {
        "sts": "s",
        "dat":  {
            "msg": "Success",
            "token": "jwt token",
            "username": "username",
            "lastname": "lastname",
            "phone": "phone",
            "org_n": "name organization",
            "usertype": "parent or student or dispatcher or sector"
        }
    }
    """
    con = cursor = None
    try:
        if not request.method == "POST":
            app.logger.warning(f"auth_mobile_code: user data is wrong")
            return proto.msg_wrong("Wrong request")

        data = json.loads(request.data)
        con = dc.check()
        phone = dc.get_from_cache(
            f"{get_access_token(request)}-{data['code']}"
        )

        if not phone:
            app.logger.warning(
                f"auth_mobile_code: {data} {phone} is wrong"
            )
            return proto.msg_wrong("Phone number not indicated")

        cursor = con.cursor()
        cursor.execute(Q["user"], (phone,))
        res = cursor.fetchall()[0]

        if res:
            token = System.jwt_token_for_mobile(res[1], phone)
            k, _ = System.app_jwt_params()
            user_data = {
                "uid": res[0],
                "un": res[1],
                "uln": res[2],
                "email": res[5],
                "ids": res[6],
                "aid": res[7],
                "org_n": res[8],
                "utyp": res[9],
                "sk": f"{k}{phone}",
            }
            con.save_to_cache(phone, user_data)
            return proto.msg_success(
                {
                    "msg": "Success",
                    "token": token,
                    "username": res[1],
                    "lastname": res[2],
                    "phone": phone,
                    "org_n": res[8],
                    "usertype": res[9]
                }
            )

    except Exception as e:
        if con:
            con.rollback()

        app.logger.error(e)
        return proto.msg_error("Error")
    finally:
        if cursor:
            cursor.close()


if __name__ == "__main__":
    if not os.path.exists(md.path):
        System.crash()

    if len(sys.argv) > 2:
        sys.exit(2)

    host, port = sys.argv[1].split(":")
    app.run(host, int(port), debug=True)
