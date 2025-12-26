let startFlag = false;
let ceil_setting;
let floor_setting;
let pigeon_height; 

let q_list = [];
let egg_list = [];
let egg_speed = [4.5, 5, 5.5, 6, 6.5, 7];
let cur_wav;
let oneround_status = false;
let answers_status = [];

// --- 移動控制變數 ---
let keys = { left: false, right: false };
let move_speed = 10; 
let current_target_answer = "";

$(document).ready(function(){
    // 判斷是否為遊戲頁面 (有熊才執行)
    if ($("#pigeon").length > 0) {
        
        let pigeon = $("#pigeon");
        pigeon_height = parseFloat(pigeon.css('height')) || 150; 
        
        let floor_el = $('#floor');
        let floor_top = floor_el.length ? parseFloat(floor_el.offset().top) : $(window).height();
        
        // 計算地板與天花板
        floor_setting = (floor_top - pigeon_height) + 'px';
        ceil_setting = '-' + pigeon_height + 'px';
        
        // RWD 速度調整
        move_speed = document.body.clientWidth * 0.01; 
        if(move_speed < 2) move_speed = 5; 

        // 啟動迴圈
        start_movement_loop();

        if (!startFlag) {
            try {
                allround(10);
            } catch (e) {
                console.error("初始化錯誤:", e);
            }
            // ★ 啟動碰撞偵測 ★
            start_collision_detection();
        }
        startFlag = true;

    } else {
        console.log("說明頁待機中...");
    }
});

// --- 鍵盤控制 ---
$(window).keydown(function(e) {
    if(e.keyCode == 37) keys.left = true;
    if(e.keyCode == 39) keys.right = true;
});

$(window).keyup(function(e) {
    if(e.keyCode == 37) keys.left = false;
    if(e.keyCode == 39) keys.right = false;
});

// --- 平滑移動 ---
function start_movement_loop() {
    function loop() {
        let pigeon = $("#pigeon");
        let currentLeft = parseFloat(pigeon.css('left'));
        if (isNaN(currentLeft)) currentLeft = 0;

        let max_width = document.body.clientWidth - pigeon.width();
        
        if (keys.left) {
            let newLeft = currentLeft - move_speed;
            if (newLeft < 0) newLeft = 0;
            pigeon.css('left', newLeft + 'px');
        }
        if (keys.right) {
            let newLeft = currentLeft + move_speed;
            if (newLeft > max_width) newLeft = max_width; 
            pigeon.css('left', newLeft + 'px');
        }
        requestAnimationFrame(loop);
    }
    loop();
}


// --- 碰撞偵測 (修正版 - 縮小蛋的判定範圍) ---
function start_collision_detection() {
    setInterval(function() {
        let pigeon = $("#pigeon");
        
        $('.active-egg').each(function() {
            let $egg = $(this);
            if ($egg.data('caught') === true) return;

            // 1. 取得原始的大矩形範圍
            let egg_rect = $egg[0].getBoundingClientRect();
            let pigeon_rect = pigeon[0].getBoundingClientRect();

            // 防呆機制 (維持不變)
            if (egg_rect.bottom < window.innerHeight / 2) {
                return; 
            }

            // ★★★ 新增：計算內縮量 ★★★
            // 取得蛋的寬高
            let egg_w = egg_rect.width;
            let egg_h = egg_rect.height;

            // 設定內縮比例 (您可以微調這些數字)
            // padX = 0.2 代表左右各向內縮 20% 的寬度
            // padY_Bottom = 0.25 代表底部向上縮 25% 的高度 (讓蛋掉深一點才算接到)
            let padX = egg_w * 0.40; 
            let padY_Bottom = egg_h * 0.35;

            // ★★★ 修改：碰撞公式 (加上內縮量) ★★★
            // 我們在 egg_rect 的邊界上加減 padX/padY 來縮小範圍
            if ((egg_rect.right - padX) > (pigeon_rect.left + 20) &&  // 蛋有效右側 > 熊有效左側
                (egg_rect.left + padX) < (pigeon_rect.right - 20) &&  // 蛋有效左側 < 熊有效右側
                (egg_rect.bottom - padY_Bottom) > (pigeon_rect.top + 30) && // 蛋有效底部 > 熊有效頂部
                egg_rect.top < pigeon_rect.bottom) { // 蛋頂部 < 熊底部 (這條通常維持原樣)
                
                // 發生碰撞 (維持不變)
                $egg.stop(); 
                $egg.data('caught', true); 
                $egg.removeClass('active-egg');
                $egg.css("display", "none"); 
                
                check_answer_immediate($egg);
            }
        });
    }, 30); 
}

