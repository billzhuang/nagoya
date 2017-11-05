from django.conf.urls import url

from . import controller

urlpatterns = [
    url(r'getteambalance', controller.get_team_balance),
    url(r'getteamlocations', controller.get_team_locations),
    url(r'buylocation', controller.buy_location),
    #url(r'paytoll', controller.pay_toll),
    url(r'getlocationsstatus', controller.get_locations_status),
    url(r'getteamsbalance', controller.get_all_teams_balance),
    url(r'adminreset', controller.admin_reset),
]
