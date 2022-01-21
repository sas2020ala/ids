import sys
import uuid
from typing import Any

from m.mgr import Logger

APP_ID = "SELECT app_i" \
         " FROM app_r " \
         " WHERE app_code = %s" \
         " AND v_last='y'" \
         " AND status=1",


def is_registered(dc: Any, app_code: str) -> int:
    """ Checking the application registration
    Parameters:
    dc (object): Data connection
    app_code(str): application hash code

    Returns:
    str: application access token
    """
    con = dc.check()
    cursor: Any = None
    app_token: str = ""

    try:
        cursor = con.cursor()
        cursor.execute(APP_ID, [app_code])
        r: list = cursor.fetchone()

        if r:
            app_token = uuid.uuid1().hex
            dc.save_to_cache(app_token, {"app_i": r[0]})

    except Exception as e:
        Logger.error(f"dbi.user.is_registered: {sys.exc_info()[-1].tb_lineno}: {e}")
        dc.rollback()

    finally:
        if cursor:
            cursor.close()

    return app_token