// --- 遊戲邏輯 ---
function game_catch_egg_start(course_id) {
    window.open(`/game/catch_egg?course_id=${course_id}`, "_self");
}

function leave_game(){
    $.ajax({
        method: "GET",
        url: "/redirect?r_type=lgame",
        contentType: 'application/json',
        dataType: "json",
    }).done(function(result) {
        if (result["status"] == "success") window.open(result["url"], "_self");
    });
}

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
    }
    end_game(n);
}

function set_q(n) {
    if (typeof subjects_CH === 'undefined' || !subjects_CH) return;
    subjects_CH.sort(() => Math.random() - 0.5);
    q_list = subjects_CH.slice(0, n);
    while(q_list.length < n) {
        subjects_CH.sort(() => Math.random() - 0.5);
        q_list = q_list.concat(subjects_CH);
    }
    q_list = q_list.slice(0, n);
}

async function oneround(round_count) {
    set_subject(round_count);
    
    if (q_list[round_count]) {
        cur_wav = q_list[round_count].split("<br>")[0];
        current_target_answer = q_list[round_count];
    } else {
        return;
    }
    
    var audio_url = "/static/audio/" + cur_wav + ".wav";
    try {
        var audio = new Audio(audio_url);
        await audio.play(); 
    } catch (e) {
        console.log("Audio autoplay blocked", e);
    }

    set_timebar();
    set_egg_text(round_count);
    set_egg_run(round_count);
}

function set_subject(round_count) {
    let adder = $('#subject_adder');
    if(adder.length) adder[0].innerHTML = (round_count+1).toString() + "/10";
}

function set_timebar() {
    $('#game_time_bar').css('width', '36.8%');
}

function set_egg_text(round_count) {
    var oneround_subjects_CH = subjects_CH.slice();
    oneround_subjects_CH = oneround_subjects_CH.filter(item => item != q_list[round_count]);
    oneround_subjects_CH.sort(() => Math.random() - 0.5);
    
    if (oneround_subjects_CH.length) {
        egg_list = oneround_subjects_CH.slice(0, 5);
        while(egg_list.length < 5) {
            oneround_subjects_CH.sort(() => Math.random() - 0.5);
            egg_list = egg_list.concat(oneround_subjects_CH);
        }
        egg_list = egg_list.slice(0, 5);
    } else{
        while(egg_list.length < 5) egg_list.push(q_list[round_count]);
    }

    egg_list.push(q_list[round_count]);
    egg_list.sort(() => Math.random() - 0.5);

    for(var i = 0; i < 6; i++) {
        $('#text' + (i+2))[0].innerHTML = egg_list[i];
    }
}

function set_egg_run(round_count) {
    egg_speed.sort(() => Math.random() - 0.5);
    for(var i = 0; i < 6; i++) {
        var egg_str = '#egg' + (i+2);
        var $egg = $(egg_str);
        
        $egg.addClass('active-egg');
        $egg.data('caught', false);
        $egg.css("display", "");
        $egg.css("visibility", "visible");
        
        // 強制歸位到上方
        $egg.css('top', ceil_setting || '-150px'); 

        $egg.animate({top: floor_setting}, egg_speed[i] * 1000, "linear", function() {
            $(this).removeClass('active-egg');
            $(this).css("display", "none");
            $(this).css("visibility", "hidden");
        });
    }
}

