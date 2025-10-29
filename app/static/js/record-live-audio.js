// This example uses MediaRecorder to record from a live audio stream,
// and uses the resulting blob as a source for an audio element.
//
// The relevant functions in use are:
//
// navigator.mediaDevices.getUserMedia -> to get audio stream from microphone
// MediaRecorder (constructor) -> create MediaRecorder instance for a stream
// MediaRecorder.ondataavailable -> event to listen to when the recording is ready
// MediaRecorder.start -> start recording
// MediaRecorder.stop -> stop recording (this will generate a blob of data)
// URL.createObjectURL -> to create a URL from a blob, which we can use as audio src

let recordButton, stopButton, recorder;
let model;
let record_flag = false;

function getModelName() {

    const modelList = document.getElementById('model_name');
    model = modelList.options[modelList.selectedIndex].text;
    console.log(model);
}

function fruity_record_init() {

    recordButton = document.getElementById('record_btn');
    // stopButton = document.getElementById('stop');
    // get audio stream from user's mic
    navigator.mediaDevices.getUserMedia({
        audio: true, video: false
    })
        .then(function (stream) {
            recordButton.disabled = false;
            recordButton.addEventListener('click', fruity_record_process);
            // recordButton.addEventListener('mouseup', stopRecording);
            // recorder = new MediaRecorder(stream, {mimeType: 'video/webm;codecs=vp9'});
            recorder = new MediaRecorder(stream, {mimeType: 'audio/webm;codecs=opus'});
            // recorder = new MediaRecorder(stream);
            //console.dir(recorder.mimeType);
            // listen to dataavailable, which gets triggered whenever we have
            // an audio blob available
            recorder.addEventListener('dataavailable', onRecordingReady);
        });
}
function fruity_record_process() {
    if (!record_flag) {
        console.log("start");
        recorder.start();
        record_flag = true;

        setTimeout(() => {
            console.log("stop");
            recorder.stop();
            record_flag = false;
        }, 3000);
    }
}

function map_record_init() {

    recordButton = document.getElementById('record_btn');
    // stopButton = document.getElementById('stop');
    // get audio stream from user's mic
    navigator.mediaDevices.getUserMedia({
        audio: true, video: false
    })
        .then(function (stream) {
            recordButton.disabled = false;
            recordButton.addEventListener('mousedown', map_record_process_start);
            recordButton.addEventListener('mouseup', map_record_process_end);
            // recordButton.addEventListener('mouseup', stopRecording);
            // recorder = new MediaRecorder(stream, {mimeType: 'video/webm;codecs=vp9'});
            recorder = new MediaRecorder(stream, {mimeType: 'audio/webm;codecs=opus'});
            // recorder = new MediaRecorder(stream);
            //console.dir(recorder.mimeType);
            // listen to dataavailable, which gets triggered whenever we have
            // an audio blob available
            recorder.addEventListener('dataavailable', onRecordingReady);
        });
}
function map_record_process_start() {
    if (!record_flag) {
        console.log("start");
        recorder.start();
        record_flag = true;
        $("#record_btn").attr("src", "/static/4GAME_ALL/MAP/1x/ALL_MIC_RED.png");
    }
}
function map_record_process_end() {
    if (record_flag) {
        console.log("stop");
        recorder.stop();
        record_flag = false;
        $("#record_btn").attr("src", "/static/4GAME_ALL/MAP/1x/ALL_MIC.png");
    }
}

function onRecordingReady(e) {
    // const audio = document.getElementById('audio');
    // e.data contains a blob representing the recording
    // audio.src = URL.createObjectURL(e.data);
    //audio.play();
    console.log(e.data);
    upload(e.data);
}

function upload(blob) {
    // getModelName();
    let form_data = new FormData();
    form_data.append("data", blob);
    console.log("POST")
    $.ajax({
        type: "POST",
        url: "/save_audio",
        data: form_data,
        processData:false,
        contentType:false
    }).then(function(response){
        console.log("Success Save");
        audio_predict()
    }, function(){
        console.error("Fail Save");
    });

}

// function audio_predict(){
//     $.ajax({
//         type: "GET",
//         url: "/predict",
//         // data: JSON.stringify(model),
//         contentType: "application/json",
//         dataType: 'json'
//     }).then(function(response){
//         console.log("Success Predict");
//         console.log(response.recognition);
//         console.log("Predict response:", response);
//         verify_answer(response.recognition)
//         // document.getElementById("recognition_result").innerHTML = "Recognition Result ->\n" + response.recognition;
//         // document.getElementById("lattice_text").innerHTML = "Lattice Scoring -> " + response.text;
//         // document.getElementById("lattice_phoneme").innerHTML = "Lattice Scoring -> " + response.phoneme;
//         // document.getElementById("correction_result").innerHTML = "Correction Result -> " + response.correction;
//     }, function(){
//         console.error("Fail Predict");
//     });
// }
function audio_predict(){
    $.ajax({
        type: "GET",
        url: "/predict",
        contentType: "application/json",
        dataType: 'json'
    }).then(function(response){
        console.log("Success Predict");
        console.log(response.recognition);
        console.log("Predict response:", response);
        if (response.recognition) {
            let ans = Array.isArray(response.recognition) ? response.recognition : [response.recognition];
            verify_answer(ans);
        } else {
            alert("無法辨識語音，請再試一次！");
        }
    }, function(){
        console.error("Fail Predict");
        alert("語音辨識 API 發生錯誤！");
    });
}
