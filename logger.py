import os

import logging

def setupLogger(sHandlerLevel,fHandlerLevel,name):
    # check to make sure the logging director exists
    if not os.path.exists("output/log/"):
       os.makedirs("output/log/")

    # Setup logger
    formatter = "%(asctime)s - %(levelname)s - (%(threadName)-2s) - %(name)s - %(message)s"
    dfmt = "%Y-%m-%d %H:%M:%S"
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    sHandler = logging.StreamHandler()
    sHandler.setLevel(sHandlerLevel)
    sHandler.setFormatter(logging.Formatter(formatter,dfmt))
    logger.addHandler(sHandler)

    fHandler = logging.FileHandler('output/log/diagnostics.log')
    fHandler.setLevel(fHandlerLevel)
    fHandler.setFormatter(logging.Formatter(formatter,dfmt))
    logger.addHandler(fHandler)

    return logger