function home()
{
    window.open("/home/stu", "_self");
}

function back()
{
    window.open("/home/stu", "_self");
}

function game_card()
{
    $.ajax({
        method: "POST",
        url: "/template/course/search",
        contentType: 'application/json',
        data: JSON.stringify({
            "game_name": "game1"
        }),
        dataType: "json",
    })
    .done(function(result) {
        console.log(result);
        if (result["status"] == "success") {
            window.open(`/game/flipping_card_tutorial?course_id=${result["course_id"]}`, "_self");
        }
    });
}

function game_catch()
{
    $.ajax({
        method: "POST",
        url: "/template/course/search",
        contentType: 'application/json',
        data: JSON.stringify({
            "game_name": "game2"
        }),
        dataType: "json",
    })
    .done(function(result) {
        console.log(result);
        if (result["status"] == "success") {
            window.open(`/game/catch_egg_tutorial?course_id=${result["course_id"]}`, "_self");
        }
    });
}

function game_fruit()
{
    $.ajax({
        method: "POST",
        url: "/template/course/search",
        contentType: 'application/json',
        data: JSON.stringify({
            "game_name": "game3"
        }),
        dataType: "json",
    })
    .done(function(result) {
        console.log(result);
        if (result["status"] == "success") {
            window.open(`/game/fruit_cutter_tutorial?course_id=${result["course_id"]}`, "_self");
        }
    });
}

function game_map()
{
    $.ajax({
        method: "POST",
        url: "/template/course/search",
        contentType: 'application/json',
        data: JSON.stringify({
            "game_name": "game4"
        }),
        dataType: "json",
    })
    .done(function(result) {
        console.log(result);
        if (result["status"] == "success") {
            window.open(`/game/map_tutorial?course_id=${result["course_id"]}`, "_self");
        }
    });
}
