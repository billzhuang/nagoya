from datetime import datetime
import pymysql

# DB config
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '1qaz!QAZ',
    'db': 'nagoya',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
}

# API config
INITIAL_PRICE_FOR_RESET = 100
INCREASE_RATE = 0.1
END_INCREASE_RATE = 0.2

INITIAL_TEAM_BALANCE_FOR_RESET = 1000

GLOBAL_FIRST_PURCHASE_LOCATION_BONUS = 30
TEAM_FIRST_PURCHASE_LOCATION_BONUS = 20

START_TIME = datetime(2017, 11, 8, 16, 00, 00)
PRICE_INCREASE_PERIOD_SECONDS = 30 * 60

ADMIN_PASSCODE_QUERY_PARAM = "Hikari"

MESSAGE_NEED_ADMIN_PASSCODE = "Need passcode in order to access admin API."

RESPONSE_INVALID_PASSCODE = {
    "status": -1,
    "message": "Invalid passcode."
}
