
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
            url: "/api/status",
            type: "PUT",
            data: { "status": "restart" },
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
    $("#countDownBegin").click(function (e) {
        e.preventDefault();
        // Send RESTApi request to change port status
        $.ajax({
            url: "/api/race/count_down",
            type: "POST",
            data: { "num_min": "3" },
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
        $.ajax({
            url: "/api/race/delay",
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
    $("#anchorForward").click(function (e) {
        e.preventDefault();
        // Send RESTApi request to change port status
        $.ajax({
            url: "/api/anchor/forward",
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
    $("#anchorReverse").click(function (e) {
        e.preventDefault();
        // Send RESTApi request to change port status
        $.ajax({
            url: "/api/anchor/reverse",
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
    $("#anchorStop").click(function (e) {
        e.preventDefault();
        // Send RESTApi request to change port status
        $.ajax({
            url: "/api/anchor/stop",
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
        // Send RESTApi request to change port status
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
    //$("#myButton").html("Off");
}

function on_hash_change() {
    var hash = window.location.hash;
    if (hash == '') {
        hash = '#status';
    }
    console.log("Hash change", hash);
    $.getJSON("api/" + hash.substring(1), function (data) {
        if (hash == "#status") {
            update_status(data)
        }
        if (hash == "#gpio") {
            update_gpio(data);
        }
    });
    $("main").hide()
    $(hash).show();
}

function load() {
    debugger;
    update_buttons();
    setInterval(poll_led_matrix, 200);
    on_hash_change();
}

window.onhashchange = on_hash_change;
$(document).ready(load);