app = {
    SERVICE_URL: "http://nagoya.eflabs.life/api/",
    GET_TEAM_LOCATIONS: {
        "method": "POST",
        "url": "getteamlocations"
    },
    GET_TEAM_BALANCE: {
        "method": "POST",
        "url": "getteambalance"
    },
    GET_TEAM_LAST_CHECKPOINTS: {
        "method": "GET",
        "url": "getteamslast3checkpoints"
    },
    GET_TEAM_TRANSACTION_RECORDS: {
        "method": "POST",
        "url": "getteamtransactionrecords"
    },

    TEAM_PASSCODE: null,

    initialize: function() {
        var url = location.search;

        if (url.indexOf("?") != -1) {
            var str = url.substr(1);
            strs = str.split('team_passcode=');
            app.TEAM_PASSCODE = strs[1];
        }
        url = location.href;
        console.log(url);
        //need change to str

        if (url.indexOf("detail") != -1) {
            app.getTeamBalance(app.TEAM_PASSCODE);
            app.getTeamLocations(app.TEAM_PASSCODE);
            app.getTeamTransactionRecords(app.TEAM_PASSCODE);
        }
        if (url.indexOf("teams") != -1) {
            console.log("teams");
            app.getTeamLastCheckpoints();
        }

    },
    getTeamBalance: function(team_passcode) {
        $.ajax({
            type: app.GET_TEAM_BALANCE["method"],
            url: app.SERVICE_URL + app.GET_TEAM_BALANCE["url"],
            data: JSON.stringify({ "team_passcode": team_passcode }),
            success: function(data) {
                if ("status" in data) {
                    if (data["status"] == -1) {
                        app.showInvalidPasscodeMessage();
                    }
                } else {
                    app.updateTeamBalanceText(data);
                }
            },
            contentType: "application/json",
        });
    },
    getTeamLocations: function(team_passcode) {
        $.ajax({
            type: app.GET_TEAM_LOCATIONS["method"],
            url: app.SERVICE_URL + app.GET_TEAM_LOCATIONS["url"],
            data: JSON.stringify({ "team_passcode": team_passcode }),
            success: function(data) {
                if ("status" in data) {
                    if (data["status"] == -1) {
                        app.showInvalidPasscodeMessage();
                    }
                } else {
                    app.updateTeamLocationsList(data);
                }
            },
            contentType: "application/json",
        });
    },
    getTeamTransactionRecords: function(team_passcode) {
        $.ajax({
            type: app.GET_TEAM_TRANSACTION_RECORDS["method"],
            url: app.SERVICE_URL + app.GET_TEAM_TRANSACTION_RECORDS["url"],
            data: JSON.stringify({ "team_passcode": team_passcode }),
            success: function(data) {
                if ("status" in data) {
                    if (data["status"] == -1) {
                        app.showInvalidPasscodeMessage();
                    }
                } else {
                    app.updateTeamTransactionHistoryTable(data);
                }
            },
            contentType: "application/json",
        });
    },
    getTeamLastCheckpoints: function() {
        $.ajax({
            type: app.GET_TEAM_LAST_CHECKPOINTS["method"],
            url: app.SERVICE_URL + app.GET_TEAM_LAST_CHECKPOINTS["url"],
            data: null,
            success: function(data) {
                app.updateTeamsTable(data);
            },
            contentType: "application/json",
        })
    },

    showInvalidPasscodeMessage: function() {
        $(".content").hide();
        $(".container-fluid h3")[0].innerText = "Invalid passcode, please contact Bill Zhuang for instructions.";
    },

    updateTeamsTable: function(data) {
        console.log(data);
        var tbody = $("#teams-table-body");

        for (index in data) {
            if (index > 0) {
                var tr = $("<tr></tr>");
                var th = $("<th>Team " + data[index]["team_id"] + ": " + data[index]["team_leader"] + "</th>");
                th.appendTo(tr);

                var team_id = data[index]["team_id"];
                var checkpoint_list = data[index]["last_3_checkpoints"];
                for (i in [0, 1, 2]) {
                    if (checkpoint_list.length > i) {
                        var td = $("<td>" + checkpoint_list[i]['location_name'] + "</td>");
                    } else {
                        var td = $("<td>" + "N/A" + "</td>");
                    }

                    td.appendTo(tr);
                }
                $("#teams-table-body").append(tr);
            }

        }

    },
    updateTeamBalanceText: function(data) {
        console.log("balance text");
        console.log(data);
        var balance = data["current_balance"];
        $("#balance-value")[0].innerText = balance;
    },
    updateTeamLocationsList: function(data) {
        console.log("locations list");
        console.log(data);
        var ol = $("#locations-ol")[0];
        for (index in data) {
            var location_name = data[index]['location_name'];
            var li = $("<li>" + location_name + "</li>");
            li.appendTo(ol);
        }
        $("#li").append(ol);
    },
    updateTeamTransactionHistoryTable: function(data) {
        console.log(data);
        var tbody = $("#transactions-table-body");

        for (index in data) {

            var tr = $("<tr></tr>");
            var th = $("<th>" + data[index]["transaction_type"] + "</th>");
            th.appendTo(tr);
            var td_amount = $("<td>" + data[index]["transaction_amount"] + "</td>");
            var td_location = $("<td>" + data[index]["location_name"] + "</td>");
            //var td_time = $("<td>" + data[index]["transaction_time"] + "</td>");
            td_amount.appendTo(tr);
            td_location.appendTo(tr);
            //td_time.appendTo(tr);
            $("#transactions-table-body").append(tr);

        }

    },
}
