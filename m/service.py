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


if __name__ == "__main__":
    if not os.path.exists(md.path):
        System.crash()

    if len(sys.argv) > 2:
        sys.exit(2)

    host, port = sys.argv[1].split(":")
    app.run(host, int(port), debug=True)
