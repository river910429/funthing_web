function game_catch_egg_start(course_id)
{
    //window.location.href="{{ url_for("test") }}";
    window.open(`/game/catch_egg?course_id=${course_id}`, "_self");
}

function leave_game(){
    $.ajax({
        method: "GET",
        url: "/redirect?r_type=lgame",
        contentType: 'application/json',
        dataType: "json",
    })
    .done(function(result) {
        console.log(result);
        if (result["status"] == "success") {
            window.open(result["url"], "_self");
        }
    });
}