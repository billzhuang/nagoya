#FOR initialize db


SQL_INIT_LOCATIONS = "INSERT INTO `nagoya`.`locations` (`location_id`, `location_name`, `current_owner_id`, `current_toll_price`, `current_price`) VALUES ('1', 'Nagoya Castle', '0', '100', '1000');" \
                     "INSERT INTO `nagoya`.`locations` (`location_name`, `current_owner_id`, `current_toll_price`, `current_price`) VALUES ('Nagoya TV Tower', '0', '100', '1000');" \
                     "INSERT INTO `nagoya`.`locations` (`location_name`, `current_owner_id`, `current_toll_price`, `current_price`) VALUES ('Oasis 21', '0', '100', '1000');" \
                     "INSERT INTO `nagoya`.`locations` (`location_name`, `current_owner_id`, `current_toll_price`, `current_price`) VALUES ('Tokugawa Park', '0', '100', '1000');" \
                     "INSERT INTO `nagoya`.`locations` (`location_name`, `current_owner_id`, `current_toll_price`, `current_price`) VALUES ('Shiroyamahachimangu', '0', '100', '1000');" \
                     "INSERT INTO `nagoya`.`locations` (`location_name`, `current_owner_id`, `current_toll_price`, `current_price`) VALUES ('Tamotsu Chiyo Inari Shrine', '0', '100', '1000');" \
                     "INSERT INTO `nagoya`.`locations` (`location_name`, `current_owner_id`, `current_toll_price`, `current_price`) VALUES ('Kosho ji', '0', '100', '1000');" \
                     "INSERT INTO `nagoya`.`locations` (`location_name`, `current_owner_id`, `current_toll_price`, `current_price`) VALUES ('Osu Kannon', '0', '100', '1000');" \
                     "INSERT INTO `nagoya`.`locations` (`location_name`, `current_owner_id`, `current_toll_price`, `current_price`) VALUES ('Tsuruma Park', '0', '100', '1000');" \
                     "INSERT INTO `nagoya`.`locations` (`location_name`, `current_owner_id`, `current_toll_price`, `current_price`) VALUES ('Atsuta Jingu', '0', '100', '1000');" \
                     "INSERT INTO `nagoya`.`locations` (`location_name`, `current_owner_id`, `current_toll_price`, `current_price`) VALUES ('Shirotori Garden', '0', '100', '1000');"

SQL_INIT_TEAMS = "INSERT INTO `nagoya`.`teams` (`team_id`, `team_leader`, `current_balance`) VALUES ('0', 'BillZhuang', '0');" \
                 "INSERT INTO `nagoya`.`teams` (`team_id`, `team_leader`, `current_balance`) VALUES ('1', 'KarlGong', '3000');" \
                 "INSERT INTO `nagoya`.`teams` (`team_id`, `team_leader`, `current_balance`) VALUES ('2', 'TerrillYe', '3000');" \
                 "INSERT INTO `nagoya`.`teams` (`team_id`, `team_leader`, `current_balance`) VALUES ('3', 'EmmaDai', '3000');" \
                 "INSERT INTO `nagoya`.`teams` (`team_leader`, `current_balance`) VALUES ('WadeWang', '3000');" \
                 "INSERT INTO `nagoya`.`teams` (`team_leader`, `current_balance`) VALUES ('WenzhouZhang', '3000');" \
                 "INSERT INTO `nagoya`.`teams` (`team_leader`, `current_balance`) VALUES ('SevenGuo', '3000');" \
                 "INSERT INTO `nagoya`.`teams` (`team_leader`, `current_balance`) VALUES ('BiguiDIng', '3000');" \
                 "INSERT INTO `nagoya`.`teams` (`team_leader`, `current_balance`) VALUES ('ObbaZhou', '3000');" \
                 "INSERT INTO `nagoya`.`teams` (`team_leader`, `current_balance`) VALUES ('DaodaoChen', '3000');" \
                 "INSERT INTO `nagoya`.`teams` (`team_leader`, `current_balance`) VALUES ('CousinLi', '3000');" \
                 "INSERT INTO `nagoya`.`teams` (`team_leader`, `current_balance`) VALUES ('DapeiChen', '3000');"
