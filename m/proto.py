from json import dumps


def msg_error(msg):
    return dumps({
        "sts": "e",
        "dat": {
            "msg": msg
        }
    })


def msg_wrong(msg):
    return dumps({
        "sts": "w",
        "dat": {
            "msg": msg
        }
    })


def msg_success(dat):
    return dumps({
        "sts": "s",
        "dat": dat
    })
