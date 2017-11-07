from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from datetime import datetime
from math import floor
from .model import Model
from .settings import DEBUG
from .config import INITIAL_PRICE_FOR_RESET, INCREASE_RATE, INITIAL_TEAM_BALANCE_FOR_RESET,\
    GLOBAL_FIRST_PURCHASE_LOCATION_BONUS, TEAM_FIRST_PURCHASE_LOCATION_BONUS, START_TIME, PRICE_INCREASE_PERIOD_SECONDS,\
    ADMIN_PASSCODE_QUERY_PARAM, MESSAGE_NEED_ADMIN_PASSCODE


def set_static_locations_price_dict():
    locations_price_dict = {}
    mod = Model()
    all_locations_info = mod.get_all_locations_info()
    for i in range(len(all_locations_info)):
        location_dict = {}
        location_dict['location_id'] = all_locations_info[i]['location_id']
        location_dict['location_name'] = all_locations_info[i]['location_name']
        location_dict['location_price_list'] = [all_locations_info[i]['last_price']]
        for index in range(1, 16):
            location_dict['location_price_list'].append(
                floor(all_locations_info[i]['last_price'] * (1 + INCREASE_RATE) ** index))
        locations_price_dict[location_dict['location_id']] = location_dict
    return locations_price_dict


STATIC_LOCATIONS_PRICE_DICT = set_static_locations_price_dict()


def get_current_price(location_id):
    index = int((datetime.now() - START_TIME).total_seconds() // PRICE_INCREASE_PERIOD_SECONDS)
    return STATIC_LOCATIONS_PRICE_DICT[location_id]['location_price_list'][index]


@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
def get_team_balance(request):
    # sample = {
    #     "team_id": 2
    # }
    if request.method == "POST":
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
        team_id = request.data['team_id']
        mod = Model()
        return Response(mod.get_team_locations(team_id))
    elif DEBUG:
        return Response({"Sample post data": {"team_id": 1}})


@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
def get_locations_price(request):
    if request.method == "GET":
        mod = Model()
        response = mod.get_all_locations_info()
        response_reduced = []
        for i in range(len(response) - 1):
            response_reduced.append({
                "location_id": response[i]['location_id'],
                "location_name": response[i]['location_name'],
                "current_price": get_current_price(i + 1)
            })
        return Response(response_reduced)
    else:
        return Response("Only support get")


@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
def get_teams_last_3_checkpoints(request):
    pass
    if request.method == "GET":
        mod = Model()
        all_teams = mod.get_all_teams_balance()
        response_reduced = []
        for i in range(len(all_teams) - 1):
            team_last_3_checkpoints = mod.get_team_last_3_purchases(all_teams[i]['team_id'])
            response_reduced.append({
                "team_id": all_teams[i]['team_id'],
                "last_3_checkpoints": team_last_3_checkpoints
            })
        return Response(response_reduced)
    else:
        return Response("Only support get")


@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
def buy_location(request):
    # sample = {
    #   "team_id": 1,
    #   "location_id": 2,
    # }
    if request.method == "POST":
        buyer_team_id = request.data['team_id']
        location_id = request.data['location_id']
        mod = Model()
        location_info = mod.get_location_info(location_id)

        # New price rule
        current_price = get_current_price(location_id)
        location_owner_id = location_info['current_owner_id']
        buyer_team_balance = mod.get_team_balance(buyer_team_id)['current_balance']
        location_owner_balance = mod.get_team_balance(location_owner_id)['current_balance']

        # Condition 1: Owned by self
        if location_owner_id == buyer_team_id:
            return Response({
                "status": 1,
                "message": "Cannot by from self.",
                "balance": buyer_team_balance
            })
        # Condition 2: No enough balance
        elif buyer_team_balance < current_price:
            return Response({
                "status": 2,
                "message": "Buyer has insufficient balance.",
                "balance": buyer_team_balance
            })
        # Condition 3: Exceed transaction limit
        elif mod.get_team_transaction_time_on_location(buyer_team_id, location_id) >= 3:
            return Response({
                "status": 3,
                "message": "Buyer has reached transaction limit on location " + str(location_id),
                "balance": buyer_team_balance
            })
        else:
            # This branch indicates successful purchasing
            # TODO: check bonus condition
            bonus = 0
            if mod.get_team_transaction_time_on_location(buyer_team_id, location_id) == 0:
                bonus += TEAM_FIRST_PURCHASE_LOCATION_BONUS
                mod.record_transaction_bonus(TEAM_FIRST_PURCHASE_LOCATION_BONUS, buyer_team_id, location_id)
            if mod.get_transaction_time_on_location(location_id) == 0:
                bonus += GLOBAL_FIRST_PURCHASE_LOCATION_BONUS
                mod.record_transaction_bonus(GLOBAL_FIRST_PURCHASE_LOCATION_BONUS, buyer_team_id, location_id)

            # Reduce balance from team_id and add bonus
            mod.update_balance(buyer_team_id, buyer_team_balance - current_price + bonus)

            # Add price to location owner
            mod.update_balance(location_owner_id, location_owner_balance + current_price)

            # Update location owner and do not increase location price
            mod.update_location_owner(location_id, buyer_team_id)

            # Record transaction
            mod.record_transaction_purchase(current_price, location_owner_id, buyer_team_id, location_id)

            return Response(
                {
                    "status": 0,
                    "message": 'Purchase successful.',
                    "bonus": bonus,
                    "balance": buyer_team_balance - current_price + bonus,
                }
            )
    elif DEBUG:
        return Response({"Sample post data": {"team_id": 1, "location_id": 2}})


@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
def get_locations_status(request):
    # sample = {
    #     "sessionId": 1
    # }
    if request.method == "GET":
        if request.query_params:
            if request.query_params['passcode'] != ADMIN_PASSCODE_QUERY_PARAM:
                return Response("Passcode: " + request.query_params['passcode'] + " not valid")
            mod = Model()
            response = mod.get_all_locations_info()
            for i in range(len(response) - 1):
                response[i]['current_price'] = get_current_price(i + 1)
            return Response(response)
        else:
            return Response(MESSAGE_NEED_ADMIN_PASSCODE)
    else:
        return Response("Only support get")


@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
def get_all_teams_balance(request):
    if request.method == "GET":
        if request.query_params:
            if request.query_params['passcode'] != ADMIN_PASSCODE_QUERY_PARAM:
                return Response("Passcode: " + request.query_params['passcode'] + " not valid")
            mod = Model()
            response = mod.get_all_teams_balance()
            return Response(response)
        else:
            return Response(MESSAGE_NEED_ADMIN_PASSCODE)
    else:
        return Response("Only support get")


@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
def admin_reset(request):
    #Very dangerous, will reset DB and runtime data according to config
    #No one should use it after game starts
    global STATIC_LOCATIONS_PRICE_DICT
    if request.method == "GET":
        if request.query_params:
            if request.query_params['passcode'] != ADMIN_PASSCODE_QUERY_PARAM:
                return Response("Passcode: " + request.query_params['passcode'] + " not valid")
            mod = Model()
            if mod.admin_reset_teams_and_locations(INITIAL_TEAM_BALANCE_FOR_RESET, INITIAL_PRICE_FOR_RESET):
                STATIC_LOCATIONS_PRICE_DICT = set_static_locations_price_dict()
                return Response("Reset successful")
            else:
                return Response("Reset failed")
        else:
            return Response(MESSAGE_NEED_ADMIN_PASSCODE)
    else:
        return Response("Only support GET")
