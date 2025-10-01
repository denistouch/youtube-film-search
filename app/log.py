import logging

import strings


def exception(e: Exception, *args):
    msg = str(e)
    if args:
        for arg in args:
            msg = f'{msg} {strings.json(arg)}'
    _args = e.args[1:] if len(e.args) > 1 else []
    logging.exception(e.__class__(msg, *_args))


def error(msg: str, *args):
    msg = str(msg)
    if args:
        for arg in args:
            msg = f'{msg} {strings.json(arg)}'

    logging.error(msg)
    

def warning(msg: str, *args):
    msg = str(msg)
    if args:
        for arg in args:
            msg = f'{msg} {strings.json(arg)}'
    
    logging.warning(msg)


def info(msg: str, *args):
    msg = str(msg)
    if args:
        for arg in args:
            msg = f'{msg} {strings.json(arg)}'

    logging.info(msg)


def debug(msg: str, *args):
    msg = str(msg)
    if args:
        for arg in args:
            msg = f'{msg} {strings.json(arg)}'
            
    logging.debug(msg)
