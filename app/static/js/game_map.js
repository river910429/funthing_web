function game_map_start(course_id){
    window.open(`/game/map?course_id=${course_id}`, "_self");
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


// [100, 163, 129]
// [137, 200, 167]
// [100, 163, 129]
// [74, 98, 52]
// [111, 174, 141]


// [109, 172, 138]  @ (4577,926)
// VM4797:40 [110, 173, 139]  @ (4517,1090)
// VM4797:40 [107, 170, 136]  @ (4310,1060)
// VM4797:40 [108, 171, 137]  @ (3989,1690)
// VM4797:40 [113, 176, 142]  @ (3494,2550)
// VM4797:40 [51, 75, 62]  @ (3717,2756)

// 對到的點
var destination_rgb = {
  "taipei": [109, 172, 138] ,
  "newtaipei": [110, 173, 139],
  "taoyuan": [107, 170, 136],
  "taichung": [108, 171, 137],
  "tainan": [113, 176, 142],
  "kaohsiung": [90, 160, 130]
}

// 對到後顯示的點
var destination_pos = {
    "taipei":    [25.7, 58.1],
    "newtaipei": [29.8, 58.5],
    "taoyuan":   [32.6, 53.5],
    "taichung":  [42.4, 50.5],
    "tainan":    [65.4, 43.0],
    "kaohsiung": [70.6, 46.3]
};


let startFlag = false;
var puzzle_seq = ["kaohsiung", "newtaipei", "taichung", "tainan", "taipei", "taoyuan"]
// var destination_rgb = {"taipei":[165,190,175],
//                         "newtaipei":[125,165,165],
//                         "taoyuan":[130,185,190],
//                         "taichung":[145,165,145],
//                         "tainan":[150,180,180],
//                         "kaohsiung":[130,170,160]}

// var destination_pos = {"taipei":[19.5,57.7],
//                         "newtaipei":[17.2, 55.1],
//                         "taoyuan":[20.6, 50.5],
//                         "taichung":[36.3, 41.8],
//                         "tainan":[60.3, 37],
//                         "kaohsiung":[58.2,41.7]}
let count = 0;
var answer_res = {}
var subject_dict = {}
let ans_subject_dict = {}
// $(document).ready(function() {
//     push_subject_2_puzzle();
// });

const placedSet = new Set();   // 已經正確放上的拼圖 id

$(document).ready(function(){
    if (!startFlag) {
        time_progress();

        var select_subjects = []
        for(var idx = 0; idx < 6; idx ++)
        {
            var select_one = subjects_CH[idx];
            select_subjects.push(select_one);
        }
        push_subject_2_puzzle(select_subjects);
        // $(this).css('visibility', 'visible');
    }
    startFlag = true;
});

function push_subject_2_puzzle(subjects)
{
    var idx = 0;
    for (var i = 0; i < puzzle_seq.length; i ++) {
        $('#subject_' + (idx + 1).toString())[0].innerHTML = subjects[idx];
        // console.log(key, value);
        $('#' + puzzle_seq[i]).attr('subject', subjects[idx])
        subject_dict[puzzle_seq[i]] = subjects[idx];
        ans_subject_dict[puzzle_seq[i]] = subjects[idx];
        answer_res[puzzle_seq[i]] = false;
        idx= idx + 1;
      }

}

var org_setting = $('#game_time_bar').css('transition');
function time_progress() {
    $('#game_time_bar').css('transition', org_setting);
    $('#game_time_bar').delay(500).queue(function () {
        $(this).css('width', '36.8%')
    });
}

// function subject_addup(){
//     count = count + 1;
//     if (count == 6) end_game();
//     else $('#subject_adder')[0].innerHTML = count.toString() + "/6";
// }
function subject_addup(){
    const c = placedSet.size;
    $('#subject_adder')[0].innerHTML = c + "/6";
    if (c === 6) end_game();
  }

function end_game() {
    console.log('Game done');
    let result_sheet = [];
    ["tainan", "taipei", "taoyuan", "kaohsiung", "newtaipei", "taichung"].forEach(function(key) {
        let tmp = []
        tmp.push(subject_dict[key]);
        tmp.push(answer_res[key]);
        result_sheet.push(tmp);
    }); 
    console.log(result_sheet);

    course_id = document.URL.split('?')[1]
    game_close(`/game/map/game_result?${course_id}`, result_sheet);
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

let duration = document.getElementById("game_time_bar");
duration.addEventListener("transitionend", end_game, false);


var puzzles = document.querySelectorAll(".puzzle")

puzzles.forEach(element => {
    element.addEventListener('dragstart', dragStart);
    element.addEventListener('drop', dropped);
    element.addEventListener('dragover', cancelDefault);
});
let puzzles_target = document.querySelector("#background_img")
puzzles_target.addEventListener('drop', dropped);
puzzles_target.addEventListener('dragover', cancelDefault);

function dragStart(e) {
    console.log("dragging...");
    e.dataTransfer.setData('text/plain', e.target.id);
    // e.preventDefault();
    // $(this).css('display', 'none')
  }


// function dropped(e) {
//     console.log('dropped');
//     cancelDefault(e);
//     // console.log(e.clientX)
//     // console.log(e.clientY)

//     var canvas = document.createElement("canvas");
//     // console.log(puzzles_target.width)
//     canvas.width = puzzles_target.width;
//     canvas.height = puzzles_target.height;
//     console.log('client x y' + e.clientX + ',' + e.clientY)
//     console.log('canvas' + canvas.width + ',' + canvas.height)
//     var ctx = canvas.getContext("2d");
//     ctx.drawImage(puzzles_target, 0, 0, canvas.width, canvas.height);
//     var c = canvas.getContext('2d');
//     var p = c.getImageData(e.clientX, e.clientY, 1, 1).data;
//     var R = p[0];
//     var G = p[1];
//     var B = p[2];  
//     let id = e.dataTransfer.getData('text/plain');
//     var dest_rgb = destination_rgb[id]

//     if (R == dest_rgb[0] && G == dest_rgb[1] && B == dest_rgb[2]){
//         // alert("bingo!!")
//         // console.log(subjects_CH)
//         console.log(id);
//         answer_res[id] = true;
//         $('#' + id).css('top', destination_pos[id][0] + 'vh');
//         $('#' + id).css('left', destination_pos[id][1] + '%');
//         subject_addup();
//     }
//     else{
//         // alert("fail!!")
//     }
//     // e.target.appendChild(document.querySelector('#' + id));
// }

function dropped(e) {
    console.log('dropped');
    cancelDefault(e);
  
    const img  = puzzles_target;                 // #background_img
    const rect = img.getBoundingClientRect();
    const iw   = img.naturalWidth;
    const ih   = img.naturalHeight;
  
    // 以圖片原生解析度建立離屏畫布
    const canvas = document.createElement('canvas');
    canvas.width = iw; canvas.height = ih;
    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    ctx.drawImage(img, 0, 0, iw, ih);
  
    // 視窗座標 → 圖片座標
    const x = Math.floor((e.clientX - rect.left) * (iw / rect.width));
    const y = Math.floor((e.clientY - rect.top)  * (ih / rect.height));
  
    const p = ctx.getImageData(x, y, 1, 1).data;
    const R = p[0], G = p[1], B = p[2];
  
    const id = e.dataTransfer.getData('text/plain');
    if (!id) return;
  
    // 已經完成的拼圖：直接忽略，避免重複加分
    if (placedSet.has(id)) {
      console.log(id, 'already placed → ignore');
      return;
    }
  
    const want = destination_rgb[id];
    if (!want) return;
  
    // 容差避免反鋸齒/壓縮造成 ± 偏差
    const tol = 40;
    const hit = Math.abs(R - want[0]) <= tol &&
                Math.abs(G - want[1]) <= tol &&
                Math.abs(B - want[2]) <= tol;
  
    console.log('sample', { x, y, got:[R,G,B], expect: want, hit, id });
  
    if (hit) {
      placedSet.add(id);                // 標記這片完成
      answer_res[id] = true;            // 記作答對
      // 用百分比定位（top%、left%）
      const pos = destination_pos[id];  // [top%, left%]
    
      const scaleMap = {
        taipei: 2.5,
        newtaipei: 1.2,
        taoyuan: 1.5,
        taichung: 0.9,
        tainan: 1.2,
        // kaohsiung: 1.0,
      };
      const scale = scaleMap[id] || 1;
      
      $('#' + id).css({
        top:  pos[0] + '%',
        left: pos[1] + '%',
        transform: `translate(-50%, -100%) scale(${scale})`,
        'z-index': 10
      });
      //   $('#' + id).css({
    //     top:  pos[0] + '%',
    //     left: pos[1] + '%',
    //     transform: 'translate(-50%, -100%)' // 視覺錨點可調
    //   });


      // 禁止再拖，避免再次觸發
      $('#' + id).attr('draggable', 'false').css('pointer-events', 'none');
  
      subject_addup();
    }
  }
  

function cancelDefault(e) {
    e.preventDefault();
    e.stopPropagation();
    return false;
}

function verify_answer(hypothesis)
{
    // Object.keys(subject_dict).forEach(function(key) {
    //     var current_ans_temp = subject_dict[key].split("<br>")[0];
    //     var ans = hypothesis.some(x => !!x.match(current_ans_temp))
    //     if (ans) {
    //         console.log(current_ans_temp, key);
    //         var org_src = $('#' + key).attr('src')
    //         org_src = org_src.replace('.png', '');
    //         org_src = org_src.replace('_Select', '');
    //         console.log(org_src)
    //         $('#' + key).attr('src', org_src + "_Select.png");
    //         $('#' + key).attr('draggable', "true");
    //     }
    // });

    var finded = false;
    for (var i = 0; i < hypothesis.length && !finded; i++) {
        var temp = hypothesis[i];
        for (var key in ans_subject_dict) {
            if (temp.includes(ans_subject_dict[key].split("<br>")[0])) {
                var org_src = $('#' + key).attr('src');
                org_src = org_src.replace('.png', '');
                org_src = org_src.replace('_Select', '');
                console.log(org_src)
                $('#' + key).attr('src', org_src + "_Select.png");
                $('#' + key).attr('draggable', "true");

                finded = true;
                delete ans_subject_dict[key];
                break;
            }
        }
    }
    // console.log(correct_id);
    // if (correct_id != "")
    // {
    //     var org_src = $('#' + correct_id).attr('src')
    //     console.log(org_src)
    //     org_src = org_src.replace('.png', '')
    //     console.log(org_src)
    //     $('#' + correct_id).attr('src', org_src + "_Select.png");
    //     $('#' + correct_id).attr('draggable', "true");
    // }
    // else{
    //     // alert("錯誤!");
    // }
    // 開啟校準：在地圖上點一下，Console 會印出 top%、left%（複製去 destination_pos）
}

// 顯示「錄音中」狀態
function showRecognizing() {
    $('#recognition_status').fadeIn(100);
    $('#recognition_status').css("display", "flex");
    
    $('#mic_wave').show();          // 顯示聲波
    $('#btn_stop_record').show();   // ★ 顯示結束按鈕 ★
    
    $('#loading_spinner').hide();   // 隱藏轉圈
    $('#status_text').text("正在聆聽...");
    $('#status_text').css("color", "#333");
}

// 顯示「分析中」狀態
function showLoading() {
    $('#mic_wave').hide();
    $('#btn_stop_record').hide();   // ★ 隱藏結束按鈕 ★
    
    $('#loading_spinner').show();   // 顯示轉圈
    $('#status_text').text("辨識中...");
}

// 顯示結果
function showResult(resultText) {
    $('#mic_wave').hide();
    $('#loading_spinner').hide();
    $('#btn_stop_record').hide();   // 確保按鈕隱藏
    
    $('#status_text').text(resultText);
    $('#status_text').css("color", "#d63031");

    setTimeout(function() {
        $('#recognition_status').fadeOut(300);
    }, 1500);
}

// ★ 新增：手動點擊「結束錄音」按鈕時呼叫的函式 ★
function finishRecording() {
    // 呼叫 record-live-audio.js 裡面的停止函式
    if (typeof map_record_process_end === "function") {
        map_record_process_end();
    }
}