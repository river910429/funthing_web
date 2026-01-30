var questions = [];
var current_index = 0;
var total_count = 0;
var recording = false;

function game_start(course_id) {
    window.open(`/game/pronunciation?course_id=${course_id}`, "_self");
}


function leave_game() {
    if (typeof gameConfig !== 'undefined' && gameConfig.homeUrl) {
        window.location.href = gameConfig.homeUrl;
    } else {
        window.location.href = "/";
    }
}

// 頁面載入後執行
$(document).ready(function() {
    // 1. 初始化資料 (gameConfig 在 HTML 中定義)
    if (typeof gameConfig !== 'undefined') {
        parseData(gameConfig.rawData);
        $("#total_q").text(total_count);
        load_question(0);
    } else {
        console.error("Game Config not found!");
    }
    
    // 2. 綁定錄音按鈕事件
    setup_recorder();
});

// 解析後端傳來的資料
function parseData(rawData) {
    if(!rawData) return;
    
    // 格式: ["膨風<br>phong-hong", ...]
    rawData.forEach(function(item) {
        var parts = item.split("<br>");
        questions.push({
            tw: parts[0],
            tlpa: parts[1] || "" 
        });
    });
    total_count = questions.length;
}

// 載入題目
function load_question(idx) {
    if (idx >= total_count) {
        alert("遊戲結束！");
        leave_game();
        return;
    }
    
    current_index = idx;
    $("#current_q").text(idx + 1);
    
    // 更新黑板文字
    $("#word_tw").text(questions[idx].tw);
    $("#word_tlpa").text(questions[idx].tlpa);
    
    // 重置介面狀態
    $("#btn_play_my_voice").css("opacity", "0.5").css("pointer-events", "none");
    $("#bear_msg").text("按下播放鍵一起學習台語發音吧！");
}

// 播放示範語音
function play_audio() {
    var text = questions[current_index].tw;
    $("#bear_msg").text("仔細聽喔：" + text);
    console.log("Play Audio: " + text);
    
    // TODO: 串接 TTS API 
    // var audio = new Audio("/api/tts?text=" + text);
    // audio.play();
}

// 設定錄音按鈕邏輯
function setup_recorder() {
    var btn = $("#btn_record");

    // 按下開始
    btn.on("mousedown touchstart", function(e) {
        e.preventDefault();
        recording = true;
        $("#bear_msg").text("錄音中...請大聲唸出來！");
        $(".dot").addClass("active"); 
        console.log("Start Recording...");
    });

    // 放開結束
    btn.on("mouseup touchend mouseleave", function(e) {
        if (recording) {
            recording = false;
            $("#bear_msg").text("錄音完成！按右邊按鈕聽聽看。");
            $(".dot").removeClass("active");
            
            // 啟用播放按鈕
            $("#btn_play_my_voice").css("opacity", "1").css("pointer-events", "auto");
            console.log("Stop Recording...");
            
            // TODO: 呼叫後端 upload API
        }
    });
}

// 播放自己的錄音
function play_my_recording() {
    $("#bear_msg").text("正在播放你的聲音...");
    console.log("Play User Recording");
}

