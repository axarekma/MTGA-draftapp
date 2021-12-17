import os
from os import path


class Config:
    SECRET_KEY = os.urandom(32)
    #LOG_PATH = "data/Player.log"
    LOG_PATH = path.expandvars(r'%USERPROFILE%\AppData\LocalLow\Wizards Of The Coast\MTGA\Player.log')
