
function update_status(data) {
    $.each(data["memory"], function (key, val) {
        var m = parseFloat(val / 1000).toFixed(2);
        $("#" + key).text(m + 'k');
    });
    $.each(data["network"], function (key, val) {
        $("#" + key).text(val);
    });
}

function create_polygon(id) {
    var polygon = $("#" + id);
    var sides = 6;
    var radius = 5;
    var angle = 2 * Math.PI / sides;
    var points = [];

    for (var i = 0; i < sides; i++) {
        points.push(radius + radius * Math.sin(i * angle));
        points.push(radius - radius * Math.cos(i * angle));
    }

    polygon[0].setAttribute("points", points);
}

function update_gpio(data) {
    var res = "";
    $.each(data["pins"], function (key, val) {
        var state = "Off";
        var btn = "<button type='button' class='btn btn-success' act=1 pin=" + val["gpio"] + ">Turn On</button>";
        if (val["value"] != "0") {
            state = "On";
            btn = "<button type='button' class='btn btn-secondary' act=0 pin=" + val["gpio"] + ">Turn Off</button>";
        }
        res += "<tr><td>" + val["gpio"] + "</td>";
        res += "<td>" + val["nodemcu"] + "</td>";
        res += "<td>" + state + "</td>";
        res += "<td class='text-center'>" + btn + "</tr>";
    });
    // update table rows
    $("#gpio_rows").html(res);
    // handle button click event
    $("button[pin]").click(function (e) {
        e.preventDefault();
        // Send RESTApi request to change port status
        $.ajax({
            url: "/api/gpio/" + $(this).attr("pin"),
            type: "PUT",
            // contentType: 'application/json',
            data: { "value": $(this).attr("act") },
            success: function (result) {
                // on success - reload table
                console.log(result);
                on_hash_change();
            },
            error: function (xhr, resp, text) {
                console.log(method, uri, resp, text);
            }
        })
    });
}

function poll_led_matrix() {
    $.ajax({
        url: "/api/leds",
        type: "GET",
        // contentType: 'application/json',
        success: update_test_led_matrix,
        error: function (xhr, resp, text) {
            console.log(method, uri, resp, text);
        }
    })
}
let matrixCreated = false;
function update_test_led_matrix(data) {
    var res = "";
    if (!matrixCreated) {
        matrixCreated = true;
        var ledIndex = 0;
        for (var i = 0; i < data.rows; i++) {
            res += "<tr>";
            for (var j = 0; j < data.columns; j++) {
                res += "<td><svg width='12' height='12'><polygon id='led_matrix" + ledIndex + "'  /></td>";
                ledIndex += 1;
            }
            res += "</tr>";
        }
        // update table rows
        $("#led_matrix").html(res);
        ledIndex = 0;
        for (var i = 0; i < data.rows; i++) {
            for (var j = 0; j < data.columns; j++) {
                create_polygon('led_matrix' + ledIndex);
                ledIndex += 1;
            }
        }
    }

    for (var i = 0; i < data.matrix.length; i++) {
        let color =  "#" + data.matrix[i].toString(16).padStart(6, '0'); 
        $('#led_matrix' + i).css({fill: color});
    }
}

