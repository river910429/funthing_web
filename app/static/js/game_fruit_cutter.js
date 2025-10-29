let current_ans, question_set, fruits, prev_fruit;
let answers_sheet = [];
let answers_status = [];
let fruits_queue = [];
let startFlag = false;
let flowingFlag = true;
let y_history = []
let x_history = []
var org_setting = $('#game_time_bar').css('transition');
var duration = document.getElementById("game_time_bar");

function game_start(course_id){
    window.open(`/game/fruit_cutter?course_id=${course_id}`, "_self");
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
function subject_addup(){
    let count = (8 - question_set.length)+1;
    if (count > 8) time_out();
    else $('#subject_adder')[0].innerHTML = count.toString() + "/8";
}

question_set = subjects_CH
console.log(question_set.length)
console.log(question_set)
wait_src = "/static/4GAME_ALL/CUT_FRUIT/SAY_INTO_MICROPHONE.png"
bomb_src = "/static/4GAME_ALL/CUT_FRUIT/FRUIT_BOB.png"
fruit_src = "/static/4GAME_ALL/CUT_FRUIT/FRUIT/"
cut_fruit_src = "/static/4GAME_ALL/CUT_FRUIT/CUT_FRUIT/"
// fruits = ["FRUIT_BANANA.png", 
//                 "FRUIT_APPLE.png",
//                 "FRUIT_BLUEBERRY.png",
//                 "FRUIT_CHERRY.png",
//                 "FRUIT_CRANBERRIES.png",
//                 "FRUIT_GRAPE.png",
//                 "FRUIT_KIWI.png",
//                 "FRUIT_LEMON.png",
//                 "FRUIT_ORANGE.png",
//                 "FRUIT_PEAR.png",
//                 "FRUIT_PINEAPPLE.png",
//                 "FRUIT_POMEGRANATE.png",
//                 "FRUIT_STRAWBERRY.png",
//                 "FRUIT_WATERMELON.png"]

fruits = ["台教_石賓魚.png",
         "台教_臺灣馬口魚.png",
         "台教_臺灣鯛.png",
         "台教_臺灣嚶口鰍.png",
         "台教_櫻花鉤吻鮭.png",
         "台教_石賓魚.png",
         "台教_臺灣馬口魚.png",
         "台教_臺灣鯛.png",
         "台教_臺灣嚶口鰍.png",
         "台教_櫻花鉤吻鮭.png",
         "台教_石賓魚.png",
         "台教_臺灣馬口魚.png",
         "台教_臺灣鯛.png",
         "台教_臺灣嚶口鰍.png"
]                

$(document).ready(function(){
    if (!startFlag) {
        duration.addEventListener("transitionend", time_out, false);
        time_progress();
        var fruit = document.getElementById('record_btn');
        fruit.addEventListener("click", pause_animate);
        change_fruit();
        shuffling_arr(question_set);
        current_ans = question_set.pop();
        answers_sheet.push(current_ans);
        console.log(current_ans);
        listen_again(current_ans);
        moveIt(fruit);
    }
    startFlag = true;
});

function listen_again() {
    var cur_wav = current_ans.split("<br>")[0];
    var audio_url = "/static/audio/" + cur_wav + ".wav";
    var audio = new Audio(audio_url).play();
}

function shuffling_arr(array) {
    array.sort(() => Math.random() - 0.5);
}

function pause_animate() {
    if (flowingFlag) {
        flowingFlag = false;
        var fruit = document.getElementById('record_btn');
        fruit.setAttribute("src", wait_src);
    }
}

function change_fruit() {
    var fruit = document.getElementById('record_btn');
    $(fruit).css('visibility', 'hidden');
    shuffling_arr(fruits);
    prev_fruit = fruits.pop();
    fruit.setAttribute("src", fruit_src+prev_fruit);
    $(fruit).css('visibility', 'visible');
    console.log("hi", prev_fruit);
}

function verify_answer(hypothesis) {
    var current_ans_temp = current_ans.split("<br>")[0];
    var ans = hypothesis.some(x => !!x.match(current_ans_temp));
    console.log(ans, current_ans_temp, hypothesis);
    if (ans) {
        console.log("CORRECT", prev_fruit);
        var fruit = document.getElementById('record_btn');
        fruit.setAttribute("src", cut_fruit_src+prev_fruit);
        answers_status.push(true);
    }
    else {
        console.log("WRONG");
        var fruit = document.getElementById('record_btn');
        fruit.setAttribute("src", bomb_src);
        answers_status.push(false);
    }
    setTimeout(() => {
        flowingFlag = true;
        console.log("continue moving");
        var fruit = document.getElementById('record_btn');
        moveIt(fruit);
        subject_addup();
        shuffling_arr(question_set);
        current_ans = question_set.pop();
        answers_sheet.push(current_ans);
        console.log(current_ans);
        listen_again(current_ans);
        change_fruit();
    }, 1500);
}

function remove_fruit() {
    var fruits = $('.fruit');
    fruits.each(function closing() {
        $(this).remove();
    });
}

function moveIt(fruit) {
    var height = $(window).height() * 0.6;
    var height_d = $(window).height() * 0.15;
    var width = $(window).width() * 0.8;
    var width_d = $(window).width() * 0.05;
    var vel = 250;
    function wildcard(){
        if(flowingFlag)
        {
            var y = (Math.random() * height + height_d) | 0;
            var x = (Math.random() * width + width_d) | 0;
            var time = Math.random() * (1200 - 400) + 400 | 0;
            if (y_history.length > 0) {
                let prev_y = y_history[y_history.length - 1];
                let prev_x = x_history[y_history.length - 1];
                alt_y = y - prev_y;
                alt_x = x - prev_x;
                
                let dist = Math.sqrt(alt_x ** 2 + alt_y ** 2);
                time = Math.floor(dist * 1000 / vel);
            }
            y_history.push(y);
            x_history.push(x);
            console.log(x, y)

            $(fruit).animate({
                left: x,
                top: y
            }, time, wildcard, 
            );
        }
    }

    $(fruit).css('visibility', 'visible');
    wildcard();
}

function time_progress() {
    $('#game_time_bar').css('transition', org_setting);
    $('#game_time_bar').delay(500).queue(function () {
        $(this).css('width', '36.8%')
    });
}

function time_out() {
    console.log('Timeout!');
    var fruits = $('.fruit');
    fruits.each(function closing() {
        $(this).css('visibility', 'hidden');
    });
    remove_fruit();
    end_game();
}

function end_game() {
    console.log('Game done');
    answers_sheet = answers_sheet.concat(question_set);
    console.log(answers_sheet);
    while (answers_status.length < answers_sheet.length) {
        answers_status.push(false);
    }
    console.log(answers_status);

    let result_sheet = []
    for (i = 0; i < 8; i++) {
        let tmp = []
        tmp.push(answers_sheet[i]);
        tmp.push(answers_status[i]);
        result_sheet.push(tmp)
    }

    course_id = document.URL.split('?')[1]
    game_close(`/game/fruit_cutter/game_result?${course_id}`, result_sheet);
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