function show_feedback_effect(isCorrect) {
    let pigeon = $("#pigeon");
    
    // 1. 讓熊跳一下 (加 class, 動畫播完後移除 class)
    pigeon.addClass("pigeon-bounce");
    setTimeout(() => {
        pigeon.removeClass("pigeon-bounce");
    }, 300); // 0.3秒後移除，跟 CSS animation 時間一樣

    // 2. 決定文字內容與顏色
    let text = isCorrect ? "⭕" : "❌"; // 也可以改成 "+100" 或 "Wrong"
    let color = isCorrect ? "#00FF00" : "#FF0000"; // 綠色 vs 紅色

    // 3. 建立飄浮元素
    let feedback = $("<div></div>").text(text).addClass("feedback-text");
    
    // 4. 設定初始位置 (在熊的頭頂中間)
    let pigeonLeft = parseFloat(pigeon.css("left"));
    let pigeonTop = parseFloat(pigeon.css("top")) || parseFloat(pigeon.offset().top); // 防呆
    // 如果 pigeon 是 absolute bottom 定位，可能需要用 offset() 抓位置比較準
    // 這裡我們直接抓 offset 比較保險
    let pOffset = pigeon.offset();
    
    feedback.css({
        left: pOffset.left + (pigeon.width() / 2) - 20 + "px", // 減20是為了置中
        top: pOffset.top - 50 + "px", // 在熊頭上 50px
        color: color
    });

    // 5. 加到畫面上並執行飄浮動畫
    $("body").append(feedback);

    feedback.animate({
        top: "-=100px",  // 往上飄 100px
        opacity: 0       // 變透明
    }, 1300, "linear", function() {
        $(this).remove(); // 動畫結束後刪除元素，節省記憶體
    });
}

function check_answer_immediate($egg) {
    var egg_text = $egg.find('span').html();
    console.log("Check:", egg_text);
    let pigeon = $("#pigeon");

    if (egg_text == current_target_answer) {
        // --- 答對 ---
        oneround_status = true;
        pigeon.css('background-image', 'url(/static/4GAME_ALL/ANIMAL_CATCH/1x/ANIMAL_CATCH_PIGEON_LOVE.png)');
        
        // ★ 加入特效 ★
        show_feedback_effect(true); 

    } else {
        // --- 答錯 ---
        if (!oneround_status) {
            oneround_status = false;
            pigeon.css('background-image', 'url(/static/4GAME_ALL/ANIMAL_CATCH/1x/ANIMAL_CATCH_PIGEON_CRY.png)');
            
            // ★ 加入特效 (只有沒答對過才顯示叉叉，或者你想每次接錯都顯示也可以) ★
            show_feedback_effect(false);
        } else {
            // 如果已經答對過了又接到錯的，你要顯示叉叉嗎？
            // 如果想，也可以在這裡呼叫 show_feedback_effect(false);
        }
    }
}

function resetround() {
    $('#game_time_bar').css('transition', "none");
    $('#game_time_bar').css('width', '3%');
    // 恢復動畫 transition
    setTimeout(function(){
        $('#game_time_bar').css('transition', "width 8s ease");
    }, 100);

    for(var i = 0; i < 6; i++) {
        var egg_str = '#egg' + (i+2);
        $(egg_str).css('top', ceil_setting);
    }
    $("#pigeon").css('background-image', 'url(/static/4GAME_ALL/ANIMAL_CATCH/1x/ANIMAL_CATCH_PIGEON.png)');
    oneround_status = false;
}

function end_game(n) {
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
        data: JSON.stringify({ "data": _data }),
        dataType: "json",
    }).done(function(result) {
        if (result["status"] == "success") document.location.href=_url;
    })
}
function listen_again() {
    if(cur_wav) {
        var audio_url = "/static/audio/" + cur_wav + ".wav";
        new Audio(audio_url).play();
    }
}