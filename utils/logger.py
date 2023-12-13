import logging

def logger_conf():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(fmt='%(levelname)s - %(module)s - %(funcName)s - %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    # Asegúrate de que no haya duplicados de manejadores
    if not logger.handlers:
        logger.addHandler(handler)

    return logger

logger = logger_conf()