function update_buttons() {
    var lightsOn = false;
    $("#lights").click(function (e) {
        e.preventDefault();
        // Send RESTApi request to change port status
        $.ajax({
            url: "/api/lights",
            type: "PUT",
            // contentType: 'application/json',
            success: function (result) {
                // on success - reload table
                console.log(result);
                on_hash_change();
            },
            error: function (xhr, resp, text) {
                console.log(method, uri, resp, text);
            }
        })
    });
    $("#webserverRestart").click(function (e) {
        e.preventDefault();
        // Send RESTApi request to change port status
        $.ajax({
            url: "/api/computer/restart",
            type: "POST",
            // contentType: 'application/json',
            success: function (result) {
                // on success - reload table
                console.log(result);
                on_hash_change();
            },
            error: function (xhr, resp, text) {
                console.log(method, uri, resp, text);
            }
        })
    })
    $("#webserverOff").click(function (e) {
        e.preventDefault();
        // Send RESTApi request to change port status
        $.ajax({
            url: "/api/computer/shutdown",
            type: "POST",
            // contentType: 'application/json',
            success: function (result) {
                // on success - reload table
                console.log(result);
                on_hash_change();
            },
            error: function (xhr, resp, text) {
                console.log(method, uri, resp, text);
            }
        })
    });
    $("#restartRos").click(function (e) {
        e.preventDefault();
        // Send RESTApi request to change port status
        $.ajax({
            url: "/api/computer/restart_ros",
            type: "POST",
            // contentType: 'application/json',
            success: function (result) {
                // on success - reload table
                console.log(result);
                on_hash_change();
            },
            error: function (xhr, resp, text) {
                console.log(method, uri, resp, text);
            }
        })
    });
    $("#raceWNR").click(function (e) {
        e.preventDefault();
        // Send RESTApi request to change port status
        $.ajax({
            url: "/api/race/wnr",
            type: "POST",
            // contentType: 'application/json',
            success: function (result) {
                // on success - reload table
                console.log(result);
            },
            error: function (xhr, resp, text) {
                console.log(method, uri, resp, text);
            }
        })
    });
    
    $("#showOrder").click(function (e) {
        e.preventDefault();
        // Send RESTApi request to change port status
        $.ajax({
            url: "/api/race/show_order",
            type: "POST",
            // contentType: 'application/json',
            success: function (result) {
                // on success - reload table
                console.log(result);
            },
            error: function (xhr, resp, text) {
                console.log(method, uri, resp, text);
            }
        })
    });
    $("#raceBegin").click(function (e) {
        e.preventDefault();
        // Send RESTApi request to change port status
        $.ajax({
            url: "/api/race/begin_race",
            type: "POST",
            data: $("#prestartTime").val(),
            // contentType: 'application/json',
            success: function (result) {
                // on success - reload table
                console.log(result);
            },
            error: function (xhr, resp, text) {
                console.log(method, uri, resp, text);
            }
        })
    });
    $("#raceDelay").click(function (e) {
        e.preventDefault();
        // Send RESTApi request to change port status
        $.post({
            url: "/api/race/delay",
            data: $("#delayTime").val(),
            // contentType: 'application/json',
            success: function (result) {
                // on success - reload table
                console.log(result);
            },
            error: function (xhr, resp, text) {
                console.log(method, uri, resp, text);
            }
        })
    });
    $("#showMessage").click(function (e) {
        e.preventDefault();
        // Send RESTApi request to change port status
        $.ajax({
            url: "/api/race/show_message",
            type: "POST",
            data: $("#txtMessage").val(),
            // contentType: 'application/json',
            success: function (result) {
                // on success - reload table
                console.log(result);
            },
            error: function (xhr, resp, text) {
                console.log(method, uri, resp, text);
            }
        })
    });
    $("#stopMessage").click(function (e) {
        e.preventDefault();
        // Send RESTApi request to change port status
        $.ajax({
            url: "/api/race/stop_message",
            type: "POST",
            data: $("#txtMessage").val(),
            // contentType: 'application/json',
            success: function (result) {
                // on success - reload table
                console.log(result);
            },
            error: function (xhr, resp, text) {
                console.log(method, uri, resp, text);
            }
        })
    });
    
    $("#anchorUp").click(function (e) {
        e.preventDefault();
        // Send RESTApi request to change port status
        $.ajax({
            url: "/api/anchor/up",
            type: "POST",
            // contentType: 'application/json',
            success: function (result) {
                // on success - reload table
                console.log(result);
            },
            error: function (xhr, resp, text) {
                console.log(method, uri, resp, text);
            }
        })
    });
    $("#anchorDown").click(function (e) {
        e.preventDefault();
        // Send RESTApi request to change port status
        $.ajax({
            url: "/api/anchor/down",
            type: "POST",
            // contentType: 'application/json',
            success: function (result) {
                // on success - reload table
                console.log(result);
            },
            error: function (xhr, resp, text) {
                console.log(method, uri, resp, text);
            }
        })
    });
    $("#anchorDisable").click(function (e) {
        e.preventDefault();
        // Send RESTApi request to change port status
        $.ajax({
            url: "/api/anchor/disabled",
            type: "POST",
            // contentType: 'application/json',
            success: function (result) {
                // on success - reload table
                console.log(result);
            },
            error: function (xhr, resp, text) {
                console.log(method, uri, resp, text);
            }
        })
    });
    $("#anchorHold").click(function (e) {
        e.preventDefault();
        // Send RESTApi request to change port status
        $.ajax({
            url: "/api/anchor/hold",
            type: "POST",
            // contentType: 'application/json',
            success: function (result) {
                // on success - reload table
                console.log(result);
            },
            error: function (xhr, resp, text) {
                console.log(method, uri, resp, text);
            }
        })
    });
    $("#anchorLock").click(function (e) {
        e.preventDefault();
        // Send RESTApi request to change port status
        $.ajax({
            url: "/api/anchor/lock",
            type: "POST",
            // contentType: 'application/json',
            success: function (result) {
                // on success - reload table
                console.log(result);
            },
            error: function (xhr, resp, text) {
                console.log(method, uri, resp, text);
            }
        })
    });
    $("#boatArm").click(function (e) {
        e.preventDefault();
        // //Send RESTApi request to change port status
        // $.ajax({
        //     url: "/api/boat/arm",
        //     type: "POST",
        //     // contentType: 'application/json',
        //     success: function (result) {
        //         // on success - reload table
        //         console.log(result);
        //     },
        //     error: function (xhr, resp, text) {
        //         console.log(method, uri, resp, text);
        //     }
        // })
        var armService = new ROSLIB.Service({
            ros : g_ros,
            name : '/mavros/cmd/arming',
            serviceType : 'mavros_msgs/CommandBool'
        });
    
        var request = new ROSLIB.ServiceRequest({
            value : true
        });
    
        armService.callService(request, function(result) {
            console.log('Result for service call on '
            + armService.name
            + ': '
            + result);
        });
    });
    $("#boatOldArm").click(function (e) {
        e.preventDefault();
        //Send RESTApi request to change port status
        $.ajax({
            url: "/api/boat/arm",
            type: "POST",
            // contentType: 'application/json',
            success: function (result) {
                // on success - reload table
                console.log(result);
            },
            error: function (xhr, resp, text) {
                console.log(method, uri, resp, text);
            }
        })
    });
    $("#boatDisarm").click(function (e) {
        e.preventDefault();
        // Send RESTApi request to change port status
        $.ajax({
            url: "/api/boat/disarm",
            type: "POST",
            // contentType: 'application/json',
            success: function (result) {
                // on success - reload table
                console.log(result);
            },
            error: function (xhr, resp, text) {
                console.log(method, uri, resp, text);
            }
        })
    });
    $("#hornTest").click(function (e) {
        e.preventDefault();
        // Send RESTApi request to change port status
        $.ajax({
            url: "/api/boat/horn",
            type: "POST",
            // contentType: 'application/json',
            success: function (result) {
                // on success - reload table
                console.log(result);
            },
            error: function (xhr, resp, text) {
                console.log(method, uri, resp, text);
            }
        })
    });
    $("#singleClass").click(function (e) {
        e.preventDefault();
        // Send RESTApi request to change port status
        console.warn( $("#singleClassData").val());
        $.post({
            url: "/api/race/single_class",
            data: $("#singleClassData").val(),
            // contentType: 'application/json',
            success: function (result) {
                // on success - reload table
                console.log(result);
            },
            error: function (xhr, resp, text) {
                console.log(method, uri, resp, text);
            }
        })
    });
    $("#musicPlay").click(function (e) {
        e.preventDefault();
        $.post({
            url: "/api/music/play",
            // contentType: 'application/json',
            success: function (result) {
                // on success - reload table
                console.log(result);
            },
            error: function (xhr, resp, text) {
                console.log(method, uri, resp, text);
            }
        })
    });
    $("#musicNext").click(function (e) {
        e.preventDefault();
        $.post({
            url: "/api/music/next",
            // contentType: 'application/json',
            success: function (result) {
                // on success - reload table
                console.log(result);
            },
            error: function (xhr, resp, text) {
                console.log(method, uri, resp, text);
            }
        })
    });
    $("#musicStop").click(function (e) {
        e.preventDefault();
        $.post({
            url: "/api/music/stop",
            // contentType: 'application/json',
            success: function (result) {
                // on success - reload table
                console.log(result);
            },
            error: function (xhr, resp, text) {
                console.log(method, uri, resp, text);
            }
        })
    });
    $("#checkVoltage").click(function (e) {
        e.preventDefault();
        $.getJSON("api/boat/voltage", (data) => {
            $("#voltage").text(data.result);
        }).fail(() => {
            $("#voltage").text("fail");
        });
    });
    $("#navToRamp").click(function (e) {
        GotoWaypoint(29.550373, -95.048091);
    });
    $("#returnToDock").click(function (e) {
        GotoWaypoint(29.549878, -95.048130);
    });
    $("#raceStart").click(function (e) {
        GotoWaypoint(29.549878, -95.048130);
    });


    function GotoWaypoint(lat, longitude){

        var mission_clear = new ROSLIB.Service({
            ros : g_ros,
            name : '/mavros/mission/clear',
            serviceType : 'mavros_msgs/WaypointPush'
        }); 

        var mission_push = new ROSLIB.Service({
            ros : g_ros,
            name : '/mavros/mission/push',
            serviceType : 'mavros_msgs/WaypointPush'
        });
        var set_mode = new ROSLIB.Service({
            ros : g_ros,
            name : 'mavros/set_mode',
            serviceType : 'mavros_msgs/SetMode'
        });

        var auto_mode = new ROSLIB.ServiceRequest({
            custom_mode: "AUTO" // http://wiki.ros.org/mavros/CustomModes  Auto
        });

    
        var mission = new ROSLIB.ServiceRequest({
            start_index: 0,
            waypoints: [{frame: 0, command: 16, // https://mavlink.io/en/messages/crsoommon.html#MAV_CMD_NAV_LOITER_UNLIM
            is_current: true, autocontinue: true, param1: 0, param2: 0.0,
          param3: 0, param4: 0.0, x_lat: 0, y_long: 0, z_alt: 0},
          {frame: 3, command: 17, // https://mavlink.io/en/messages/common.html#MAV_CMD_NAV_LOITER_UNLIM
                is_current: false, autocontinue: true, param1: 5.0, param2: 0.0,
              param3: 50.0, param4: 0.0, x_lat: lat, y_long: longitude, z_alt: 50.0}] 
        });
    
        mission_clear.callService({}, function(result) {
            console.log('Result for clear on '
                + JSON.stringify(result));

            mission_push.callService(mission, function(result) {
                console.log('Result for service call on '
                    + mission_push.name
                    + ': '
                    + JSON.stringify(result));

                set_mode.callService(auto_mode, function(result){
                    console.log('Result for service call on '
                        + auto_mode
                        + ': '
                        + JSON.stringify(result));

                })
            });
        });
    
    }
}

