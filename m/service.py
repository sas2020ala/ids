import json
import os
import sys
import uuid
from functools import wraps
from typing import Dict

from flask import Flask, request, session
from flask_cors import CORS

import dbi.app
from dbi import user
from m import md, proto
from m.mairadb import Database
from m.mgr import System, Logger
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

SEL_DEV = """
    SELECT u.u_tel, ud.id
    FROM device d 
    INNER JOIN user_device ud on d.d_id = ud.d_id
    INNER JOIN users u on ud.u_id = u.u_id
    WHERE d.h_code = %s;
    """


up_dev = """
    UPDATE user_device
    SET r_status = 1
    WHERE id = %s
    """


@app.route("/app/verify", methods=["GET", "POST"])
def verify_app():
    """Application is identified by hash code

    Returns
    dict: app_token and status"""

    try:
        if not request.method == "POST":
            return proto.msg_wrong("Wrong request")

        data: dict = json.loads(request.data)
        app_token = dbi.app.is_registered(dc, data["appl_code"])

        if app_token:
            return proto.msg_success({"access_token": app_token, "msg": "Success"})
        else:
            return proto.msg_error("You sent the wrong data")

    except Exception as e:
        Logger.error(f"m.service.verify_app: {sys.exc_info()[-1].tb_lineno}: {e}")
        return proto.msg_error("At the moment you cannot log in."
                               " Please contact your system administrator")


@app.route(f"/user/auth_by_email", methods=["POST"])
def auth_by_email():
    """User is identified by a previously registered e-mail

    Returns
    dict: user data (token, profile, etc.)"""

    try:
        if not request.method == "POST":
            return proto.msg_wrong("Wrong request")

        app_token = request.headers.get("access-token")

        if not app_token:
            return proto.msg_wrong("No access token")

        data = json.loads(request.data)
        e_mail = data["email"]

        if e_mail and System.valid_email(e_mail):
            app_i: int = dc.get_from_cache(app_token)["app_i"]

            if user.is_registered(dc, e_mail, app_i, app_token) == 1:
                return proto.msg_success({"msg": "Success"})
            else:
                return proto.msg_error("At the moment you cannot log in."
                                       " Please contact your system administrator")
        else:
            proto.msg_error("Wrong user e-mail")

    except Exception as e:
        Logger.error(f"m.service.auth_by_email: {sys.exc_info()[-1].tb_lineno}: {e}")
        return proto.msg_error("At the moment you cannot log in."
                               " Please contact your system administrator")


@app.route("/user/verify", methods=["POST"])
def verify_code() -> Dict:
    """Checking the code received by e-mail.

    Returns
    dict: user data (token, profile, etc.)"""

    try:
        if not request.method == "POST":
            return proto.msg_wrong("Wrong request")

        app_token = request.headers.get("access-token")

        if not app_token:
            return proto.msg_wrong("No access token")

        data = json.loads(request.data)
        code_client: str = data["code"]
        e_mail = dc.get_from_cache(f"{app_token}-{code_client}")

        if e_mail is None:
            return proto.msg_wrong("e-mail not indicated")

        user_data = user.get_user_info(dc, e_mail)

        if user_data:
            return proto.msg_success(user_data)

    except Exception as e:
        Logger.error(f"m.service.verify_code: {sys.exc_info()[-1].tb_lineno}: {e}")
        return proto.msg_error("At the moment you cannot log in."
                               " Please contact your system administrator")


@app.route("/user/register", methods=["POST"])
def user_register():

    try:
        if not request.method == "POST":
            return proto.msg_wrong("Wrong reuest")

        data = json.loads(request.data)

        first_name = data["f_n"]
        last_name = data["l_n"]
        tel_number = data["tel"]
        email = data["email"]
        app_i = data["app_i"]
        org_i = data["org_i"]

        user_i = user.user_registration(dc, first_name, last_name, tel_number, email, app_i, org_i)

        if user_i:
            return proto.msg_success(user_i)

    except Exception as e:
        Logger.error(f"m.service.verify_code: {sys.exc_info()[-1].tb_lineno}: {e}")
        return proto.msg_error("At the moment you cannot log in."
                               " Please contact your system administrator")


