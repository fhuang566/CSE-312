const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
const courseId = urlParams.get('courseId');
var socket;


document.addEventListener('DOMContentLoaded', () => {
    // create websocket connection
    socket = io.connect({query:{"token": document.getElementById("xsrf_token").value}});

    // //upon connecting, join room, room name = courseid
    socket.on('connect', function() {
        socket.emit('join', {'xsrf_token':document.getElementById("xsrf_token").value, 'courseId': courseId});
    });

    socket.on('message', data => {
        console.log(`Message received: ${data}`);
        if(data["type"] == "st"){
            setST(data['id'], data['st']);
        }
        else if(data['type'] == 'score') {
            setScore(data);
        }
        else if(data['type'] == 'stAll') {
            for(let i = 0; i < data['id'].length; i++){
                setST(data['id'][i], data['st']);
            }
        }
        else{
            addQuestion(data);
        }
        
        
    });

    const forms = document.querySelectorAll('form');
    //catch form submition, extract form entries into json object
    forms.forEach(function (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const data = new FormData(form);
            const JSONdata = Object.fromEntries(data.entries());
            if (JSONdata["type"] == "question-create"){
                JSONdata["correct-answer"] = data.getAll("correct-answer");
            }
            else{
                JSONdata["ans"] = data.getAll("ans");
            }

            JSONdata["courseId"] = courseId;
            JSONdata["xsrf_token"] = document.getElementById('xsrf_token').value;
            console.log(JSONdata);
            socket.emit('message', JSON.stringify(JSONdata));
            form.reset();
        });
    });

})

// document.addEventListener("MutationObserver", () => {
//     console.log("mutation detected");
//     const forms = document.querySelectorAll('form');
//     //catch form submition, extract form entries into json object
//     forms.forEach(function (form) {
//         form.addEventListener('submit', (e) => {
//             e.preventDefault();
//             const data = new FormData(form);
//             const JSONdata = Object.fromEntries(data.entries());
//             if (JSONdata["type"] == "question-create"){
//                 JSONdata["correct-answer"] = data.getAll("correct-answer");
//             }
//             else{
//                 JSONdata["ans"] = data.getAll("ans");
//             }

//             JSONdata["courseId"] = courseId;
//             console.log(JSONdata);
//             socket.emit('message', JSON.stringify(JSONdata));
//             form.reset();
//         });
//     });
// })


