var app = {
    SERVICE_URL: "http://127.0.0.1:8000/",
    BUY_LOCATION: {
        "method": "POST",
        "url": "buylocation"
    },
    GET_LOCATIONS_STATUS: {
        "method": "GET",
        "url": "/getlocationsstatus?passcode=Hikari"
    },

    initialize: function() {
        $("#btn-buy-location").click(function() {
            console.log("buy clicked");
            data = {
                "team_id": parseInt($("#team-id-dropdown select")[0].value),
                "location_id": parseInt($("#location-id-dropdown select")[0].value),
                "time_slot_id": parseInt($("#time-slot-id-dropdown select")[0].value)
            };
            selected_text = {
                "team_text": $("#team-id-dropdown select")[0].selectedOptions[0].text,
                "location_text": $("#location-id-dropdown select")[0].selectedOptions[0].text,
                "time_slot_text": $("#time-slot-id-dropdown select")[0].selectedOptions[0].text,
            };
            console.log(data);
            app.showConfirmationDialog(data, selected_text);
        });
    },

    showConfirmationDialog: function(data, selected_text) {
        BootstrapDialog.show({
            title: "Purchase Confirmation",
            message: "Buy location " + selected_text['location_text'] + " for team " + selected_text['team_text'] + " in time slot " + selected_text["time_slot_text"] + ", CONFIRM?",
            buttons: [{
                label: "CONFIRM",
                cssClass: "btn-primary",
                action: function(dialogItself) {
                    //alert(JSON.stringify(data));
                    app.buyLocation(data);
                    dialogItself.close();
                }
            }, {
                label: 'Close',
                action: function(dialogItself) {
                    dialogItself.close();
                }
            }]
        });
    },

    buyLocation: function(data) {
        $.ajax({
            type: app.BUY_LOCATION["method"],
            url: app.SERVICE_URL + app.BUY_LOCATION["url"],
            data: JSON.stringify(data),
            success: function(data) {
                message_text = data['message'];
                if (data['price'] > 0) {
                    message_text += (" Price: " + data['price'].toString() + ".");
                }
                if (data['bonus'] > 0) {
                    message_text += (" Bonus: " + data['bonus'].toString() + ".");
                }
                message_text += (" Latest balance: " + data['balance'].toString() + ".");
                app.showMessage(message_text);
            },
            contentType: "application/json",
        });
    },

    showMessage: function(message) {
        BootstrapDialog.show({
            title: "Purchase Result",
            message: message
        });
    },


};