@app.route("/checkDevice", methods=["POST"])
def check_device():

    try:
        if not request.method == "POST":
            return proto.msg_wrong("Wrong reuest")

        data = json.loads(request.data)
        con = dc.check()
        cur = con.cursor()
        cur.execute(SEL_DEV, (data['terminal'],))
        res = cur.fetchone()
        print(res)
        if res and res[0] == data["email"]:

            app_token = request.headers.get("access-token")

            if not app_token:
                return proto.msg_wrong("No access token")

            e_mail = data["email"]

            if e_mail and System.valid_email(e_mail):
                app_i: int = dc.get_from_cache(app_token)["app_i"]

                if user.is_registered(dc, e_mail, app_i, app_token) == 1:
                    dc.save_to_cache(e_mail+"term", data["terminal"])
                    return proto.msg_success({"msg": "Success"})
                else:
                    return proto.msg_error("At the moment you cannot log in."
                                           " Please contact your system administrator")
            else:
                proto.msg_error("Wrong user e-mail")

    except Exception as e:
        Logger.error(f"m.service.verify_code: {sys.exc_info()[-1].tb_lineno}: {e}")
        return proto.msg_error("At the moment you cannot log in."
                               " Please contact your system administrator")


@app.route("/saveDevice", methods=["POST"])
def save_device():
    tag = "SaveDevice"
    cur = None
    conn = None
    try:
        dat = json.loads(request.data)

        conn = dc.check()
        cur = conn.cursor()
        # rd = dc.get_from_cache(f"{dat['email']}-{dat['code']}")
        terminal_id = dc.get_from_cache(dat["email"]+"term")

        if terminal_id:
            cur.execute(up_dev, (terminal_id,))
            return proto.msg_success({"own": dat["phone"], "tid": terminal_id})
        app.logger.warning(f'{tag} - {dat} мәліметтер дұрыс емес')
        return proto.msg_wrong("Wrong data")

    except Exception as e:
        Logger.error(f"m.service.verify_code: {sys.exc_info()[-1].tb_lineno}: {e}")
        return proto.msg_error("At the moment you cannot log in."
                               " Please contact your system administrator")


# @app.route(f"{base_url}/checkDevice", methods=["POST"])
# @access_token_required
# def check_device_info():
#     """Check Device Info (Pos terminal 1)
#     Pos терминалда активатция жасау.
#     Терминалдың иесі номерін және терминалдың id - ін жібереді.
#     Егер мәліметтер дұрыс болса қолданушыны растау мақсатында номеріне
#     смс код жіберіледі.
#     :return:
#     """
#     tag = "CheckDevice"
#     cur = None
#     conn = None
#     try:
#         dat = json.loads(request.data)
#
#         conn = db.get_con()
#         cur = conn.cursor()
#         cur.execute(sql["sel_dev"], (dat["terminal"],))
#         res = cur.fetchone()
#         print(res)
#         print(dat)
#         if res and res[0] == dat["phone"]:
#             tkn = get_access_token(request)
#             appl_id = redis_db.read(tkn)["appl_id"]
#
#             result, _code = smss.send_sms(dat["phone"], appl_id)
#             if "error" in result:
#                 return proto.msg_error(result["error"])
#
#             redis_db.write(f"{dat['phone']}-{_code}", {"tid": res[1]})
#             return proto.msg_success({"code": _code, "msg": "Success"})
#         app.logger.warning(f'{tag} - {dat} мәліметтер дұрыс емес')
#         return proto.msg_wrong("Wrong data")
#     except Exception as e:
#         app.logger.exception(e)
#         return proto.msg_error("Error")
#     finally:
#         if cur:
#             cur.close()
#             db.close(conn)
#
#
# @app.route(f"{base_url}/saveDevice", methods=["POST"])
# @access_token_required
# def save_device_info():
#     """Save Device Info (Pos terminal 2)
#     Pos терминалда активатция жасау.
#     Қолданушы номеріне келген смс код дұрыс
#     болса қосымша әрі қарай жұмыс жасау үшін
#     терминалдың мәліметтері (status) өзгертіледі.
#     Parameters
#     ----------
#     terminal_id: str
#
#     Returns
#     -------
#     {
#         "sts": "s",
#         "dat": {
#             "own": "user phone",
#             "tid": "terminal id"
#         }
#     }
#     """
#     tag = "SaveDevice"
#     cur = None
#     conn = None
#     try:
#         dat = json.loads(request.data)
#
#         conn = db.get_con()
#         cur = conn.cursor()
#         rd = redis_db.read(f"{dat['phone']}-{dat['code']}")
#         terminal_id = rd["tid"]
#
#         if terminal_id:
#             cur.execute(sql['up_dev'], (terminal_id,))
#             return proto.msg_success({"own": dat["phone"], "tid": rd["tid"]})
#         app.logger.warning(f'{tag} - {data} мәліметтер дұрыс емес')
#         return proto.msg_wrong("Wrong data")
#     except Exception as e:
#         app.logger.exception(e)
#         conn.rollback()
#         return proto.msg_error("Error")
#     finally:
#         if cur:
#             cur.close()
#             db.close(conn)


if __name__ == "__main__":
    if not os.path.exists(md.path):
        System.crash()

    if len(sys.argv) > 2:
        sys.exit(2)

    host, port = sys.argv[1].split(":")
    app.run(host, int(port), debug=True)