function addQuestion(data) {
    const choices = ['a', 'b', 'c', 'd', 'e'];
    var optionType = 'checkbox';
    var instructor = false;
    var isDisabled = true;
    // let br = document.createElement("span");
    // br.innerHTML = "<br>";
    if (data['active'] == 'Started'){
        isDisabled = false;
    }
    if (data['correct-answer'] != undefined){
        instructor = true;
    }
    if (data["mutiple-ans"] == "False"){
        optionType = 'radio';
    }
    let newQuestion = document.createElement('form');
    newQuestion.setAttribute('id', 'form-' + data["questionId"]);
    newQuestion.addEventListener('submit', (e) => {
        e.preventDefault();
        const data = new FormData(newQuestion);
        const JSONdata = Object.fromEntries(data.entries());
        if (JSONdata["type"] == "question-submit"){
            JSONdata["ans"] = data.getAll("ans");
        }

        JSONdata["courseId"] = courseId;
        JSONdata["xsrf_token"] = document.getElementById('xsrf_token').value;
        console.log(JSONdata);
        socket.emit('message', JSON.stringify(JSONdata));
    });
    let field = document.createElement('fieldset');
    field.setAttribute('id', 'field-' + data["questionId"]);
    let type = document.createElement("input");
    type.setAttribute('type', 'hidden');
    type.setAttribute('name', 'type');
    type.setAttribute('value', 'question-submit')
    let id = document.createElement('input');
    id.setAttribute("type", 'hidden');
    id.setAttribute('name', 'id');
    id.value = data['questionId'];
    let question = document.createElement('b');
    question.setAttribute('type', "text");
    question.innerHTML = data["question"] + '<br>';
    field.appendChild(type);
    field.appendChild(id);
    field.appendChild(question);

    for (let i = 0; i<choices.length; i++){
        let option = document.createElement('input');
        option.setAttribute('type', optionType);
        option.setAttribute('name', 'ans');
        option.setAttribute('value', choices[i]);
        option.setAttribute('id', choices[i] + '-' + data['questionId'])
        let ans_string = choices[i] + ": " + data['choice-'+choices[i]];
        if (instructor){
            if (data['correct-answer'].includes(choices[i])){
                option.checked = true;
            }
            
        }
        let label = document.createElement('label');
        label.setAttribute('for', choices[i] + '-' + data['questionId']);
        label.innerHTML = ans_string + "<br>";
        field.appendChild(option);
        field.appendChild(label);
        

    }
    if(!instructor){
        let submitButton = document.createElement('button');
        submitButton.setAttribute('type', 'submit');
        submitButton.innerHTML = 'Submit';
        let score = document.createElement('i');
        score.innerHTML = 'Score : 0/1 <br>';
        field.disabled = isDisabled;
        field.appendChild(score);
        field.appendChild(submitButton);
        newQuestion.appendChild(field);
        document.getElementById('myQuestions').appendChild(newQuestion);
    }
    else{
        let state = document.createElement('b');
        state.setAttribute("id", 'state-' +  data['questionId']);
        state.innerHTML = data['active'] + '<br>';
        field.disabled = true;
        field.appendChild(state);
        let startButton = document.createElement('button');
        startButton.setAttribute('onclick', 'st("Started", \'' + data["questionId"] + '\')');
        startButton.innerHTML = "Start";
        let stopButton = document.createElement('button');
        stopButton.setAttribute('onclick', 'st("Stopped", \'' + data["questionId"] + '\')');
        stopButton.innerHTML = "Stop";
        newQuestion.appendChild(field);
        document.getElementById('myQuestions').appendChild(newQuestion);
        document.getElementById('myQuestions').appendChild(startButton);
        document.getElementById('myQuestions').appendChild(stopButton);
    }
    

    


    // var template = "<fieldset id=" + data["questionId"] + " disabled><div>" + "<input id='type' name='type' value='question-submit' hidden><br><b type='text' id='question' name='questions'>"+ data["question"] +
    // "</b><br><input id='a' name=" + data["questionId"] + " type='checkbox' value='a'>a: "+ data["choice-a"] + 
    // "</input><br><input id='b' name=" + data["questionId"] + " type='checkbox' value='b'>b: "+ data["choice-b"] + 
    // "</input><br><input id='c' name=" + data["questionId"] + " type='checkbox' value='c'>c: "+ data["choice-c"] + 
    // "</input><br><input id='d' name=" + data["questionId"] + " type='checkbox' value='d'>d: "+ data["choice-d"] +
    // "</input><br><input id='e' name=" + data["questionId"] + " type='checkbox' value='e'>e: "+ data["choice-b"];
    

    
    // if (data["mutiple-ans"] == "False"){
    //     template = template.replaceAll("checkbox", "radio");
    // }

    // if (data['correct-answer'] != undefined){
    //     for(let i = 0; i < data['correct-answer'].length; i++){
    //         x = data['correct-answer'][i];
    //         template = template.replace("value=\'" + x + "\'", "value=\'" + x + "\' checked");

    //     }
    //     template += '</input></fieldset><div><button onclick="st(\'start\', \'' + data["questionId"] + '\')">Start</button><button onclick="st(\'stop\', \'' + data["questionId"] + '\')">Stop</button></div><div id=' + data["questionId"] + "state" + '>' + data['active'] + '</div>';
    // }
    // else{
    //     template += "</input></div><div><button type='submit'>Submit</button></div></fieldset>";
    // }
    // document.getElementById('myQuestions').innerHTML += template;

}

function st(e, id) {
    ret = {"type": "st", "courseId": courseId, "st": e, "id": id, "xsrf_token": document.getElementById('xsrf_token').value};
    socket.emit('message', JSON.stringify(ret));
}

function setST(id, st) {
    let doc = document.getElementById('myQuestions').querySelector('#form-'+ id).querySelector('fieldset');
    let state =  doc.querySelector("#state-" + id);
    let disable = true;
    if (st == 'Started'){
        disable = false;
    }
    if(st == 'Stopped'){
        ret = {'type': 'score', 'courseId': courseId, 'id': id, 'xsrf_token':document.getElementById('xsrf_token').value};
        socket.emit('message', JSON.stringify(ret));
    }
    if (state == null) {
        
        doc.disabled = disable;

    }
    else{
        state.innerHTML = st;
    }

    
    
}

function setScore(data) {
    let doc = document.getElementById('myQuestions').querySelector('#form-'+ data['id']).querySelector('fieldset').querySelector('i');
    if (doc != null){
        doc.innerHTML = 'Score: ' + data['grade'] + '/1<br>';
    }
}

function stAll(option){
    data = {'type': 'stAll', 'courseId': courseId, 'st': option, 'xsrf_token':document.getElementById('xsrf_token').value};
    socket.emit('message', JSON.stringify(data));
}


// function mySubmit(event) {
//     event.preventDefault();
//     const data = new FormData(form);
//     const JSONdata = Object.fromEntries(data.entries());
//     if (JSONdata["type"] == "question-create"){
//         JSONdata["correct-answer"] = data.getAll("correct-answer");
//     }
//     else{
//         JSONdata["ans"] = data.getAll("ans");
//     }

//     JSONdata["courseId"] = courseId;
//     console.log(JSONdata);
//     socket.emit('message', JSON.stringify(JSONdata));
//     form.reset();
// }

function loadQuestions(){
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            const questions = JSON.parse(this.response);
            for (const question of questions) {
                addQuestion(question);
            }
        }
    };
    request.open("GET", "/myQuestions?courseId=" + courseId);
    request.send();

}

function loadCourse(){
    loadQuestions();
}