function poll_anchor_status() {
    $.getJSON("api/anchor/status", (data) => {
        $("#anchor_status").text(data.mode);
        setTimeout(poll_anchor_status, 1000);
    }).fail(() => {
        $("#anchor_status").text("fail");
        setTimeout(poll_anchor_status, 1000);
    });
}
var g_ros;

function load() {
    debugger;
    update_buttons();
    setInterval(poll_led_matrix, 200);
    //setTimeout(poll_anchor_status, 1000);
    g_ros = new ROSLIB.Ros({
        url : 'ws://' + location.hostname + ':9090'
    });
    g_ros.on('connection', function() {
        $("#mavros_status").css('color', 'green');
    });

    g_ros.on('error', function(error) {
        console.log('Error connecting to websocket server: ', error);
        $("#mavros_status").css('color', 'red');
    });

    g_ros.on('close', function() {
        console.log('Error connecting to websocket server: ', error);
        $("#mavros_status").css('color', 'red');
    });

    var listener = new ROSLIB.Topic({
        ros : g_ros,
        name : '/mavros/state',
        messageType : 'mavros_msgs/State'
    });

    listener.subscribe(function(message) {
        var armed_state = "Disarmed";
        if(message.armed){
            armed_state = "Armed";
        }
        $("#mavros_state").text(message.mode + " " + armed_state);
        if(message.connected === false){
            $("#armed_panel").hide();
            $("#boat_status").css('color', 'red');
        }else{
            $("#armed_panel").show();
            $("#boat_status").css('color', 'green');
        }
        console.log('Received message on ' + listener.name + ': ' + message.data);
    });

}

$(document).ready(load);