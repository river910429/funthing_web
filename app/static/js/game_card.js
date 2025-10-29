const cards = document.querySelectorAll('.card');

let startFlag = false;
let cardhidden = false;
let count_downIntervalId;
let count_down_num = 10;

let hasFlipped = false;
let lock = false;
let firstCard, secondCard, current_ans, question_set;
let answers_sheet = [];
let answers_status = [];

function game_start(course_id){
    window.open(`/game/flipping_card?course_id=${course_id}`, "_self");
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
        cards.forEach(card => card.addEventListener('click', flipCard));
        shuffle();
        count_downIntervalId = setInterval(count_down, 1000);
        show_all();
        setTimeout(hide_all, 10000)
    }
    startFlag = true;
});

function count_down() {
    console.log(count_down_num);
    count_down_num -= 1;
    if (count_down_num < 0){
        clearInterval(count_downIntervalId);
        $('#count_down').remove();
    }
    else {
        $('#count_down').attr("src", `/static/4GAME_ALL/CARD_GAME4X4/1x/CARD_GAME_${count_down_num}.png`);
    }
}

function show_all() {
    cards.forEach(card => {
        card.classList.add('flip');
        question = card.querySelector('.question');
        question.hidden = false;
        question.innerHTML = card.dataset.txt;
    });
}

function hide_all() {
    cardhidden = true;
    cards.forEach(card => {
        card.classList.remove('flip');
        question = card.querySelector('.question');
        question.hidden = true;
    });
    listen_again();
}

function subject_addup(){
    let count = 8 - question_set.length - 1;
    $('#subject_adder')[0].innerHTML = count.toString() + "/8";
}

function listen_again() {
    if (cardhidden) {
        var cur_wav = current_ans.split("<br>")[0];
        var audio_url = "/static/audio/" + cur_wav + ".wav";
        var audio = new Audio(audio_url).play();
    }
}

function flipCard() {
    if (lock) return;
    if (this === firstCard) return;

    this.classList.add('flip');
    
    if (!hasFlipped) {
        // first click
        hasFlipped = true;
        firstCard = this;
        firstText = this.querySelector('.question');
        firstText.hidden = false;
        firstText.innerHTML = firstCard.dataset.txt;
        return;
    }
    // second click
    hasFlipped = false;
    secondCard = this;
    secondText = this.querySelector('.question');
    secondText.hidden = false;
    secondText.innerHTML = secondCard.dataset.txt;
    
    checkMatch();
}

function checkMatch() {
    let isMatch = (firstCard.dataset.txt === secondCard.dataset.txt) && (secondCard.dataset.txt === current_ans);
    
    isMatch ? disableCards() : unflipCards();
}

function disableCards() {
    firstCard.removeEventListener('click', flipCard);
    secondCard.removeEventListener('click', flipCard);
    if (question_set.length === 0) {
        console.log("GAME OVER! WELL DONE!");
        answers_status.push(true);
        setTimeout(end_game, 1000);
    }
    else {
        answers_status.push(true);
        shuffling_arr(question_set);
        current_ans = question_set.pop();
        answers_sheet.push(current_ans);
        console.log(current_ans);
        listen_again();
        subject_addup();
    }
}

function unflipCards() {
    lock = true;
    setTimeout(() => {
        firstCard.classList.remove('flip');
        secondCard.classList.remove('flip');
        firstText.hidden = true;
        secondText.hidden = true;

        resetGame();
        lock = false;
    }, 500)
}

function resetGame() {
    [hasFlipped, lock] = [false, false];
    [firstCard, secondCard] = [null, null];
    [firstText, secondText] = [null, null];
}

function shuffle() {
    question_set = subjects_CH
    time_progress();
    var arr = question_set.concat(question_set);
    shuffling_arr(question_set);
    current_ans = question_set.pop();
    answers_sheet.push(current_ans);
    console.log(question_set);
    console.log(current_ans);
    cards.forEach(card => {
        let randomPos = Math.floor(Math.random() * 16);
        card.style.order = randomPos;
        tmp_txt = arr.pop();
        card.setAttribute('data-txt', tmp_txt);
    });
}

function shuffling_arr(array) {
    array.sort(() => Math.random() - 0.5);
}

var org_setting = $('#game_time_bar').css('transition');
function time_progress() {
    $('#game_time_bar').css('transition', org_setting);
    $('#game_time_bar').delay(500).queue(function () {
        $(this).css('width', '36.8%')
    });
}

function time_out() {
    console.log('Timeout!');
    end_game();
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
    game_close(`/game/flipping_card/game_result?${course_id}`, result_sheet);
}

var duration = document.getElementById("game_time_bar");
duration.addEventListener("transitionend", time_out, false);

// cards.forEach(card => card.addEventListener('click', flipCard));