from django.conf.urls import url

from . import controller

urlpatterns = [
    #for team leaders
    url(r'getlocationsprice', controller.get_locations_price),
    url(r'getteamslast3checkpoints', controller.get_teams_last_3_checkpoints),
    url(r'getteambalance', controller.get_team_balance),
    url(r'getteamlocations', controller.get_team_locations),

    #for admin action
    url(r'buylocation', controller.buy_location),
    url(r'adminreset', controller.admin_reset),

    #for admin query
    url(r'getlocationsstatus', controller.get_locations_status),
    url(r'getteamsbalance', controller.get_all_teams_balance),
]
