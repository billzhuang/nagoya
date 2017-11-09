from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from datetime import datetime
from math import floor
from .model import Model
from .settings import DEBUG
from .config import INITIAL_PRICE_FOR_RESET, INCREASE_RATE, INITIAL_TEAM_BALANCE_FOR_RESET, \
    GLOBAL_FIRST_PURCHASE_LOCATION_BONUS, TEAM_FIRST_PURCHASE_LOCATION_BONUS, START_TIME, PRICE_INCREASE_PERIOD_SECONDS, \
    ADMIN_PASSCODE_QUERY_PARAM, MESSAGE_NEED_ADMIN_PASSCODE, END_INCREASE_RATE, RESPONSE_INVALID_PASSCODE


def set_static_locations_price_dict():
    locations_price_dict = {}
    mod = Model()
    all_locations_info = mod.get_all_locations_info()
    for i in range(len(all_locations_info)):
        location_dict = {}
        location_dict['location_id'] = all_locations_info[i]['location_id']
        location_dict['location_name'] = all_locations_info[i]['location_name']
        location_dict['location_price_list'] = [all_locations_info[i]['last_price']]
        for index in range(1, 14):
            location_dict['location_price_list'].append(
                floor(all_locations_info[i]['last_price'] * (1 + INCREASE_RATE) ** index))
        location_dict['location_price_list'].append(floor(location_dict['location_price_list'][-1]
                                                          * (1 + END_INCREASE_RATE)))
        locations_price_dict[location_dict['location_id']] = location_dict
    return locations_price_dict


STATIC_LOCATIONS_PRICE_DICT = set_static_locations_price_dict()


