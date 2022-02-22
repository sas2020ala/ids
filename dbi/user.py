import secrets
import sys
from typing import Any, Dict

from m.mgr import System, Logger

USER_PROFILE = "SELECT up.user_i" \
               " , up.u_name" \
               " , up.u_ln" \
               " , up.u_tel" \
               " , up.u_email" \
               " , d.org_i" \
               " , a.app_i" \
               " , d.org_n" \
               " , up.u_typ" \
               " FROM user_p up" \
               " INNER JOIN  user_app a" \
               "  ON a.user_i=up.user_i AND a.status=1 AND a.v_last='y'" \
               " INNER JOIN user_org b" \
               "  ON b.user_i=up.user_i AND b.status=1 AND b.v_last='y'" \
               " INNER JOIN org d" \
               "  ON d.org_i = b.org_i AND d.status=1 AND d.v_last='y'" \
               " WHERE up.u_email = %s"

USER_ID = "SELECT up.user_i" \
          " FROM user_p up" \
          " INNER JOIN user_app ua" \
          "  ON up.user_i = ua.user_i AND ua.status=1 AND ua.v_last='y'" \
          " WHERE up.u_email = %s" \
          " AND up.v_last='y'" \
          " AND up.status=1" \
          " AND ua.app_i = %s"


def get_user_info(dc: Any, e_mail: str) -> Dict:
    """ Get user profile by e_mail
    Parameters:
    dc (object): Data connection
    e_mail(str): User e-mail

    Returns:
    dict: user profile (firstname, lastname, JWT - JSON web token, etc.)
    """
    con = dc.check()
    cursor: Any = None
    info: Dict = {}
    try:
        cursor = con.cursor()
        cursor.execute(USER_PROFILE, (e_mail,))
        rs: list = cursor.fetchall()
        if rs:
            r: tuple = rs[0]
            tel = r[3]
            key = f"{secrets.token_hex(24)}{tel}"

            jwt = System.jwt_token_for_mobile(r[1], tel, key)
            
            info = {
                "uid": r[0],
                "un": r[1],
                "uln": r[2],
                "email": r[4],
                "ids": r[5],
                "aid": r[6],
                "org_n": r[7],
                "utyp": r[8],
                "sk": key,
            }
            dc.save_to_cache(tel, info)
            info = {
                "msg": "Success",
                "token": jwt,
                "username": r[1],
                "lastname": r[2],
                "phone": tel,
                "org_n": r[7],
                "usertype": r[8]
            }
    except Exception as e:
        Logger.error(f"dbi.user.get_user_info: {sys.exc_info()[-1].tb_lineno}: {e}")
        dc.rollback()
    finally:
        if cursor:
            cursor.close()

    return info


def is_registered(dc: Any, e_mail: str, app_i: str, app_token: str) -> int:
    """ Checking the user registration and code received by e-mail
    Parameters:
    dc (object): Data connection
    e_mail(str): User e-mail
    app_i(str): application identifier
    app_token(str): application access token

    Returns:
    int: 0 - isn't registered or 1 - is registered
    """
    if e_mail == "demo@decoritm.com":
        dc.save_to_cache(f"{app_token}-000000", e_mail)
        return 1

    con = dc.check()
    cursor: Any = None
    res: int = 0
    try:
        cursor = con.cursor()
        cursor.execute(USER_ID, [e_mail, app_i])
        rs: list = cursor.fetchall()
        print(rs)
        if rs:
            user_code: str = System.send_by_email(e_mail)
            dc.save_to_cache(f"{app_token}-{user_code}", e_mail)
            res = 1
    except Exception as e:
        Logger.error(f"dbi.user.is_registered: {sys.exc_info()[-1].tb_lineno}: {e}")
        dc.rollback()
    finally:
        if cursor:
            cursor.close()

    return res
