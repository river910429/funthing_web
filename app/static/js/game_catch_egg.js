
let startFlag = false;
let org_setting = $('#game_time_bar').css('transition');
let ceil_setting = '-'+$('#pigeon').css('height');
let floor_setting = parseFloat($('#floor').css('top'), 10) - parseFloat($('#pigeon').css('height'), 10) + 'px';
let q_list = [];
let egg_list = [];
let egg_speed = [4.5,5,5.5,6,6.5,7];
let pigeon = $("#pigeon");
let cur_wav;

let oneround_status = false;
let answers_status = [];

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

$(document).ready(function(){
    if (!startFlag) {
        allround(10);
    }
    startFlag = true;
});

async function sleep(ms = 0) {
    return new Promise(r => setTimeout(r, ms));
}

async function allround(n) {
    set_q(n);
    for(var i = 0; i < n; i++){
        oneround(i);
        await sleep(10 * 1000);
        answers_status.push(oneround_status);
        resetround();
        // await sleep(500);
    }
    end_game(n);
}

function listen_again() {
    var audio_url = "/static/audio/" + cur_wav + ".wav";
    var audio = new Audio(audio_url).play();
}

// init set
function set_q(n) {
    subjects_CH.sort(() => Math.random() - 0.5);
    q_list = subjects_CH.slice(0, n);
    while(q_list.length < n) {
        subjects_CH.sort(() => Math.random() - 0.5);
        q_list = q_list.concat(subjects_CH);
    }
    q_list = q_list.slice(0, n);
    console.log("q_list", q_list);
}

// one round
async function oneround(round_count) {
    set_subject(round_count);
    cur_wav = q_list[round_count].split("<br>")[0];
    var audio_url = "/static/audio/" + cur_wav + ".wav";
    var audio = new Audio(audio_url).play();
    console.log(q_list[round_count]);
    await sleep(1500);
    set_timebar();
    set_egg_text(round_count);
    set_egg_run(round_count);
}

function set_subject(round_count) {
    $('#subject_adder')[0].innerHTML = (round_count+1).toString() + "/10";
}

function set_timebar() {
    $('#game_time_bar').css('transition', org_setting);
    $('#game_time_bar').css('width', '36.8%');
}

function set_egg_text(round_count) {
    var oneround_subjects_CH = subjects_CH.slice();
    oneround_subjects_CH = oneround_subjects_CH.filter(item => item != q_list[round_count]);

    // console.log("subjects_CH", subjects_CH);
    // console.log("oneround_subjects_CH", oneround_subjects_CH);

    oneround_subjects_CH.sort(() => Math.random() - 0.5);
    if (oneround_subjects_CH.length) {
        egg_list = oneround_subjects_CH.slice(0, 5);
        while(egg_list.length < 5) {
            oneround_subjects_CH.sort(() => Math.random() - 0.5);
            egg_list = egg_list.concat(oneround_subjects_CH);
        }
        egg_list = egg_list.slice(0, 5);
    }
    else{
        while(egg_list.length < 5) {
            egg_list.push(q_list[round_count]);
        }
    }

    egg_list.push(q_list[round_count]);
    egg_list.sort(() => Math.random() - 0.5);

    // console.log("egg_list", egg_list);

    for(var i = 0; i < 6; i++) {
        $('#text' + (i+2))[0].innerHTML = egg_list[i];
    }
}

function set_egg_run(round_count) {
    egg_speed.sort(() => Math.random() - 0.5);
    for(var i = 0; i < 6; i++) {
        var egg_str = '#egg' + (i+2);
        var jj = i;
        $(egg_str).css("display", "");
        $(egg_str).css("visibility", "visible");
        $(egg_str).animate({top: floor_setting}, egg_speed[i] * 1000, "linear", function() {
            // console.log("onfloor");
            check_answer(this, q_list[round_count], $(this).offset().left);
            $(this).css("display", "none");
            $(this).css("visibility", "hidden");
        });
    }
}

function check_answer(egg, answer) {
    var egg_str = $($(egg).html()).html();
    var egg_left = parseFloat($(egg).offset().left, 10);
    var egg_right = egg_left + parseFloat($(egg).width(), 10);
    var pigeon_left = parseFloat($("#pigeon").offset().left, 10);
    var pigeon_right = pigeon_left + parseFloat($("#pigeon").width(), 10);
    // console.log(egg_str, egg_left, egg_right);
    // console.log(answer, pigeon_left, pigeon_right);
    if (pigeon_right >= egg_left && egg_right >= pigeon_left) {
        console.log("catch", egg_str);
        if (egg_str == answer) {
            console.log("correct");
            oneround_status = true;
            pigeon.css('background-image', 'url(/static/4GAME_ALL/ANIMAL_CATCH/1x/ANIMAL_CATCH_PIGEON_LOVE.png)');
        }
        else {
            if (!oneround_status) {
                console.log("error");
                oneround_status = false;
                pigeon.css('background-image', 'url(/static/4GAME_ALL/ANIMAL_CATCH/1x/ANIMAL_CATCH_PIGEON_CRY.png)');
            
            }
        }
    }
}

// reset round
function resetround() {
    $('#game_time_bar').css('transition', "none");
    $('#game_time_bar').css('width', '3%');
    for(var i = 0; i < 6; i++) {
        var egg_str = '#egg' + (i+2);
        $(egg_str).css('top', ceil_setting);
    }
    pigeon.css('background-image', 'url(/static/4GAME_ALL/ANIMAL_CATCH/1x/ANIMAL_CATCH_PIGEON.png)');
    oneround_status = false;
}

// end
function end_game(n) {
    console.log(answers_status);

    let result_sheet = []
    for (i = 0; i < n; i++) {
        let tmp = []
        tmp.push(q_list[i]);
        tmp.push(answers_status[i]);
        result_sheet.push(tmp)
    }

    course_id = document.URL.split('?')[1]
    game_close(`/game/catch_egg/game_result?${course_id}`, result_sheet);
}
function game_close(_url, _data) {
    $.ajax({
        method: "POST",
        url: _url,
        contentType: 'application/json',
        data: JSON.stringify({
            "data": _data
        }),
        dataType: "json",
    })
    .done(function(result) {
        console.log(result);
        if (result["status"] == "success") {
            document.location.href=_url;
        }
    })
}

// move 
$(document).keydown(function(e) {
    var step_float = 0.05; //vw
    step_info = transfer_vh_2_px(step_float);
    step_pix = parseInt(step_info[0]);
    max_width = parseInt(step_info[1]);
    var pigeon_width = parseInt(pigeon.css('width'));

    if(e.keyCode == 37) { // left
      now_position = parseInt(pigeon.css('left'));
      next_position = now_position - step_pix;
    //   console.log(next_position);
      if (next_position >= 0)
      {
        pigeon.css('left', next_position)
      }
      else {
        pigeon.css('left', 0)
      }
    }
    else if(e.keyCode == 39) { // right
        now_position = parseInt(pigeon.css('left'));
        next_position = now_position + step_pix + pigeon_width;
        // console.log(next_position);
        if (next_position < max_width)
        {
            next_position = next_position - pigeon_width;
            pigeon.css('left', next_position)
        }
        else {
            pigeon.css('left', max_width-pigeon_width-10)
        }
    }
});
function transfer_vh_2_px(_step){
    var client_width;
    client_width = document.body.clientWidth;
    move_pix = client_width * _step
    return [move_pix, client_width]
}


