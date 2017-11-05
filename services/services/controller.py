from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from .model import Model
from .settings import DEBUG

INITIAL_PRICE = 1000
INITIAL_TOLL_PRICE = 100
INITIAL_TEAM_BALANCE = 3000

INCREASE_AMOUNT = 100
INCREASE_TOLL_AMOUNT = 100

INCREASE_RATE = 0.1

@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
def admin_reset(request):
    if request.method == "GET":
        mod = Model()
        if mod.admin_reset_teams_and_locations(INITIAL_TEAM_BALANCE, INITIAL_TOLL_PRICE, INITIAL_PRICE):
            return Response("Reset successful")
        else:
            return Response("Reset failed")


# @api_view(['GET', 'POST'])
# @permission_classes((permissions.AllowAny,))
# def login(request):
#     # sample = {
#     #     "userName": "DaKai",
#     #     "password": "pass"
#     # }
#
#     if request.method == "POST":
#         user_name = request.data['userName']
#         password = request.data['password']
#         mod = Model()
#         # TODO: Get post data and pass to validation
#         return Response(mod.validate_login_info(user_name, password))
#     else:
#         return Response("Only support post")


@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
def get_team_balance(request):
    # sample = {
    #     "team_id": 2
    # }
    if request.method == "POST":
        # TODO: get balance for team id
        team_id = request.data['team_id']
        mod = Model()
        return Response(mod.get_team_balance(team_id))
    elif DEBUG:
        return Response({"Sample post data": {"team_id": 1}})


@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
def get_team_locations(request):
    # sample = {
    #     "team_id": 1
    # }
    if request.method == "POST":
        # TODO: get balance for team id
        team_id = request.data['team_id']
        mod = Model()
        return Response(mod.get_team_locations(team_id))
    elif DEBUG:
        return Response({"Sample post data": {"team_id": 1}})


@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
def buy_location(request):
    # sample = {
    #   "team_id": 1,
    #   "location_id": 2,
    # }
    if request.method == "POST":
        # TODO 1: Get purchase price for location and current team balance
        buyer_team_id = request.data['team_id']
        location_id = request.data['location_id']
        mod = Model()
        location_info = mod.get_location_info(location_id)
        current_price = location_info['last_price'] * ((1 + INCREASE_RATE) ** location_info['number_of_interest_periods'])
        location_owner_id = location_info['current_owner_id']
        buyer_team_balance = mod.get_team_balance(buyer_team_id)['current_balance']
        location_owner_balance = mod.get_team_balance(location_owner_id)['current_balance']

        # TODO 2: Reduce balance from team_id
        mod.update_balance(buyer_team_id, buyer_team_balance - current_price)

        # TODO 3: Add price to location owner
        mod.update_balance(location_owner_id, location_owner_balance + current_price)

        # TODO 4: Update location owner and increase location price and toll price
        mod.update_location_owner_and_price(location_id, buyer_team_id, current_price)

        return Response(
            {
                "status": 0,
                "balance": buyer_team_balance - current_price
            }
        )
    elif DEBUG:
        return Response({"Sample post data": {"team_id": 1, "location_id": 2}})


@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
def pay_toll(request):
    ### deprecated
    # sample = {
    #   "team_id": 1,
    #   "location_id": 2,
    # }


    if request.method == "POST":
        # TODO 1: Get toll price for location
        buyer_team_id = request.data['team_id']
        location_id = request.data['location_id']
        mod = Model()
        toll_price = mod.get_location_info(location_id)['current_toll_price']
        location_owner_id = mod.get_location_info(location_id)['current_owner_id']

        buyer_team_balance = mod.get_team_balance(buyer_team_id)['current_balance']
        location_owner_balance = mod.get_team_balance(location_owner_id)['current_balance']

        # TODO 2: Reduce balance from team_id
        mod.update_balance(buyer_team_id, buyer_team_balance - toll_price)

        # TODO 3: Add price to location owner
        mod.update_balance(location_owner_id, location_owner_balance + toll_price)

        # TODO 4: Update toll price
        new_toll_price = toll_price + INCREASE_TOLL_AMOUNT
        mod.update_location_toll_price(location_id, new_toll_price)

        return Response(
            {
                "status": 0,
                "balance": buyer_team_balance - toll_price
            })
    elif DEBUG:
        return Response({"Sample post data": {"team_id": 1, "location_id": 2}})


@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
def get_locations_status(request):
    # sample = {
    #     "sessionId": 1
    # }
    if request.method == "GET":
        if str(request.query_params) is not None:
            token = request.query_params
            # TODO: validate admin token from query params
            mod = Model()
            response = mod.get_all_locations_info()
            for i in range(len(response)):
                response[i]['current_price'] = response[i]['last_price'] * ((1 + INCREASE_RATE) ** response[i]['number_of_interest_periods'])
            return Response(response)
        else:
            return Response("Not authorized")
    else:
        return Response("Only support get")


@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
def get_all_teams_balance(request):
    # sample = {
    #     "sessionId": 1
    # }
    if request.method == "GET":
        if str(request.query_params) is not None:
            token = request.query_params
            # TODO: validate admin token from query params
            mod = Model()
            response = mod.get_all_teams_balance()
            return Response(response)
        else:
            return Response("Not authorized")
    else:
        return Response("Only support get")
