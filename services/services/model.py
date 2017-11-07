import pymysql.cursors
from .config import DB_CONFIG


class Model():
    config = DB_CONFIG

    __SQL_GET_BALANCE_BY_TEAM_ID = "SELECT current_balance FROM teams WHERE team_id = %s;"
    __SQL_GET_LOCATIONS_BY_TEAM_ID = "SELECT location_id, location_name FROM locations WHERE current_owner_id = %s;"
    __SQL_GET_LOCATION_INFO = "SELECT location_id, location_name, last_price, last_updated_time, NOW()," \
                              "timediff(NOW(), last_updated_time) as hold_duration, current_owner_id " \
                              "FROM locations WHERE location_id = %s;"
    __SQL_GET_ALL_LOCATIONS_INFO = "SELECT location_id, location_name, last_price, last_updated_time, NOW()," \
                                   "timediff(NOW(), last_updated_time) as hold_duration, current_owner_id" \
                                   " FROM locations;"
    __SQL_GET_ALL_TEAMS_BALANCE = "SELECT team_id, current_balance FROM teams;"
    __SQL_UPDATE_BALANCE_FOR_TEAM = "UPDATE teams SET current_balance = %s WHERE team_id = %s;"
    __SQL_UPDATE_LOCATION_OWNER = "UPDATE locations SET current_owner_id = %s," \
                                  " last_updated_time = NOW() WHERE location_id = %s;"
    __SQL_INSERT_TRANSACTION_PURCHASE = "INSERT INTO transactions VALUES (NULL, 'PURCHASE', %s, %s, %s, %s, NOW());"
    __SQL_INSERT_TRANSACTION_BONUS = "INSERT INTO transactions VALUES (NULL, 'BONUS', %s, 0, %s, %s, NOW());"

    __SQL_RESET_LOCATIONS_OWNER_AND_PRICE = "UPDATE locations SET current_owner_id = 0, last_updated_time = NOW()," \
                                            " last_price = %s WHERE location_id < 200;"
    __SQL_RESET_TEAMS_BALANCE = "UPDATE teams SET current_balance = %s WHERE team_id < 200;"
    __SQL_RESET_TRANSACTIONS = "TRUNCATE transactions;"
    __SQL_GET_TRANSACTION_TIME_FOR_TEAM_ON_LOCATION = "SELECT * FROM transactions WHERE transaction_type = 'PURCHASE' " \
                                                      "AND transaction_to_id = %s AND transaction_location_id = %s;"
    __SQL_GET_TRANSACTION_TIME_ON_LOCATION = "SELECT transaction_id FROM transactions WHERE " \
                                             "transaction_type = 'PURCHASE' AND transaction_location_id = %s;"
    __SQL_GET_TEAM_LAST_3_PURCHASES = "SELECT transaction_to_id, transaction_location_id FROM transactions" \
                                            " WHERE transaction_to_id = %s AND transaction_type = 'PURCHASE'" \
                                            " ORDER BY transaction_time DESC LIMIT 3;"

    def admin_reset_teams_and_locations(self, initial_team_balance, initial_price):
        sql_reset_locations = self.__SQL_RESET_LOCATIONS_OWNER_AND_PRICE % (initial_price)
        sql_reset_teams_balance = self.__SQL_RESET_TEAMS_BALANCE % initial_team_balance
        sql_reset_transactions = self.__SQL_RESET_TRANSACTIONS

        db = pymysql.connect(**self.config)
        cursor = db.cursor()
        try:
            cursor.execute(sql_reset_locations)
            db.commit()
            cursor.execute(sql_reset_teams_balance)
            db.commit()
            cursor.execute(sql_reset_transactions)
            db.commit()
            db.close()
            return True
        except:
            db.rollback()
            db.close()
            return False

    def get_team_balance(self, team_id):
        db = pymysql.connect(**self.config)
        cursor = db.cursor()
        cursor.execute(self.__SQL_GET_BALANCE_BY_TEAM_ID % team_id)
        data = cursor.fetchone()
        db.close()
        return data

    def get_team_locations(self, team_id):
        db = pymysql.connect(**self.config)
        cursor = db.cursor()
        cursor.execute(self.__SQL_GET_LOCATIONS_BY_TEAM_ID % team_id)
        data = cursor.fetchall()
        if data is not None:
            db.close()
            return data
        else:
            db.close()
            return "No result"

    def get_team_last_3_purchases(self, team_id):
        db = pymysql.connect(**self.config)
        cursor = db.cursor()
        cursor.execute(self.__SQL_GET_TEAM_LAST_3_PURCHASES % team_id)
        data = cursor.fetchall()
        db.close()
        return data

    def get_location_info(self, location_id):
        db = pymysql.connect(**self.config)
        cursor = db.cursor()
        cursor.execute(self.__SQL_GET_LOCATION_INFO % location_id)
        data = cursor.fetchone()
        db.close()
        return data

    def get_all_locations_info(self):
        db = pymysql.connect(**self.config)
        cursor = db.cursor()
        cursor.execute(self.__SQL_GET_ALL_LOCATIONS_INFO)
        data = cursor.fetchall()
        if data is not None:
            db.close()
            return data
        else:
            db.close()
            return None

    def get_all_teams_balance(self):
        db = pymysql.connect(**self.config)
        cursor = db.cursor()
        cursor.execute(self.__SQL_GET_ALL_TEAMS_BALANCE)
        data = cursor.fetchall()
        if data is not None:
            db.close()
            return data
        else:
            db.close()
            return None

    def get_team_transaction_time_on_location(self, team_id:int, location_id:int):
        sql = self.__SQL_GET_TRANSACTION_TIME_FOR_TEAM_ON_LOCATION % (team_id, location_id)
        db = pymysql.connect(**self.config)
        cursor = db.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        db.close()
        return len(data)

    def get_transaction_time_on_location(self, location_id:int):
        sql = self.__SQL_GET_TRANSACTION_TIME_ON_LOCATION % location_id
        db = pymysql.connect(**self.config)
        cursor = db.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        db.close()
        return len(data)

    def update_location_owner(self, location_id, team_id):
        sql = self.__SQL_UPDATE_LOCATION_OWNER % (team_id, location_id)
        db = pymysql.connect(**self.config)
        cursor = db.cursor()
        try:
            cursor.execute(sql)
            db.commit()
            db.close()
        except:
            db.rollback()
            db.close()
            return False

    def record_transaction_purchase(self, transaction_amount:int, from_team_id:int, to_team_id:int, location_id:int):
        sql = self.__SQL_INSERT_TRANSACTION_PURCHASE % (transaction_amount, from_team_id, to_team_id, location_id)
        db = pymysql.connect(**self.config)
        cursor = db.cursor()
        try:
            cursor.execute(sql)
            db.commit()
            db.close()
        except:
            db.rollback()
            db.close()
            return False

    def record_transaction_bonus(self, transaction_amount: int, to_team_id: int, location_id: int):
            sql = self.__SQL_INSERT_TRANSACTION_BONUS % (transaction_amount, to_team_id, location_id)
            db = pymysql.connect(**self.config)
            cursor = db.cursor()
            try:
                cursor.execute(sql)
                db.commit()
                db.close()
            except:
                db.rollback()
                db.close()
                return False

    def update_balance(self, team_id, new_balance):
        sql = self.__SQL_UPDATE_BALANCE_FOR_TEAM % (new_balance, team_id)
        print(sql)
        db = pymysql.connect(**self.config)
        cursor = db.cursor()
        try:
            cursor.execute(sql)
            db.commit()
            db.close()
        except:
            db.rollback()
            db.close()
            return False