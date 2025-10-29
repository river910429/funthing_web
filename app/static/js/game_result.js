var url = document.URL
console.log(url)
console.log(url.split('/'))
var game = url.split('/')[4];
let updated = false;
console.log(game);
$(document).ready(function(){
    if (game == 'map')
    {
        $("#background_img").attr("src", "/static/4GAME_ALL/MAP/1x/MAP_BG.png");
    }
    else if(game == 'catch_egg')
    {
        $("#background_img").attr("src", "/static/4GAME_ALL/ANIMAL_CATCH/1x/ANIMAL_CATCH_BG.png");
    }
    else if(game == 'fruit_cutter')
    {
        $("#background_img").attr("src", "/static/4GAME_ALL/CUT_FRUIT/1x/CUT_ FRUIT_BG.png");
    }
    else if(game == 'flipping_card')
    {
        $("#background_img").attr("src", "/static/4GAME_ALL/CARD_GAME4X4/1x/CARD_GAME_BG.png");
    }
});

function play_subject_audio(elem)
{
    var subject = elem.id;
    var cur_wav = subject.split("<br>")[0];
    var audio_url = "/static/audio/" + cur_wav + ".wav";
    var audio = new Audio(audio_url).play();
}

function unshow_dialog() {
    $("#upgrade_dialog").remove();
    $("#upgrade_text").remove();
    $("#upgrade_continue_btn").remove();
    $("#wear_btn").remove();
    $("#not_wear_btn").remove();
    $("#gray_layer").css({"z-index":300});
}

function show_dialog(info_dict, mode)
{

    if (mode == 'upgrade')
    {
        var level = info_dict["level"]
        var img_id_str = ""
        var over_score = level * 1000
        var now_wear = info_dict['wear_now']
        console.log(now_wear)
        img_id_str = '0' + level.toString();

        // var img_id = 0
        // if (level < 6)
        // {
        //     img_id = level + now_wear
            
        // }
        // else{
        //     img_id = level + 7 + now_wear
        // }

        // if (img_id < 10)
        // {
        //     img_id_str = '0' + img_id.toString();
        // }
        // else{
        //     img_id_str = img_id.toString()
        // }
        img_url = "/static/4GAME_ALL/ALL/1x/ALL_UPGRADE_" + img_id_str +".png"
        btn_img_url = "/static/4GAME_ALL/ALL/1x/ALL_CONFIRM_C.png"
        console.log(img_url)
        // $('#_parent')[0].innerHTML += "<div id = 'gray_all'></div>";
        $("#gray_layer").css({"z-index":998});

        $('#_parent')[0].innerHTML += "<img id = 'upgrade_dialog' class = 'upgrade_dialog' src='" + img_url + "'></img>";
        $('#_parent')[0].innerHTML += "<div id = 'upgrade_text'>" + over_score.toString()+"積分，成就達成！<br>您的鴿寶已升級至LV." + level.toString()+"</p>";
        $('#_parent')[0].innerHTML += "<img id = 'upgrade_continue_btn' onclick = 'unshow_dialog()' src='" + btn_img_url + "'></img>";
    }
    else if(mode == 'equip')
    {

        var gain_weapon_id = info_dict.weapon
        var weapon_id_str = '0' + gain_weapon_id
        
        img_url = "/static/4GAME_ALL/ALL/1x/ALL_EQUIPMENT_" + weapon_id_str +".png"
        check_img_url = "/static/4GAME_ALL/ALL/1x/ALL_EQUIPMENT.png"
        btn_wear_url = "/static/4GAME_ALL/ALL/1x/ALL_YES.png"
        btn_not_wear_url = "/static/4GAME_ALL/ALL/1x/ALL_NO.png"
        // $('#game_background')[0].innerHTML += "<img id = 'gray_layer' src ='/static/4GAME_ALL/ALL/1x/ALL_GRAY_LAYER.png'>";
        $("#gray_layer").css({"z-index":998});
        $('#_parent')[0].innerHTML += "<img id = 'upgrade_dialog' class = 'upgrade_dialog' src='" + img_url + "'></img>";
        // $('#game_background')[0].innerHTML += "<div id = 'upgrade_text'>" + over_score.toString()+"積分，成就達成！<br>您的鴿寶已升級至LV." + level.toString()+"</p>";
        $('#_parent')[0].innerHTML += "<img id = 'wear_btn' onclick = 'wearing(this.id, "+ gain_weapon_id +")' src='" + btn_wear_url + "'></img>";
        $('#_parent')[0].innerHTML += "<img id = 'not_wear_btn' onclick = 'unshow_dialog()' src='" + btn_not_wear_url + "'></img>";

    }
}

function wearing(btn_id, equip_id){
    console.log("---------------------------"  + equip_id.toString())
    // var btn_name = elem.
    if (btn_id == 'wear_btn')
    {
        var form_data = new FormData();
        form_data.append('equip_id', equip_id);
        // window.open("/score_upload", "_self");
        $.ajax({
            type: "POST",
            url: $SCRIPT_ROOT + "/wearing",
            data: form_data,
            success: (data) => {
                console.log(data.status);
                if (data.status==true)
                {
                    // alert("裝備更新成功!")
                    // window.open("/stu/game", "_self");
                    unshow_dialog();
                } 
            },
            contentType: false,
            processData: false,
            dataType: "json"
        });
        }
    else{
        // window.open("/stu/game", "_self");
        unshow_dialog();
    }

}

function backto_gameselec_page(){
    window.open("/stu/game", "_self");
}
function upload_score(){
    if (!updated) {
        updated = true;
        $("#btn_register_score").css({filter: "grayscale(1)"});
        var form_data = new FormData();
        form_data.append('score', $("#score")[0].innerHTML);
        // window.open("/score_upload", "_self");
        $.ajax({
            type: "POST",
            url: $SCRIPT_ROOT + "/score_upload",
            data: form_data,
            success: (data) => {
                console.log(data.status);
                
                if (data.upgrade == true)
                {
                    img_url = ""
                    // info_dict = {'level':data.level, 'wear':0}
                    show_dialog(data, 'upgrade')
                    // if data.level = 1
                    // msg = "您升級了! 升到了" + data.level + "級";
                    // alert(msg)
                    // window.open("/stu/game", "_self");
                }
                else if (data.weapon_gain == true)
                {
                    show_dialog(data, 'equip')
                }
                else
                {
                    // msg = "您尚未升級!您目前" + data.level + "級";
                    // alert(msg)
                    var SetSuccessModal = new bootstrap.Modal($('#SetSuccessModal'));
                    if (! $('#SetSuccessModal').hasClass('show')) SetSuccessModal.show();
                }
            },
            contentType: false,
            processData: false,
            dataType: "json"
        });
    }
}

function play_again(){
    url = document.URL
    course_id = url.split('?')[1]
    url_split = url.split('/')
    game_name = url_split[4]
    console.log(game_name)
    base_url = url_split[2] + '/' + url_split[3]
    to_url = `../${game_name}_tutorial?${course_id}`
    console.log(to_url)
    window.open(to_url, "_self");
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