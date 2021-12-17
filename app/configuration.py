import os


class Config:
    SECRET_KEY = os.urandom(32)
    LOG_PATH = "data/Player.log"
    # LOG_PATH = "c:/Users/axela/appdata/LocalLow/Wizards Of The Coast/MTGA/Player.log"