def get_current_price(location_id, time_slot_id=None):
    if time_slot_id is None:
        index = int((datetime.now() - START_TIME).total_seconds() // PRICE_INCREASE_PERIOD_SECONDS)
    else:
        index = time_slot_id
    return STATIC_LOCATIONS_PRICE_DICT[location_id]['location_price_list'][index]


def get_team_id_by_passcode(team_passcode):
    mod = Model()
    team_id_dict = mod.get_team_id_by_passcode(team_passcode)
    if (team_id_dict is not None):
        return team_id_dict["team_id"]
    else:
        return None


@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
def get_team_balance(request):
    # sample = {
    #     "team_passcode": "2"
    # }
    if request.method == "POST":
        team_id = get_team_id_by_passcode(request.data['team_passcode'])
        if (team_id is None):
            return Response(RESPONSE_INVALID_PASSCODE)
        mod = Model()
        return Response(mod.get_team_balance(team_id))
    elif DEBUG:
        return Response({"Sample post data": {"team_id": 1}})


@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
def get_team_locations(request):
    # sample = {
    #     "team_passcode": "2"
    # }
    if request.method == "POST":
        team_id = get_team_id_by_passcode(request.data['team_passcode'])
        if (team_id is None):
            return Response(RESPONSE_INVALID_PASSCODE)
        mod = Model()
        return Response(mod.get_team_locations(team_id))
    elif DEBUG:
        return Response({"Sample post data": {"team_id": 1}})


@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
def get_team_transaction_records(request):
    # sample = {
    #     "team_passcode": "2"
    # }
    # Transaction time is the operation time

    if request.method == "POST":
        team_id = team_id = get_team_id_by_passcode(request.data['team_passcode'])
        if (team_id is None):
            return Response(RESPONSE_INVALID_PASSCODE)
        mod = Model()
        response = mod.get_team_transaction_records(team_id)

        # Hide transaction "to id" and determine transaction direction
        response_hide_to_id = []
        for i in range(len(response)):
            response_hide_to_id.append({
                "transaction_type": "SELL" if (team_id != response[i]['transaction_from_id']
                                               and 0 != response[i]['transaction_from_id'])
                else response[i]['transaction_type'],
                "transaction_amount": -response[i]['transaction_amount'] if (
                    team_id == response[i]['transaction_from_id'] and response[i]['transaction_type'] == 'PURCHASE')
                else response[i]['transaction_amount'],
                "transaction_location_id": response[i]['transaction_location_id'],
                "location_name": response[i]['location_name'],
                "transaction_time": response[i]['transaction_time'].time()
            })
        return Response(response_hide_to_id)
    elif DEBUG:
        return Response({"Sample post data": {"team_id": 1}})


@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
def get_locations_price(request):
    if request.method == "GET":
        mod = Model()
        response = mod.get_all_locations_info()
        response_reduced = []
        for i in range(len(response)):
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
                "team_leader": all_teams[i]['team_leader'],
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
    #   "time_slot_id": 0,
    # }
    if request.method == "POST":
        buyer_team_id = request.data['team_id']
        location_id = request.data['location_id']
        time_slot_id = None

        if request.data['time_slot_id'] >= 0:
            time_slot_id = request.data['time_slot_id']

        mod = Model()
        location_info = mod.get_location_info(location_id)

        # New price rule
        current_price = get_current_price(location_id, time_slot_id)
        location_owner_id = location_info['current_owner_id']
        buyer_team_balance = mod.get_team_balance(buyer_team_id)['current_balance']
        location_owner_balance = mod.get_team_balance(location_owner_id)['current_balance']

        # Condition 1: Owned by self
        if location_owner_id == buyer_team_id:
            return Response({
                "status": 1,
                "message": "Cannot buy from self.",
                "bonus": 0,
                "price": 0,
                "balance": buyer_team_balance
            })
        # Condition 2: No enough balance
        elif buyer_team_balance < current_price:
            return Response({
                "status": 2,
                "message": "Buyer has insufficient fund.",
                "bonus": 0,
                "price": 0,
                "balance": buyer_team_balance
            })
        # Condition 3: Exceed transaction limit
        elif mod.get_team_transaction_time_on_location(buyer_team_id, location_id) >= 3:
            return Response({
                "status": 3,
                "message": "Buyer has reached transaction limit on location " + str(location_id),
                "bonus": 0,
                "price": 0,
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
            mod.record_transaction_purchase(current_price, buyer_team_id, location_owner_id, location_id)

            return Response(
                {
                    "status": 0,
                    "message": 'Purchase successful.',
                    "bonus": bonus,
                    "price": current_price,
                    "balance": buyer_team_balance - current_price + bonus,
                }
            )
    elif DEBUG:
        return Response({"Sample post data(set time_slot_id to -1 if not required)": {"team_id": 1, "location_id": 2,
                                                                                      "time_slot_id": 0}})


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
            for i in range(len(response)):
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
def get_game_end_scores(request):
    if request.method == "GET":
        if request.query_params:
            if request.query_params['passcode'] != ADMIN_PASSCODE_QUERY_PARAM:
                return Response("Passcode: " + request.query_params['passcode'] + " not valid")

            response = []
            for team_id in range(1, 15):
                mod = Model()
                end_balance = mod.get_team_balance(team_id)["current_balance"]
                locations_value = 0
                locations_dict_list = mod.get_team_locations(team_id)
                owned_locations = []
                for locations_index in range(len(locations_dict_list)):
                    location_name = locations_dict_list[locations_index]["location_name"]
                    location_end_value = get_current_price(locations_dict_list[locations_index]["location_id"], -1)
                    owned_locations.append({
                        "location_name": location_name,
                        "location_end_value": location_end_value
                    })
                    locations_value += location_end_value
                response.append({
                    "team_id": team_id,
                    "end_balance": end_balance,
                    "owned_locations": owned_locations,
                    "locations_value": locations_value,
                    "total_score": end_balance + locations_value
                })
            return Response(response)
        else:
            return Response(MESSAGE_NEED_ADMIN_PASSCODE)
    else:
        return Response("Only support get")


@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
def admin_reset(request):
    # Very dangerous, will reset DB and runtime data according to config
    # No one should use it after game starts
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
