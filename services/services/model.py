import pymysql.cursors
from datetime import datetime

class Model():
    config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': '',
        'db': 'nagoya',
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor,
    }
    #
    # __SQL_VALIDATE_USER_AND_PASSWORD = "SELECT user_id, user_name FROM USERS WHERE user_name='%s' AND user_password='%s';"
    # __SQL_GET_ALL_SESSIONS_BY_USER_ID = "SELECT session_id, session_name FROM SESSIONS WHERE created_by_user_id=%s;"
    # __SQL_GET_LINES_BY_SESSION_ID = "SELECT * FROM polylines WHERE session_id = %s;"
    # __SQL_GET_LAST_INCREMENT_ID = "SELECT MAX(line_id) FROM polylines;"
    # __SQL_GET_LAST_SESSION_ID = "SELECT MAX(session_id) FROM sessions;"
    # __SQL_CREATE_SESSION_BY_USER = "INSERT INTO sessions VALUES(NULL, '%s', %s, NULL, NULL)"
    # __SQL_CREATE_LINE_FOR_SESSION = "INSERT INTO polylines VALUES(NULL, %s, %s, '%s', NULL, NULL);"
    __SQL_GET_BALANCE_BY_TEAM_ID = "SELECT current_balance FROM teams WHERE team_id = %s;"
    __SQL_GET_LOCATIONS_BY_TEAM_ID = "SELECT location_id, location_name FROM locations WHERE current_owner_id = %s;"
    __SQL_GET_LOCATION_INFO = "SELECT location_name, last_price, last_updated_time, NOW()," \
                              "timediff(NOW(), last_updated_time) as hold_duration, current_owner_id " \
                              "FROM locations WHERE location_id = %s;"
    __SQL_GET_ALL_LOCATIONS_INFO = "SELECT location_name, last_price, last_updated_time, NOW()," \
                                   "timediff(NOW(), last_updated_time) as hold_duration, current_owner_id" \
                                   " FROM locations;"
    __SQL_GET_ALL_TEAMS_BALANCE = "SELECT team_id, current_balance FROM teams;"
    __SQL_UPDATE_BALANCE_FOR_TEAM = "UPDATE teams SET current_balance = %s WHERE team_id = %s;"
    __SQL_UPDATE_LOCATION_OWNER_AND_PRICE = "UPDATE locations SET current_owner_id = %s, last_price = %s," \
                                            " last_updated_time = NOW() WHERE location_id = %s;"

    #deprecated
    __SQL_UPDATE_LOCATION_TOLL_PRICE = "UPDATE teams SET last_updated_time = %s WHERE location_id = %s;"

    __SQL_RESET_LOCATIONS_OWNER_AND_PRICE = "UPDATE locations SET current_owner_id = 0, last_updated_time = %s, last_price = %s WHERE location_id < 200;"
    __SQL_RESET_TEAMS_BALANCE = "UPDATE teams SET current_balance = %s WHERE team_id < 200;"

#TODO:
    # 1. Review all functions
    # 2. Update buy actions
    # 3. Test API
    # 4. Do page

    def get_number_of_interest_periods(self, start_time:datetime, end_time:datetime):
        return (end_time.hour - start_time.hour) * 2 - (start_time.minute // 30) + (end_time.minute // 30) + 1

    def admin_reset_teams_and_locations(self, initial_team_balance, initial_updated_time, initial_price):
        sql_reset_locations = self.__SQL_RESET_LOCATIONS_OWNER_AND_PRICE % (initial_updated_time, initial_price)
        sql_reset_teams_balance = self.__SQL_RESET_TEAMS_BALANCE % initial_team_balance

        print(sql_reset_locations)
        print(sql_reset_teams_balance)

        db = pymysql.connect(**self.config)
        cursor = db.cursor()
        try:
            # 执行sql语句
            cursor.execute(sql_reset_locations)
            # 提交到数据库执行
            db.commit()
            # 执行sql语句
            cursor.execute(sql_reset_teams_balance)
            # 提交到数据库执行
            db.commit()
            db.close()
            return True

        except:
            # Rollback in case there is any error
            db.rollback()
            db.close()
            return False

    def get_team_balance(self, team_id):
        db = pymysql.connect(**self.config)
        cursor = db.cursor()
        cursor.execute(self.__SQL_GET_BALANCE_BY_TEAM_ID % team_id)
        data = cursor.fetchone()
        print(data)
        db.close()
        return data

    def get_team_locations(self, team_id):
        db = pymysql.connect(**self.config)
        cursor = db.cursor()
        cursor.execute(self.__SQL_GET_LOCATIONS_BY_TEAM_ID % team_id)
        data = cursor.fetchall()
        if data is not None:
            print(data)
            db.close()
            return data
        else:
            return "No result"

    def get_location_info(self, location_id):
        db = pymysql.connect(**self.config)
        cursor = db.cursor()
        cursor.execute(self.__SQL_GET_LOCATION_INFO % location_id)
        data = cursor.fetchone()
        data["number_of_interest_periods"] = self.get_number_of_interest_periods(
            data['last_updated_time'], data['NOW()'])

        print(data)
        db.close()
        return data

    def get_all_locations_info(self):
        db = pymysql.connect(**self.config)
        cursor = db.cursor()
        cursor.execute(self.__SQL_GET_ALL_LOCATIONS_INFO)
        data = cursor.fetchall()
        if data is not None:

            db.close()
            for i in range(len(data)):
                data[i]["number_of_interest_periods"] = self.get_number_of_interest_periods(
                    data[i]['last_updated_time'], data[i]['NOW()'])
            print(data)
            return data
        else:
            return None

    def get_all_teams_balance(self):
        db = pymysql.connect(**self.config)
        cursor = db.cursor()
        cursor.execute(self.__SQL_GET_ALL_TEAMS_BALANCE)
        data = cursor.fetchall()
        if data is not None:
            print(data)
            db.close()
            return data
        else:
            return None

    def update_location_owner_and_price(self, location_id, team_id, new_price):
        sql = self.__SQL_UPDATE_LOCATION_OWNER_AND_PRICE % (team_id, new_price, location_id)
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

    def update_location_toll_price(self, location_id, new_price):
        sql = self.__SQL_UPDATE_LOCATION_TOLL_PRICE % (new_price, location_id)
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


#
mod = Model()
# print(mod.get_team_locations(1))
print(mod.get_all_locations_info())
# info = mod.get_location_info(1)
# start_time = info['last_updated_time']
# end_time = info['NOW()']
# print(mod.get_number_of_interest_periods(start_time, end_time))
# start_time = datetime(2017,11,5,11,30,24)
# end_time = datetime(2017,11,5,11,32,24)
# print(mod.get_number_of_interest_periods(start_time,end_time))
# print(mod.get_all_locations_info())
# print(mod.get_all_teams_balance())
# print(mod.update_balance(0, 1000))
# print(mod.update_balance(1, 2000))
# print(mod.update_location_owner_and_price(1, 1, 1100))
# print(mod.get_balance(0))
# print(mod.get_locations(1))
# print(mod.get_location_info(1))
# print(mod.get_locations(0))
# print(mod.get_all_teams_balance())
# mod.get_lines_by_session_id(0)
# mod.create_line_for_session_user(0,0,"test")
