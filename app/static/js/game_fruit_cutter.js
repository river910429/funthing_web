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

window.audio_predict = function() {
    console.log("切水果專用的辨識流程啟動...");
    $.ajax({
        type: "GET",
        url: "/predict",
        contentType: "application/json",
        dataType: 'json'
    }).then(function(response){
        console.log("Success Predict", response);
        
        // 恢復顯示題號 (原本在錄音時可能顯示"辨識中")
        subject_addup(); 

        if (response.recognition) {
            let ans = Array.isArray(response.recognition) ? response.recognition : [response.recognition];
            // 呼叫切水果的驗證邏輯
            verify_answer(ans);
        } else {
            console.log("無法辨識");
            verify_answer(["(無聲)"]);
        }
    }, function(){
        console.error("Fail Predict");
        verify_answer(["(API Error)"]);
    });
}

$(document).ready(function(){
    if (!startFlag) {
        duration.addEventListener("transitionend", time_out, false);
        time_progress();
        var fruit = document.getElementById('record_btn');

        create_status_label();
        
        // 初始化錄音 (呼叫 record-live-audio.js 裡面的函式)
        if(typeof map_record_init === "function") {
             map_record_init(); 
        }

        // 綁定點擊事件
        fruit.addEventListener("click", pause_animate);
        
        change_fruit();
        shuffling_arr(question_set);
        current_ans = question_set.pop();
        answers_sheet.push(current_ans);
        listen_again(current_ans);
        moveIt(fruit);
    }
    startFlag = true;
});


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


// ★★★ 重點修改 2: 修改點擊水果後的行為 ★★★
function pause_animate() {
    // 防止連點，確認是否正在移動中
    if (flowingFlag) {
        flowingFlag = false;
        var fruit = document.getElementById('record_btn');
        var $fruit = $(fruit);
        
        // 1. 停止動畫
        $(fruit).stop(); 
        fruit.setAttribute("src", wait_src); // 換成麥克風圖片

        // 2. ★★★ 計算位置並顯示標籤 ★★★
        var pos = $fruit.position(); // 抓目前魚停在哪
        var fishWidth = $fruit.width();
        var fishHeight = $fruit.height();
        
        // 顯示標籤，並算一下位置讓它置中
        $('#status_label').css({
            'display': 'block',
            // 水平置中：魚的左邊 + (魚寬/2) - (標籤寬度會自動修正，這裡先簡單對齊)
            'left': pos.left + (fishWidth / 2), 
            'top': pos.top - 60, // 放在魚頭上方 60px 處
            'transform': 'translateX(-50%)' // 確保標籤本身置中
        }).text("辨識中..."); // 重設文字

        // 3. 呼叫共用檔的「開始錄音」
        // 假設 record-live-audio.js 裡原本是用 map_record_process_start 這個名字
        if(typeof map_record_process_start === "function") {
            // 強制設定 flag 允許錄音 (以防共用檔狀態不同步)
            // 如果共用檔是用 record_flag 控制，我們確保它是 false 才能開始
            map_record_process_start(); 
        }

        // 3. 設定自動停止 (Auto-stop)
        console.log("錄音開始，2.5秒後自動結束...");
        setTimeout(() => {
            console.log("時間到，停止錄音並送出...");
            
            // 視覺提示：顯示辨識中
            $('#subject_adder').text("辨識中...");

            // 呼叫共用檔的「停止錄音」
            if(typeof map_record_process_end === "function") {
                map_record_process_end();
                // 注意：共用檔的 end 函式通常會呼叫 upload -> 然後呼叫 audio_predict
                // 因為我們在上面已經覆寫了 audio_predict，所以它會自動跑回來執行我們寫好的邏輯
            }
        }, 2500);
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

// game_fruit_cutter.js

function verify_answer(hypothesis) {
    var current_ans_temp = current_ans.split("<br>")[0];
    var ans = hypothesis.some(x => !!x.match(current_ans_temp));
    console.log(ans, current_ans_temp, hypothesis);

    // ★★★ 修改重點 1：顯示辨識結果 ★★★
    // 舊的程式碼是直接 hide()，現在我們改成更新文字
    var resultText = Array.isArray(hypothesis) ? hypothesis.join(", ") : hypothesis;
    
    // 防呆：如果是空的或 undefined
    if (!resultText) resultText = "(無法辨識)";
    
    // 更新標籤文字
    $('#status_label').text(resultText);

    // (選用) 您可以根據對錯改變文字顏色，讓回饋更明顯
    if (ans) {
        $('#status_label').css('color', '#90EE90'); // 答對顯示淺綠色
    } else {
        $('#status_label').css('color', '#FF6347'); // 答錯顯示番茄紅
    }

    // --- 原本的判斷邏輯 ---
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

    // --- 1.5秒後重置遊戲 ---
    setTimeout(() => {
        // ★★★ 修改重點 2：等要換下一題了，再把標籤藏起來 ★★★
        $('#status_label').hide();
        $('#status_label').css('color', 'white'); // 記得把顏色改回白色，不然下一題會殘留顏色

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
    }, 1500); // 這個時間決定了結果顯示多久
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
    var vel = 220;
    function wildcard(){
        if(flowingFlag)
        {
            var y = (Math.random() * height + height_d) | 0;
            var x = (Math.random() * width + width_d) | 0;
            // var time = Math.random() * (1200 - 400) + 400 | 0;
            var time = Math.random() * (4000 - 2000) + 2000 | 0;

            
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

// 產生「辨識中」的浮動標籤
function create_status_label() {
    if ($('#status_label').length === 0) {
        // 建立一個 div，樣式直接寫在這裡方便控制
        var label = $('<div id="status_label">辨識中...</div>');
        label.css({
            'position': 'absolute',
            'display': 'none',        // 一開始隱藏
            'z-index': '1000',        // 確保蓋在魚上面
            'background-color': 'rgba(0, 0, 0, 0.7)', // 半透明黑色背景
            'color': 'white',
            'padding': '10px 20px',
            'border-radius': '20px',  // 圓角
            'font-size': '24px',      // 字體大小
            'font-weight': 'bold',
            'pointer-events': 'none', // 讓滑鼠點擊穿透它，不會擋到操作
            'white-space': 'nowrap'
        });
        $('#holder').append(label); // 加到遊戲畫面上
    }
}